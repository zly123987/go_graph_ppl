import requests
import json
from lib.database import get_internal_ip
import time
import random
ip = get_internal_ip()

def is_greater_than(ver1, ver2, session):
    has_session = True
    if session == None:
        session = requests.Session()
        has_session = False
    try:
        port = random.randint(8000, 8007)
        res = session.get(f'http://{ip}:{str(port)}/compare?a={ver1}&b={ver2}'.replace( '+', '%2B'))
        res.raise_for_status()
        if not has_session:
            session.close()
        return res.content.decode() == 'true'
    except Exception as e:
        #print(e)
        time.sleep(0.01)
        return is_greater_than(ver1, ver2, session)

def check_range_type(name, range, session):
    has_session = True
    if session == None:
        session = requests.Session()
        has_session = False
    try:
        port = random.randint(8000, 8007)
        res = session.get(f'http://{ip}:{str(port)}/check?name={name}&range={range}'.replace( '+', '%2B'))
        res.raise_for_status()
        if not has_session:
            session.close()
        return res.content.decode()
    except Exception as e:
        #print(e)
        time.sleep(0.01)
        return check_range_type(name, range, session)


def sort_vers(versionlist, session):
    has_session = True
    if session == None:
        session = requests.Session()
        has_session = False
    try:
        port = random.randint(8000, 8007)
        res = session.post(f'http://{ip}:{str(port)}/sort', json.dumps(versionlist))
        res.raise_for_status()
        if not has_session:
            session.close()
        return res.content.decode().split(',')
    except Exception as e:
        #print(e)
        time.sleep(0.01)
        return sort_vers(versionlist, session)


def check_in_range(ver, versionrange, session):
    if not versionrange:
        return False
    has_session = True
    if session == None:
        session = requests.Session()
        has_session = False
    try:
        port = random.randint(8000, 8007)
        res = session.get(f'http://{ip}:{str(port)}/inrange?version={ver}&range={versionrange}'.replace( '+', '%2B'))
        res.raise_for_status()
        if not has_session:
            session.close()
        return res.content.decode() == 'true'
    except Exception as e:
        #print(e)
        time.sleep(0.01)
        return check_in_range(ver, versionrange, session)

