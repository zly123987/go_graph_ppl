import json
import csv
import re
import os
import pymongo
import concurrent.futures
from extract_dependencies.test_semver import sort_versions, is_valid_version
from lib.database import get_mongo_connection
dir = 'generate_csv/csv'
library_csv_doc = [['libraryId:ID(Library)', 'library', ':LABEL']]
lib_ver_doc = [['version', 'library', 'versionId:ID(Version)', ':LABEL']]
upper_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
lower_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
has = [[':START_ID(Library)', ':END_ID(Version)', ':TYPE']]
depend_list = [[':START_ID(Version)', ':END_ID(Library)', 'range', 'versions', ':TYPE']]
default_list = [[':START_ID(Version)', ':END_ID(Version)', ':TYPE']]
libdep_list = [[':START_ID(Library)', ':END_ID(Library)', ':TYPE']]

mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
crawl = c['golang']
golang = crawl['go_affected_dependencies_stable']
golang_size = golang.count()
indices = []
limit = 1000
libdep_list_temp = []
missing_libs = []
libvers = {}


def generate_basic():
    """
    Generate all non-dependency csv files (lib, ver, has, upper, lower)
    """
    count = 0
    if not os.path.exists(dir):
        os.mkdir(dir)

    for file in golang.find(no_cursor_timeout=True):
        lib = file['name']
        content = file['versions']
        library_csv_doc.append([lib, lib, 'Library'])
        header = ''
        verlist = []
        print(count, lib)
        for ver, vercontent in content.items():

            lib_ver_doc.append([ver, lib, lib + ':' + ver, 'Version'])
            if not is_valid_version(ver):
                header = ver
            else:
                verlist.append(ver)
        sorted_vers = sort_versions(verlist)
        if header != '':
            sorted_vers.append(header)
        index = 0
        last_ver = None
        for ver in sorted_vers:
            if not ver:
                continue
            has.append([lib, lib + ':' + ver, 'HAS'])
            if index > 0 and last_ver:
                upper_list.append([lib + ':' + last_ver, lib + ':' + ver, 'UPPER'])
                lower_list.append([lib + ':' + ver, lib + ':' + last_ver, 'LOWER'])
            last_ver = ver
            index += 1
        libvers[lib] = sorted_vers
        count += 1

    with open(dir+"/library_nodes.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(library_csv_doc)
    with open(dir+"/library_versions.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(lib_ver_doc)
    with open(dir+"/has.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(has)
    with open(dir+"/upper.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(upper_list)
    with open(dir+"/lower.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(lower_list)
    c.close()


def parse(index):
    if index in indices:
        return
    c1 = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
    crawl1 = c1['golang']
    golang1 = crawl1['go_affected_dependencies_stable']
    count = 0
    for file in golang1.find(no_cursor_timeout=True).skip(index).limit(limit):
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
    c1.close()

    with open(dir+"/depends" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(depend_list)
    with open(dir+"/default" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(default_list)
    with open(dir+"/libdeps" + str(index) + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(libdep_list)
    with open(dir+"/missing" + str(index) + ".json", "w") as f:
        json.dump(missing_libs, f)


def generate_dep():
    """
    Generate 3 dependency csv files ()
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        future_name = {executor.submit(parse, file): file for file in range(0, int(golang_size), limit)}
        for future in concurrent.futures.as_completed(future_name):
            print('Done!')

def generate_csv():
    generate_basic()
    generate_dep()