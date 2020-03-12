import os
from extract_dependencies.extract_deps_for_package import extract_packages
import pymongo
import json
import concurrent.futures
from datetime import datetime
from lib.database import get_mongo_connection
from postgres_utils import get_affeted_localpath
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
home_dir = os.getcwd()
deps = {}
count = 0
worker = 16

def generate_deps(repo_paths, index, all_count):
    c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
    crawl = c['golang']
    # print(crawl.collection_names())
    staging = crawl['go_affected_dependencies_staging']
    stable = crawl['go_affected_dependencies_stable']
    master = crawl['go_libdepends']
    master_dep = {}
    existing_stable_dep = {}
    lib_deps = {}
    count = 0
    for name, path in repo_paths.items():
        print('index: ' + str(index) + ', count:' + str(count) + ', name: ' + name, all_count)
        count += 1
        try:
            # Get master branch(default) and other existing dependencies
            master_dep_doc = master.find_one({'name': name})
            if master_dep_doc:
                master_dep = master_dep_doc['versions']
                if master_dep:
                    # Remove default branch from excluding list
                    default_branch = list(master_dep.keys())[0]
            stable_dep = stable.find_one({'name': name})
            if stable_dep:
                existing_stable_dep = stable_dep['versions']

            # Extract the new versions' dependencies
            existing_dep = list(existing_stable_dep.keys())
            existing_dep.remove(default_branch) if default_branch in existing_dep else ''
            deps = extract_packages(path, name, existing_dep)
            dependencies = {
                'name': name,
                'versions': {**deps, **master_dep, **existing_stable_dep}
            }
            if dependencies['versions']:
                staging.insert(dependencies, check_keys=False)
        except Exception as e:
            print(e)
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
    affected_libs = json.load(open('affected_libs.json'))
    repo_localpath = get_affeted_localpath(affected_libs)
    print(len(affected_libs), 'libs are affected', len(repo_localpath), 'of them got localpath,'
          , len(affected_libs)-len(repo_localpath), 'are missing.')
    all_count = len(repo_localpath)
    all_dependencies = {}
    batch = 1000
    repo_localpath_list = []
    repo_path_tmp = {}
    for name, path in repo_localpath.items():
        repo_path_tmp[name] = path.replace('/REPOS', '/DATA')
        if batch >= len(repo_path_tmp):
            repo_localpath_list.append(repo_path_tmp)
            repo_path_tmp = {}

    with concurrent.futures.ProcessPoolExecutor(max_workers=worker) as executor:
        future_name = {executor.submit(generate_deps, repo_localpath_list[file], file, all_count): file for file in range(int(len(repo_localpath_list)))}
        for future in concurrent.futures.as_completed(future_name):
            all_dependencies = {**all_dependencies, **future.result()}

    open('all_dependencies.json', 'w').write(json.dumps(all_dependencies))
