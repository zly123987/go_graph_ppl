import os
import re
import glob
import io
import subprocess
# def get_standard_packages(go_src_dir):
#     standard_packages = []
#     for file in os.listdir(path=go_src_dir):
#         standard_packages.append(file.split('.')[0])
#     return standard_packages
# standard = get_standard_packages('/home/lcwj3/go/go/src')
# print(standard)
standard_packages = ['debug', 'unsafe', 'make', 'reflect', 'flag', 'errors', 'README', 'iostest', 'image', 'io', 'archive', 'testdata', 'sort', 'all', 'mime', 'bufio', 'text', 'log', 'vendor', 'testing', 'fmt', 'all', 'go', 'clean', 'go', 'run', 'crypto', 'bootstrap', 'strconv', 'hash', 'index', 'html', 'database', 'make', 'net', 'internal', 'run', 'sync', 'regexp', 'compress', 'run', 'context', 'cmp', 'clean', 'unicode', 'builtin', 'bytes', 'encoding', 'syscall', 'path', 'plugin', 'all', 'expvar', 'math', 'go', 'race', 'strings', 'cmd', 'os', 'race', 'clean', 'container', 'Make', 'runtime', 'time', 'make', 'buildall']
filtered_packages = standard_packages + ['_', '']
def get_deps(dir, root_dir):
    deps = []
    try:
        os.chdir(dir)
        go_list = []
        go_list = glob.glob('*.go')
        if not go_list:
            return deps
        if os.path.exists(dir + '/go.mod'):
            os.remove(dir + '/go.mod')
        if os.path.exists(dir + '/go.sum'):
            os.remove(dir + '/go.sum')
        proc = subprocess.Popen('go list -deps', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        proc.wait()
        x = str(io.TextIOWrapper(proc.stdout, encoding='utf-8').read())
        deps = list(a.strip() for a in x.split('\n') if a.split('/')[0] not in filtered_packages and root_dir not in a)
    except Exception as e:
        print(e)
    return deps
# get_deps('.')




def get_deps_without_mod(package_dir, id):
    g = os.walk(package_dir)
    deps_set = set()
    deps = get_deps(package_dir, id)
    deps_set = deps_set | set(deps)
    for root, dirs, files in g:
        for dir in dirs:
            if dir.split('/')[0] in ['.git', 'vendor']:
                continue
            full_path = os.path.join(root, dir)
            if os.path.isdir(full_path):
                deps = get_deps(full_path, id)
                deps_set = deps_set | set(deps)
    deps_dict = {}
    for dep in list(deps_set):
        if re.match(r'.+..+/.+/.+', dep):
            repo_id = '/'.join(dep.split('/')[:3])
            #print(repo_id)
            if repo_id not in deps_dict:
                deps_dict[repo_id] = 'latest'
    return deps_dict

#print(get_deps_without_mod('/home/lcwj3/go_repos/go_repo_sample/go_repos/mattermost-server', 'mattermost-server'))