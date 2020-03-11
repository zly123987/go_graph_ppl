import pymongo
from postgres_utils import get_affected_libs
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
crawl = c['golang']
print(crawl.collection_names())
golang = crawl['go_dependencies']
go_affect = crawl['go_dependencies_affected']

##
# 1. Get all master dependencies <a depends on b> from go_dependencies collection in mongodb and store reversely {b:[a]} in libdeps
# 2. Get the affected library id list from postgres
# 3. Find all directly or transitive affectedly libraries using Breadth First Search, starting from vulnerability nodes, and using libaffects relation to find affected libraries.
# 4. comparing with existing affected libs in go_dependencies collection in mongodb, and add an empty entry into this collection if it is newly added.
# ##
def get_new_libraries():
    libdeps = []
    for file in golang.find(no_cursor_timeout=True):
        for ver, ver_content in file['versions'].items():
            for deplib, depver in ver_content.items():
                if deplib in libdeps:
                    libdeps[deplib].append(file['name'])
                else:
                    libdeps[deplib] = [file['name']]
    ids = []
    lib_pubs = get_affected_libs()
    for row in lib_pubs:
        if row[1] not in ids:
            if '/'.join(row[0].split('/')[:2]) == 'github.com/golang':
                id = 'golang.org/x/' + row[0].split('/')[2]
            else:
                id = row[0]
            ids.append(id)

    ids_temp = ids
    ids = []
    for id in ids_temp:
        if '/'.join(id.split('/')[:2]) == 'golang.org/x':
            id = 'github.com/golang/' + id.split('/')[2]
        ids.append(id)
    new_ids = ids.copy()
    ids = set(ids)
    missing = set()
    while new_ids:
        print(len(ids), len(missing))
        laste_ids = new_ids
        new_ids = []
        for id in laste_ids:
            if '/'.join(id.split('/')[:2]) == 'golang.org/x':
                id = 'github.com/golang/' + id.split('/')[2]
            if id not in libdeps:
                missing.add(id)
                continue
            for package in libdeps[id]:
                if package not in ids:
                    ids.add(package)
                    new_ids.append(package)
    new_ids = []
    for id in ids:
        if not go_affect.find_one({'name':id}, no_corsur_timeout=True):
            new_ids.append(id)
            go_affect.insert({'name': id, 'versions':{}})
