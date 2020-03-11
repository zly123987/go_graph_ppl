import os
from repocloneref.extract_dependencies.extract_deps_for_package import extract_packages
import pymongo
import datetime
import json
import concurrent.futures
from lib.database import get_mongo_connection
from postgres_utils import get_go_names_and_localpath
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
go = c['library-crawler']['go']
start = datetime.datetime.now()
home_dir = os.getcwd()
deps = {}
count = 0
def generate_deps(repo_paths, index):
    # c = pymongo.MongoClient(MONGO_HOST, username=MONGO_USER,
    #                         password=MONGO_PWD, port=MONGO_PORT, authSource=MONGO_AUTH)
    # c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
    # crawl = c['golang']
    # print(crawl.collection_names())
    # golang = crawl['go_dependencies_affected_added']
    lib_deps = {}
    count = 0
    for name, path in repo_paths.items():
        print('index: ' + str(index) + ', count:' + str(count) + ', name: ' + name)
        count += 1
        dependencies = {}
        # try:
        deps = extract_packages(path, name)
        print(deps)
        dependencies = {
            'name': name,
            'versions': deps
        }
        #golang.insert(dependencies, check_keys=False)
        # except Exception as e:
        #     print(e)
        lib_deps[name] = deps
    return lib_deps
# a = generate_deps({'rancher': '/home/lcwj3/go_repos/rancher'}, os.getcwd(), 0, 'github.com/rancher/rancher')
# golang.insert(a, check_keys=False)
# b = generate_deps({'public': '/home/lcwj3/go_repos/public'}, os.getcwd(), 1, 'github.com/rancher/rancher')
# golang.insert(b, check_keys=False)

# dir = '/home/lcwj3/go_repos/go_repo_sample/go_repos'
# count = 0
# start = datetime.datetime.now()
# for f in os.listdir(dir):
#     a = generate_deps({f: dir + '/' + f}, count)
#     count += 1
# end = datetime.datetime.now()
# print(end - start)
def run():
    try:
        last_timestamp = go.find_one({'key': 'last_update'})
        if last_timestamp:
            last_timestamp = last_timestamp['datetime'][:10]
        else:
            print('Exiting. Failed to retrieve last updated timestamp from mongodb')
            return
    except:
        print('Exiting. Failed to retrieve last updated timestamp from mongodb')
        return
    repo_localpath = get_go_names_and_localpath(last_timestamp)
    added = {
        'github.com/adampresley/GoHttpService':'/home/cc/workspace/go_ppl/graph_pipeline/repos/GoHttpService',
        'github.com/fox-one/mixin': '/home/cc/workspace/go_ppl/graph_pipeline/repos/mixin',
        'github.com/quan-to/go-vsm': '/home/cc/workspace/go_ppl/graph_pipeline/repos/go-vsm',
        'github.com/D-L-M/spritengine': '/home/cc/workspace/go_ppl/graph_pipeline/repos/spritengine'
    }
    added_names = []
    all_dependencies = {}
    with open('./repocloneref/extract_dependencies/add2.json', 'r') as f:
        added_names = json.load(f)
    #for x in added_names:
    #    added[x] = repo_localpath[x]
    repo_count = len(added)
    batch = 4
    repo_localpath_list = []
    repo_path_tmp = {}
    for name, path in added.items():
        repo_path_tmp[name] = path.replace('/REPOS', '/DATA')
        if batch >= len(repo_path_tmp):
            repo_localpath_list.append(repo_path_tmp)
            repo_path_tmp = {}
    print(len(repo_localpath_list))
    with concurrent.futures.ProcessPoolExecutor(max_workers=36) as executor:
        future_name = {executor.submit(generate_deps, repo_localpath_list[file], file): file for file in range(int(len(repo_localpath_list)))}
        for future in concurrent.futures.as_completed(future_name):
            all_dependencies = {**all_dependencies, **future.result()}
            print('Done!')

    open('all_dependencies.json', 'w').write(json.dumps(all_dependencies))
