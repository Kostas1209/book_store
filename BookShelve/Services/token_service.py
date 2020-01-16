import base64
import memcache


def DecodeToken(token):
    token = str(token)
    token = token.split('.')
    result = base64.b64decode(str(token[1]))
    d = dict()
    result = str(result)
    result = result.replace("{"," ").replace(","," ").replace("}"," ").replace("'"," ").replace(":"," ").replace("\""," ")
    result = result.split()
    for i in range(1,len(result),2):
        d[result[i]] = result[i+1]
    return d

def GetRefreshToken(user_id):

    client = memcache.Client([("cache",11211)])

    return client.get(str(user_id))

def delete_refresh_token(user_id):
    client = memcache.Client([("cache",11211)])
    client.delete(str(user_id))

