import base64
from pymemcache.client import base


def DecodeToken(token):
    token = str(token)
    token = token.split('.')
    result = base64.b64decode(token[1])

    d = dict()
    result = str(result)
    result = result.replace("{"," ").replace(","," ").replace("}"," ").replace("'"," ").replace(":"," ").replace("\""," ")
    result = result.split()
    for i in range(1,len(result),2):
        d[result[i]] = result[i+1]
    return d

def ReturnAccessToken(user_id):
    client = base.Client(('localhost', 11211)) # What is it numbers !!!

    return client.get('{}_access'.format(user_id))

def GetRefreshToken(user_id):
    client = base.Client(('localhost', 11211)) # What is it numbers !!!

    return client.get('{}_refresh'.format(user_id))