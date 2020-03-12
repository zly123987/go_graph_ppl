import ctypes
getMajor = ctypes.CDLL('./extract_dependencies/semver.so').getMajor
getMajor.argtypes = [ctypes.c_char_p]
getMajor.restype = ctypes.c_char_p

getMajorMinor = ctypes.CDLL('./extract_dependencies/semver.so').getMajorMinor
getMajorMinor.argtypes = [ctypes.c_char_p]
getMajorMinor.restype = ctypes.c_char_p


sortVers = ctypes.CDLL('./extract_dependencies/semver.so').sortVers
sortVers.argtypes = [ctypes.c_char_p]
sortVers.restype = ctypes.c_char_p

parse = ctypes.CDLL('./extract_dependencies/parse.so').Parse
parse.argtypes = [ctypes.c_char_p]
parse.restype = ctypes.c_char_p


compareVersion = ctypes.CDLL('./extract_dependencies/semver.so').compareVersion
compareVersion.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
compareVersion.restype = ctypes.c_int

isvalid = ctypes.CDLL('./extract_dependencies/semver.so').isValidVersion
isvalid.argtypes = [ctypes.c_char_p]
isvalid.restype = ctypes.c_bool

def get_major(version_number):
    a = getMajor(version_number.encode())
    return a.decode('utf-8')

def get_major_minor(version_number):
    a = getMajorMinor(version_number.encode())
    return a.decode('utf-8')

def sort_versions(verlist):
    version_number = '|'.join(verlist)
    a = sortVers(version_number.encode())
    return list(a.decode('utf-8').split('|'))

def compare_versions(v1, v2):
    a = compareVersion(v1.encode(), v2.encode())
    return a > 0

def is_valid_version(ver):
    a = isvalid(ver.encode())
    return a

def parse_dep_file(path):
    a = parse(path.encode())
    return list(a.decode('utf-8').split('|'))

# print(parse_dep_file('/home/lcwj3/go_repos/public/bookmarkd/pkg/actions/add.go'))
# test_a = get_major('v1.2.3-hcnkenve')
# test_b = get_major_minor('v1.2.3-hcnkenve')
# test_c = sort_versions(['v1.0.3', 'v1.0.1', 'v1.0.2', 'v1.0.2-hfder'])
# test_d = compare_versions('v1.0.3', 'v1.0.2')
# test_e = is_valid_version('v11.0.3')
# test_f = is_valid_version('1.0.3')
# test_g = is_valid_version('1.3')
# test_h = is_valid_version('v1.3')
# print(test_a)
# print(test_b)
# print(test_c)
# print(test_d)
# print(test_e)
# print(test_f)
# print(test_g)
# print(test_h)