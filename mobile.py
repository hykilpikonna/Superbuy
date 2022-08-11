import json
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from urllib.parse import urlparse, parse_qs

import requests
from fastapi import Body, FastAPI
from hypy_utils import json_stringify
from hypy_utils.serializer import pickle_decode, pickle_encode
from starlette.middleware.cors import CORSMiddleware

from dotdotbuy_auth import sign_params, sign_api
from popos.popos import *
from popos.gateway_order import *

r = requests.Session()
r.encoding = 'utf-8'
r.headers.update({
    'User-Agent': 'Superbuy/5530001 CFNetwork/1220.1 Darwin/20.3.0',
    'app-key': 'aaa',
})


CONFIG_PATH = Path('.config/superbuy')


def user_id() -> str:
    return r.headers['userId']


def login(user: str, passwd: str) -> LoginData:
    # Desktop:
    resp: SuperbuyResponse = js(r.post('https://login.superbuy.com/api/site/login', data={'login_name': user, 'password': passwd}))
    assert resp.state == 0, resp

    # Mobile:
    resp: SuperbuyResponse = js(r.post('https://api.superbuy.com/auth/login', data={'loginToken': user, 'password': passwd}))
    assert resp.state == 0, resp
    data: LoginData = resp.data

    # Add mobile access token
    r.headers.update({'accessToken': data.accessToken})
    r.headers.update({'userId': str(data.userId)})

    print(f'Successfully logged in as {user}')
    return data


def login_cached(user: str, passwd: str):
    global r
    p = CONFIG_PATH / f'ss_{user.replace("@", "_").replace(".", "_")}.pickle'
    if p.is_file():
        print(f'Using cached login session for {user}')
        r = pickle_decode(p.read_bytes())
        return
    login(user, passwd)
    CONFIG_PATH.mkdir(exist_ok=True, parents=True)
    p.write_bytes(pickle_encode(r))


def app_order_list():
    # endpoint = 'https://front.superbuy.com/package/parcel/expert-send-list'
    endpoint = 'https://front.superbuy.com/package/parcel/app-list'
    req = r.get(endpoint, params=dict(pageSize=100, currPage=1, includeOverdueItemFlg=1), headers=sign_params(dict(r.headers)))
    resp: SuperbuyResponse = js(req)
    return resp


def gateway_order_list(limit: int = 200, type: Literal['storage', 'payment', 'all', 'receive'] = 'all', orderType: int = 0) -> list[GatewayOrder]:
    """
    Get a list of orders that are already added to the account.
    """
    endpoint = f'https://api.superbuy.com/gateway/orderpkg/list/{user_id()}/1/{limit}'
    print(endpoint)
    print(sign_api(dict(r.headers)))
    req = r.get(endpoint, params=dict(type=type, orderType=orderType), headers=sign_api(dict(r.headers)))
    resp: PaginatedResponse = js(req)
    assert resp.Code == 10000, resp
    return resp.List


def get_url_param(url: str, param: str) -> str:
    return parse_qs(urlparse(url).query)[param][0]


def crawl(item_url: str) -> dict:
    id = get_url_param(item_url, 'id')
    out_path = Path(f'crawler/{id}.json')

    if not out_path.is_file():
        print(f'Crawling {id}...')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(r.post('https://front.superbuy.com/crawler/', data={"needSoldOutSkuInfo": 1, "location": 2, "goodUrl": item_url}).text)

    return json.loads(out_path.read_text())


def create_diy_order(create: list[TaobaoOrder]):
    """
    创建一个转运订单

    :param create: List of taobao urls and details
    """
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

        print(f'Orders {c.id} created, sending...')
        j = json_stringify({'diy': out, 'transport': {'list': []}})
        Path(f'crawler/order_{c.id}_created.json').write_text(j, 'utf-8')
        resp = r.post('https://front.superbuy.com/order/transport/create-diy-order', data=j.encode('utf-8'),
                      headers={'content-type': 'application/json; charset=UTF-8'}).json()
        print(resp)
        time.sleep(10)


def load_taobao(p: str = 'bought_items.json') -> list[TaobaoOrder]:
    p = Path(p)
    return js(p.read_text())


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)


@app.post('/taobao/fill_items')
def taobao_fill_items(body: Any = Body):
    taobao_data: list[TaobaoOrder] = js(body)
    orders = gateway_order_list()
    ids = [get_url_param(i.GoodsLink, 'id') for o in orders for i in o.Items if 'id=' in i.GoodsLink]
    create_diy_order([o for o in taobao_data if o.date >= '2022-08-10' and not any(get_url_param(i.url, 'id') in ids for i in o.items)])


@app.post('/taobao/fill_delivery')
def taobao_fill_delivery(body: Any = Body):
    taobao_data: list[TaobaoOrder] = js(body)
    print(taobao_data)
    pass


if __name__ == '__main__':
    # print(r.get(f'https://api.superbuy.com/gateway/oauth2/personalcenter/{USERID}').json())
