import hashlib
import hmac
import time


KEY = 'yaA9pBTwBdTDYz6ruLiJOI8jkijJ3Vs3'


def timestamp() -> str:
    # Java timestamp now
    return str(int(round(time.time() * 1000)))


def sign_params(params: dict[str, str]):
    # Add useless keys
    params.update({
        'platform': 'MeowOS', 'appVersion': '114.514', 'apiVersion': '3.0.0', 'language': 'cn',
        'currency': 'CNY', 'appName': 'owo', 'timestamp': timestamp()
    })

    # Add signature
    signed_keys = ['userId', 'accessToken', 'platform', 'appVersion', 'apiVersion', 'language', 'currency', 'appName', 'timestamp']
    raw = '&'.join(f'{k}:{params[k]}' for k in sorted(signed_keys))
    params['signature'] = hashlib.md5((KEY + raw + KEY).encode('utf-8')).hexdigest().upper()
    params['signMethod'] = 'md5'
    return params


def sign_api(params: dict[str, str]):
    # Add useless keys
    params.update({
        'user_id': params['userId'], 'access_token': params['accessToken'],
        'app_key': 'aaa', 'partner_id': '', 'service': 'dotdotbuy',
        'timestamp': timestamp(),
        'ddb-mobile-platform': 'iOS', 'ddb-mobile-version': '14.4', 'systemversion': '14.4'
    })

    signed_keys = ['access_token', 'app_key', 'partner_id', 'service', 'timestamp', 'user_id']
    raw = ''.join(f'{k}:{params[k]}&' for k in sorted(signed_keys))
    params['sign'] = hashlib.sha1(('456' + raw + '456').encode('utf-8')).hexdigest().lower()
    return params

