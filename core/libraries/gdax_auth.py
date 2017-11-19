import hmac
import hashlib
import time
import base64
from requests.auth import AuthBase

class Authentication(AuthBase):
    #source docs.gdax API signing a Message
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def get_dict(self):
        #WEBSTREAM
        timestamp = str(time.time())
        msg = timestamp + 'UPPERCASE' + '/users/self/verify' + ''
        hmac_ = base64.b64decode(self.secret_key)
        sign = hmac.new(hmac_, msg.encode('ascii'), hashlib.sha256)
        sign_b64 = base64.b64encode(sign.digest()).decode('utf-8')

        reqs={
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': sign_b64,
            'CB-ACCESS-TIMESTAMP':timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE':self.passphrase
        }
        return reqs

    def __call__(self, request):
        #ONLY REQUEST.GET
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        })
        return request
