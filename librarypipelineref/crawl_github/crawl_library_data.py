import pymongo
import requests
import json
import concurrent.futures
import datetime
import time
from datetime import datetime, timedelta
from lib.database import get_mongo_connection
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
c = pymongo.MongoClient(MONGO_HOST, username=MONGO_USER,
                        password=MONGO_PWD, port=MONGO_PORT, authSource=MONGO_AUTH)
crawl = c['library-crawler']
print(crawl.collection_names())
golang = crawl['go']
## using description to judge if the item is already crawled
partition = int(int(golang.find({'description':{'$exists': False}}).count())/WORKER + 1)
print(partition)
#tokens are from every people in scantist, please don't leak them out
token_sum = [
    '2eeff8a2b015b39732d5ccdd704d763f0eaeaf24',
    '5d6652ecf38702c003cf93e577da51dce3966b22',
    '8d636b909a0853775074a0086fe5844f31341775',
    '8bbab49f728dfe2f8d24133e72b5df6694182388',
    'fce7ccaa37ea90c215e2316fd52baf65c4b0cfa3',
    'd87ff2386248496d4c4b5018b1dc3170e4fdaa90',
    'ec86578e8826e23a515efba3dbe3045a8f0acfc4',
    '5b925bbd889bab4cb1978162aff87b25cee3628a',
    '8a63d8f43734b87ea6197bbec276298d0d99a170',
    '6d960ff5fa99779bf4694146f2cd534ed7306825',
    '5aca901da564bd2597af2175fe38738813ca0536',
    '16ed9533807f976d4d0d7505b5162762283fb65e',
    '80e30b0518f19d6d469fbfc50d3ebb3e764d5055',
    '00e07c81f0428b137f3508ea0bbce9341a65c1b0',
    'f9bc29389fe3de0ad10968a90166c9d50d1a5cad',
    '97b6d38f0ef247f5ad31bbee3408a94075d4b67a',
    '5c4d4e5d600e741154c9010ce628b9e7226a994c',
]
WORKER = 8#int(len(token_sum))
QUOTA = 1000
##
# check how many limits are allowed in this hour, foreach account, github only allows 5K times requests per hour
# #
def check_remaining_limits(token):
    url = f'https://api.github.com/rate_limit?access_token={token}'
    try:
        res = requests.get(url)
        res.raise_for_status()
    except Exception as e:
        print(e)
    remaining = json.loads(res.content.decode())['rate']['remaining']
    if remaining < QUOTA:
        return False
    else:
        return True

def get_available_token():
    for token in token_sum:
        if check_remaining_limits(token):
            return token
    return None


class MyHeaders():
    def __init__(self, t):
        self._tokens = t
    def __iter__(self):
        self._size = len(self._tokens)
        self._i = 0
        return self

    def __next__(self):
        self._i = (self._i + 1) % self._size
        return {'Authorization': f'token {self._tokens[self._i]}'}




##
# requests wrapped with tokens and check limits
# ##

def get_requests(url, token):
    status = True
    while True:
        try:
            res = requests.get(url, headers={'Authorization': f'token {token}'})
            res.raise_for_status()
        except Exception as e:
            raise Exception(e)

        if 'X-RateLimit-Remaining' not in res.headers:
            time.sleep(60)
        else:
            rate_limit_remaining = int(res.headers["X-RateLimit-Remaining"])
            if rate_limit_remaining < 200:
                status = False
            break

    return res, status




# type can be releases, tags, branches
# github.com/{owner}/{repo},
# gittype is for github.com or bitbucket.org or gitlab.com, may need to check if the real API is in the same format for different gittype
def crawl_versions(owner, repo, type, token, gittype):
    releases = []
    end = False
    i = 0
    while not end:
        i += 1
        tagurl = f'https://api.{gittype}/repos/{owner}/{repo}/{type}?&per_page=100&page={i}'
        try:
            res2, status = get_requests(tagurl, token)
            result = json.loads(res2.content.decode())
            releases += result
            if not result:
                end = True
        except Exception as e:
            print(e)
            continue
    return releases, status


def download_libvers(skip, token):

    c1 = pymongo.MongoClient(MONGO_HOST, username=MONGO_USER,
                            password=MONGO_PWD, port=MONGO_PORT, authSource=MONGO_AUTH)
    crawl1 = c1['library-crawler']
    print(crawl1.collection_names())
    go = crawl1['go']
    bad_url = crawl1['golang_bad_url']
    count = 0
    with requests.Session() as session:
        for lib in go.find(no_cursor_timeout=True).skip(skip * partition).limit(partition):
            count += 1
            id_info = lib['repo'].split('https://')[1].split('/')
            type = id_info[0]
            owner = id_info[1]
            repo = id_info[2]
            if type == 'github.com':
                libraryurl = f'https://api.{type}/repos/{owner}/{repo}'
            elif type == 'bitbucket.org':
                libraryurl = f'https://api.bitbucket.org/2.0/repositories/{owner}/{repo}'
            elif type == 'gitlab.com':
                libraryurl = f'https://gitlab.com/api/v4/users/{owner}/projects'
            status = True
            res = None
            try:
                if type == 'github.com':
                    res, status = get_requests(libraryurl, token)
                else:
                    res = session.get(libraryurl)
                    res.raise_for_status()
            except Exception as e:
                print(lib['repo'], lib['id'], e, '1234')
                bad_url.insert({'url': libraryurl, 'error': str(e)})
                go.update({'id': lib['id']}, {'$set': {'is_updated': True}})
                continue
            lib_content = json.loads(res.content.decode())
            if type == 'gitlab.com':
                lib_content_temp = {}
                for x in lib_content:
                    if x['path_with_namespace'] == f'{owner}/{repo}':
                        lib_content_temp = x
                        break
                lib_content = lib_content_temp
            lib_content['id'] = lib['id']
            lib_content['repo'] = lib['repo']
            lib_content['is_updated'] = True
            tags, status2 = crawl_versions(owner, repo, 'tags', token, type)
            lib_content['tags'] = tags
            go.update({'id': lib['id']}, lib_content)
            if status and status2:
                pass
            else:
                a = False
                while not a:
                    time.sleep(10 * 60)
                    a = check_remaining_limits(token)
            print(count + skip * partition, lib['id'])


def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER) as executor:
        future_name = {executor.submit(download_libvers, file, token_sum[file]): file for file in range(WORKER)}
        for future in concurrent.futures.as_completed(future_name):
            print('Done!')

run()

