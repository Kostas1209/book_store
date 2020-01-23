import memcache


TIME_FOR_SAVE = 30*24*60*60 # 1 month
cache_client = memcache.Client([("cache",11211)])
    #refresh_token.set(info['user_id'], data['refresh'],time = 24*60*60)

def save_to_cache(name, data):
    cache_client.set(name, data, time=TIME_FOR_SAVE)


def is_in_cache(name : str):
    return cache_client.get(name)


def get_from_cache(name):
    print("Get {} info".format(name))
    return cache_client.get(name)

def delete_from_cache(name):
     cache_client.delete(name)