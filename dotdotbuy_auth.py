import hashlib
import hmac
import time


KEY = 'yaA9pBTwBdTDYz6ruLiJOI8jkijJ3Vs3'


def sign_params(params: dict[str, str]):
    # Add useless keys
    params.update({
        'platform': 'MeowOS', 'appVersion': '114.514', 'apiVersion': '3.0.0', 'language': 'cn',
        'currency': 'CNY', 'appName': 'owo', 'timestamp': str(int(round(time.time() * 1000)))
    })

    # Add signature
    signed_keys = ['userId', 'accessToken', 'platform', 'appVersion', 'apiVersion', 'language', 'currency', 'appName', 'timestamp']
    raw = '&'.join(f'{k}:{params[k]}' for k in sorted(signed_keys))
    params['signature'] = hashlib.md5((KEY + raw + KEY).encode('utf-8')).hexdigest().upper()
    params['signMethod'] = 'md5'
    return params
