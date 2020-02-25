import re
def parse_version(ver):
    return re.split('\+|-', ver.strip())[0]