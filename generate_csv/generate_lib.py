import json
import csv
import re
import pymongo
import concurrent.futures
from extract_dependencies.test_semver import sort_versions
dir = '/home/lcwj3/golang_data/go_deps'

library_csv_doc = [['libraryId:ID(Library)','library',':LABEL']]
lib_ver_doc = [['version','library','versionId:ID(Version)',':LABEL']]
upper_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
lower_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
has = [[':START_ID(Library)', ':END_ID(Version)', ':TYPE']]
depend_list = [[':START_ID(Version)', ':END_ID(Library)', 'version_range', 'versions', ':TYPE']]
default_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
libdep_list = [[":START_ID(Library)",":END_ID(Library)",":TYPE"]]
libvers = {}
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
golang = crawl['go_dependencies_affected']
golang_size = golang.count()
count = 0
indices = []
# for dir in os.listdir('/home/lcwj3/codes/crawl_golang_gene/import_aff/def'):
#     indices.append(int(dir.split('.')[0].split('default')[1]))
for file in golang.find(no_cursor_timeout=True):
    lib = file['name']
    content = file['versions']
    library_csv_doc.append([lib, lib, 'Library'])
    header = ''
    verlist = []
    for ver, vercontent in content.items():

        lib_ver_doc.append([ver, lib, lib + ':' + ver, 'Version'])
        if ver == 'master':
            header = 'master'
        else:
            verlist.append(ver)
    sorted_vers = sort_versions(verlist)
    sorted_vers.append('master')
    index = 0
    last_ver = None
    for ver in sorted_vers:
        has.append([lib, lib + ':' + ver, 'HAS'])
        if index > 0 and last_ver:
            upper_list.append([lib + ':' + last_ver, lib + ':' + ver, 'UPPER'])
            lower_list.append([lib + ':' + ver, lib + ':' + last_ver, 'LOWER'])
        last_ver = ver
        index += 1
    libvers[lib] = sorted_vers
    print(count)
    count += 1
libdep_list_temp = []
missing_libs = []

with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/lib/library_nodes.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(library_csv_doc)
with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/ver/library_versions.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(lib_ver_doc)
with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/has/has.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(has)
with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/upper/upper.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(upper_list)
with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/lower/lower.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(lower_list)


limit = 500
def parse(index):
    if index in indices:
        return
    c1 = pymongo.MongoClient(MONGO_HOST, username=MONGO_USER,
                            password=MONGO_PWD, port=MONGO_PORT, authSource=MONGO_AUTH)
    crawl1 = c1['golang']
    print(crawl1.collection_names())
    golang1 = crawl1['go_dependencies_affected']
    count = 0
    for file in golang1.find(no_cursor_timeout=True).skip(index).limit(limit):
        # if count == 2403:
        #     break
        lib = file['name']
        content = file['versions']
        for ver, vercontent in content.items():
            for deplib, depver in vercontent.items():
                if deplib.split('/')[0] == 'github.com':
                    if len(list(deplib.split('/'))) > 3:
                        deplib = '/'.join(deplib.split('/')[:3])
                if deplib not in libvers:
                    if re.match(r'golang\.org/x/.+', deplib):
                        try:
                            deplib = 'github.com/golang/' + deplib.split('golang.org/x/')[1]
                        except Exception as e:
                            print(deplib)
                            raise RuntimeError('testError')
                    if re.match(r'golang_org/x/.+', deplib):
                        try:
                            deplib = 'github.com/golang/' + deplib.split('golang_org/x/')[1]
                        except Exception as e:
                            print(deplib)
                            raise RuntimeError('testError')
                if deplib == lib:
                    continue
                if deplib not in libvers:
                    missing_libs.append(deplib)
                    verlist = ''
                    latest = ''
                elif depver in ['latest', 'v0.0.0']:
                    verlist = '|'.join(libvers[deplib])
                    latest = 'master'
                else:
                    verlist = depver
                    latest = depver
                if verlist and latest:
                    depend_list.append([lib + ':' + ver, deplib, depver, verlist, 'DEPENDS'])
                    default_list.append([lib + ':' + ver, deplib + ':' + latest, 'DEFAULT'])
                if lib + '--->' + deplib not in libdep_list_temp:
                    libdep_list.append([lib, deplib, 'LIBDEPENDS'])
                    libdep_list_temp.append(lib + '--->' + deplib)
        count += 1
        print('dep', index, count)


    with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/deps/depends" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(depend_list)
    with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/def/default" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(default_list)
    with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/libdep/libdeps" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(libdep_list)
    with open("/home/lcwj3/codes/crawl_golang_gene/import_aff/miss/missing" + str(index) + ".csv", "w") as f:
        json.dump(missing_libs, f)



with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        # future: name
        insert_docs = []
        future_name = {executor.submit(parse, file): file for file in range(0, int(golang_size), limit)}
        for future in concurrent.futures.as_completed(future_name):
            print('Done!')