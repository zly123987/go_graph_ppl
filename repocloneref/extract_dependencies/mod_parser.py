import os
import re
import subprocess
from repocloneref.extract_dependencies.get_deps_without_mod import get_deps_without_mod
def parse_mod(root_dir, id):
    dir_mod = root_dir + '/go.mod'
    dir_gopkg = root_dir + '/Gopkg.lock'
    dir_glide = root_dir + '/glide.lock'
    dir_godep = root_dir + '/Godeps'
    dir_vendor = root_dir + '/vendor/vendor.json'
    deps = {}
    added = False
    if (os.path.exists(dir_gopkg) or os.path.exists(dir_glide) or os.path.exists(dir_godep) or os.path.exists(dir_vendor)) and not os.path.exists(dir_mod):
        os.chdir(root_dir)
        proc = subprocess.Popen('go mod init ' + id, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, bufsize=-1)
        proc.wait()
        added = True
    if os.path.exists(dir_mod):
        with open(dir_mod, 'r') as f:
            file_content = f.read()
            if 'require (' in file_content:
                b = re.findall('require \((.*?)\)', file_content, flags=re.DOTALL)
                for req in b:
                    c = list(x for x in req.split('\n') if x)
                    for dep in c:
                        if 'indirect' in dep:
                            continue
                        depinfo = dep.split(' ')
                        depid = depinfo[0].strip()
                        depver = depinfo[1]
                        #depver = re.split('\+|-', depinfo[1].strip())[0]
                        deps[depid] = depver
            elif 'require' in file_content:
                b = re.findall('require.*?\n', file_content + '\n', flags=re.DOTALL)
                for dep in b:
                    if 'indirect' in dep:
                        continue
                    depinfo = dep.split(' ')
                    depid = depinfo[1].strip()
                    depver = re.split('\+|-', depinfo[2].strip())[0]
                    deps[depid] = depver
        if added:
            os.remove(dir_mod)
    else:
        deps = get_deps_without_mod(root_dir, id)
    return deps

# for x,y in parse_mod('/home/lcwj3/go_repos/OpenDiablo2', 'abc').items():
#     print(x + ':' + y)




