import os
from git import Repo, Git
from extract_dependencies.mod_parser import parse_mod
from extract_dependencies.test_semver import is_valid_version
#get the latest version for each majorminor
# def filter_tags_name(tag_list):
#     filtered_tag_dict = {}
#     mm_tag_mapping = {}
#     filtered_tags = list(x for x in tag_list if is_valid_version(x))
#     if not filtered_tags:
#         return [], {}, {}
#     sorted_tags = sort_versions(filtered_tags)
#     for tag in sorted_tags:
#         mm_v = get_major_minor(tag)
#         filtered_tag_dict[mm_v] = tag
#         mm_tag_mapping[tag] = mm_v
#     return sorted_tags, filtered_tag_dict, mm_tag_mapping
def extract_package_master(dir, id):
    repo = Repo(dir)
    lib_deps = {}
    os.chdir(dir)
    try:
        repo.git.checkout('master')
        deps = parse_mod(dir, id)
    except Exception as e:
        print(e, id)
        with open('failed_id','a') as f:
            f.write(id)
    lib_deps['master'] = deps
    return lib_deps



def extract_packages(dir, id, existing):
    repo = Repo(dir)
    valid_branches = []
    tags = repo.tags
    tag_names = []
    lib_deps = {}
    for tag in tags:
        if is_valid_version(tag.name):
            tag_names.append(tag.name)
    tag_names = [t for t in tag_names if t not in existing]
    os.chdir(dir)
    count = 0
    if tag_names:
        for tag in tag_names:
            print(count, tag)
            count += 1
            repo.git.clean('-xdf')
            repo.git.checkout(tag, force=True)
            #os.system('git checkout ' + tag)
            # proc = subprocess.Popen('git checkout ' + tag, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, bufsize=-1)
            # proc.wait()
            deps = parse_mod(dir, id)
            lib_deps[tag] = deps
        # for tag in valid_tags:
        #     lib_deps[tag] = lib_deps[tag_dict[mm_tag_mapping[tag]]]
    # proc = subprocess.Popen('git checkout master', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, bufsize=-1)
    # proc.wait()
    else:
        for branch in repo.heads:
            if is_valid_version(branch.name):
                valid_branches.append(branch.name)
        valid_branches = [t for t in valid_branches if t not in existing]
        for valid_branch in valid_branches:
            print(count, valid_branch)
            count += 1
            repo.git.clean('-xdf')
            repo.git.checkout(valid_branch, force=True)
            deps = parse_mod(dir, id)
            lib_deps[valid_branch] = deps
    return lib_deps
