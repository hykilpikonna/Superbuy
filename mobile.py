import argparse
import os
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse, parse_qs

import requests
import toml
from hypy_utils import json_stringify
from hypy_utils.serializer import pickle_decode, pickle_encode
from hypy_utils.logging_utils import setup_logger

from dotdotbuy_auth import sign_params, sign_api
from popos.gateway_order import *
from popos.popos import *

r = requests.Session()
r.encoding = 'utf-8'
r.headers.update({
    'User-Agent': 'Superbuy/5530001 CFNetwork/1220.1 Darwin/20.3.0',
    'app-key': 'aaa',
})

MIN_DATE = '2023-09-03'
CONFIG_PATH = Path('.config/superbuy')
PORT = 12943

log = setup_logger()


def user_id() -> str:
    return r.headers['userId']


def login(user: str, passwd: str) -> LoginData:
    # Desktop:
    # resp: SuperbuyResponse = jsn(r.post('https://login.superbuy.com/api/site/login', data={'login_name': user, 'password': passwd}))
    # assert resp.state == 0, resp

    # Mobile:
    resp: SuperbuyResponse = jsn(r.post('https://api.superbuy.com/auth/login', data={'loginToken': user, 'password': passwd}))
    assert resp.state == 0, resp
    data: LoginData = resp.data

    # Add mobile access token
    r.headers.update({'accessToken': data.accessToken})
    r.headers.update({'userId': str(data.userId)})

    log.info(f'Successfully logged in as {user}')
    return data


def login_cached(user: str, passwd: str):
    global r
    p = CONFIG_PATH / f'ss_{user.replace("@", "_").replace(".", "_")}.pickle'
    if p.is_file():
        log.info(f'Using cached login session for {user}')
        r = pickle_decode(p.read_bytes())
        return
    login(user, passwd)
    CONFIG_PATH.mkdir(exist_ok=True, parents=True)
    p.write_bytes(pickle_encode(r))


def app_order_list():
    # Mobile
    endpoint = 'https://front.superbuy.com/package/parcel/app-list'
    req = r.get(endpoint, params=dict(pageSize=100, currPage=1, includeOverdueItemFlg=1), headers=sign_params(dict(r.headers)))
    resp: SuperbuyResponse = jsn(req)
    return resp


def gateway_order_list(limit: int = 200, type: Literal['storage', 'payment', 'all', 'receive'] = 'all', orderType: int = 0) -> list[GatewayOrder]:
    """
    Get a list of orders that are already added to the account.
    """
    # Mobile
    endpoint = f'https://api.superbuy.com/gateway/orderpkg/list/{user_id()}/1/{limit}'
    log.debug(endpoint)
    log.debug(sign_api(dict(r.headers)))
    req = r.get(endpoint, params=dict(type=type, orderType=orderType), headers=sign_api(dict(r.headers)))
    resp: PaginatedResponse = jsn(req)
    assert resp.Code == 10000, resp
    return resp.List


def get_url_param(url: str, param: str) -> str:
    return parse_qs(urlparse(url).query)[param][0]


def crawl(item_url: str) -> dict:
    id = get_url_param(item_url, 'id')
    out_path = Path(f'crawler/{id}.json')
    log.info(f'Crawling {id}...')

    if out_path.is_file():
        return json.loads(out_path.read_text())

    while True:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        resp = r.post('https://front.superbuy.com/crawler/', data={"needSoldOutSkuInfo": 1, "location": 2, "goodUrl": item_url})
        if resp.status_code != 200:
            log.error(f"Request failed: {resp.status_code}")
            assert input("Retry? [y/N]").lower() == 'y'
            continue
        out_path.write_text(resp.text)
        return resp.json()


