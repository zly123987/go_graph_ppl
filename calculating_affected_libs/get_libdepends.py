import json
from lib.database import get_mongo_connection
from calculating_affected_libs.get_libaffect import get_updated_vul_info
import pymongo
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)

def update_libdepends(added_libdepends):
    golang = c['golang']['go_libdepends']

    for lib, dep in added_libdepends.items():
        existing_dep = golang.find_one({'name': lib})
        if existing_dep:
            golang.update_one(existing_dep,{'$set':{'versions': dep}})
        else:
            print(lib)
            golang.insert({
                'name': lib,
                'versions': dep
            }, check_keys=False)

def update_reverse_libdepends(added_libdepends):
    golang = c['golang']['go_libdepended']
    for lib, deps in added_libdepends.items():
        for branch in deps.keys():
            for dep_lib in deps[branch].keys():
                existing = golang.find_one({'name': dep_lib})
                if existing:
                    depended_list = existing['dep']
                    if lib not in depended_list:
                        depended_list.append(lib)
                        golang.update_one(existing, {'$set': {'dep': depended_list}})
                else:
                    golang.insert({
                        'name': dep_lib,
                        'dep': [lib]
                    }, check_keys=False)

def get_all_affected_libs(vul_libs):
    depended = {}
    for lib in c['golang']['go_libdepended'].find():
        depended[lib['name']] = lib['dep']
    print('github.com/golang/go' in depended.keys())
    temp = vul_libs
    temp2 = []
    all_affected = vul_libs
    while temp:
        for i in temp:
            if i in depended.keys():
                temp2.extend(depended[i])
                temp2 = list(set(temp2))
                for each in temp2:
                    if each in all_affected:
                        temp2.remove(each)
        temp = temp2
        print(len(temp2))
        all_affected.extend(temp2)
        temp2 = []
    open('affected_libs.json', 'w').write(json.dumps(all_affected))


def filter_affected_libs():
    added_libdepends = json.load(open('../all_dependencies.json', 'r'))
    update_libdepends(added_libdepends)
    update_reverse_libdepends(added_libdepends)
    vulnerable_libs = get_updated_vul_info(lib_only=True)
    get_all_affected_libs(vulnerable_libs)


