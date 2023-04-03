from __future__ import annotations

import datetime
import json
from pathlib import Path

import requests


ses = requests.Session()
ses.headers = {'accept-language': 'zh-CN'}


out_path = Path('index-data')
out_path.mkdir(exist_ok=True)


def write_entry(data):
    id = data['guid']
    time = datetime.datetime.fromtimestamp(data['delivery_time']).strftime('%Y-%m-%d %H-%M')

    p = out_path / f'{time} {id}.json'
    if p.is_file():
        return False

    p.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return True


def setup_proxy(session: requests.Session, verbose: bool = True):
    url = 'https://ip.me'

    # Setup proxy
    ip = session.get(url).text.strip()
    session.proxies = {
        'http': 'socks5://localhost:9050',
        'https': 'socks5://localhost:9050'
    }
    proxy_ip = session.get(url).text.strip()

    # Print ip
    if verbose:
        print(f'Raw ip: {ip}')
        print(f'Proxy ip: {proxy_ip}')

    # ips shouldn't match
    assert ip != proxy_ip, 'Proxy did not start correctly.'

    # Disable default requests behavior
    def warn(*args, **kwargs):
        raise ReferenceError('Use session.get instead of requests.get')
    requests.get = warn
    requests.post = warn


if __name__ == '__main__':
    setup_proxy(ses)

    prev_date_file = out_path / '0-prev-date.txt'

    def send_req(prev_date: int | None):
        add_param = {'logisticMinDeliveryTime': prev_date} if prev_date is not None else {}

        r = ses.get('https://front.superbuy.com/logistic/get-index-pull-data', params={'onlyPackage': 1, **add_param},
                    cookies={'lang': 'zh-cn'}).json()

        assert r['state'] == 0, 'Request failed.'

        data = r['data']
        successes = [write_entry(i) for i in data]

        print(f'Out of {len(data)} entries, successfully wrote {sum(successes)} entries.')
        prev_date_file.write_text(str(data[-1]['delivery_time'] - 1))

    if not prev_date_file.is_file():
        print('Getting first request...')
        send_req(None)

    while True:
        prev_date = int(prev_date_file.read_text())
        print(f'Getting entries before {prev_date}')
        send_req(prev_date)