def create_diy_order(create: list[TaobaoOrder]):
    """
    创建一个转运订单

    :param create: List of taobao urls and details
    """
    orders = gateway_order_list()
    ids = [get_url_param(i.GoodsLink, 'id') for o in orders for i in o.Items if 'id=' in i.GoodsLink]
    create = [o for o in create if o.date >= MIN_DATE and not any(get_url_param(i.url, 'id') in ids for i in o.items)]
    for c in create:
        shop_name = c.store.name
        shop_id = crawl(c.items[0].url)['data']['shop']['shopId']

        goods = []
        for i in c.items:
            id = get_url_param(i.url, 'id')
            cr = crawl(i.url)

            goods.append(CreateGood(
                desc=''.join(f'{k}：{v}，'for k, v in i.sel) if 'sel' in i.__dict__ else i.name,
                goodsId=id, inventory=0, name=i.name, num=int(i.qty),
                shopName=shop_name, shopUrl='https:' + c.store.url, skus='0',
                totalPrice=float(i.price.split('￥')[-1]), url=i.url))

        out = [CreateOrder('', shop_id, shop_name, goods)]

        log.info(f'Orders {c.id} created, sending...')
        j = json_stringify({'diy': out, 'transport': {'list': []}})
        Path(f'crawler/order_{c.id}_created.json').write_text(j, 'utf-8')
        resp = r.post('https://front.superbuy.com/order/transport/create-diy-order', data=j.encode('utf-8'),
                      headers={'content-type': 'application/json; charset=UTF-8'}).json()
        log.debug(resp)


def fill_express_no(taobao_data: list[TaobaoOrder]):
    log.info("Filling express numbers")
    orders = gateway_order_list(orderType=4)
    for o in orders:
        for i in o.Items:
            # 审核通过 means the delivery number hasn't been inputted yet
            if i.StatusName != '审核通过':
                log.debug(f"Item {i.ItemId} has status {i.StatusName}, skipped.")
                continue

            # Find item in taobao
            tb = next(to for to in taobao_data for ti in to.items if get_url_param(ti.url, 'id') == i.goodsCode)

            # Check delivery status
            if tb.status not in {'卖家已发货', '快件已签收', '快件已揽收', '物流运输中'}:
                log.debug(f"Item {i.ItemId} has status code {tb.status}, skipped.")
                continue

            # Check if delivery id exists
            if not tb.delivery.expressId:
                log.debug(f"Item {i.ItemId} has no delivery id, skipped.")
                continue

            # Find delivery company's id
            data = {'itemId': i.ItemId,
                    'warehouseId': i.WarehouseId,
                    'deliveryCompany': str(find_delivery_id(tb.delivery.expressName)),
                    'deliveryno': tb.delivery.expressId,
                    'platform': '3', 'itemStatus': '0', 'desc': ' '}

            # Send request
            log.info(f'Filling express no for {i.GoodsName}')
            # Mobile endpoint
            resp = r.post(f'https://api.superbuy.com/gateway/transport/fillExpressno/{user_id()}', json=data,
                          headers=sign_api(dict(r.headers)))
            assert resp.json()['Code'] == 10000, resp.text + "\n" + str(data)
            log.debug(resp.json())


def load_taobao(p: str = 'bought_items.json') -> list[TaobaoOrder]:
    p = Path(p)
    return jsn(p.read_text())


delivery_companies: list[SuperbuyDeliveryCompany] = jsn(Path('data/delivery.json').read_text('utf-8'))
delivery_name_map = {d.name: d for d in delivery_companies}
delivery_name_map.update({d.name.replace("快递", "物流"): d for d in delivery_companies})
delivery_name_map.update({d.name.replace("物流", "快递"): d for d in delivery_companies})


def find_delivery_id(name: str) -> int:
    return delivery_name_map[name].id if name in delivery_name_map else -1


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write("Up".encode())

        log.info("Taobao data received!")
        body = self.rfile.read(int(self.headers.get('content-length', 0))).decode()

        if self.path.lower() == '/taobao':
            taobao_data: list[TaobaoOrder] = jsn(body)
            log.debug(taobao_data)
            create_diy_order(taobao_data)
            fill_express_no(taobao_data)

            # Stop process
            sys.exit(0)

        # For desktop logins after captcha is added (not actually used)
        if self.path.lower() == '/login':
            # await fetch("http://127.0.0.1:12842/login", {method: "POST", body: document.cookie})
            cookies = [[urllib.parse.unquote(k) for k in c.strip().split("=", 1)] for c in body.split(";")]
            # noinspection PyTypeChecker
            r.cookies.update(dict(cookies))
            log.debug(app_order_list())

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()


if __name__ == '__main__':
    par = argparse.ArgumentParser("Superbuy Order Helper")
    par.add_argument("-a", "--auth", help="Auth config path", default="auth.toml")
    args = par.parse_args()

    auth = toml.loads(Path(args.auth).read_text())

    log.info(login(auth['login'], auth['passwd']))

    # Start HTTP server asyncronously
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    # Open browser
    webbrowser.open_new_tab(f"https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?script={PORT}")

