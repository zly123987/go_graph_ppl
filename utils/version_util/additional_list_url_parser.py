###crawl the version and dependencies tags from github url###

import pandas as pd
import json
from bs4 import BeautifulSoup
import urllib.request

'''
Resolves links with ranges preceded by #/@/#semver 
'''
def resolve_other_links(name, url):
    lib_name_list = []
    url_list = []
    version_list = []
    dependency_list = []
    url_parser_list = []
    df = pd.DataFrame()
    import re
    if '#' in url or re.search(r'@\d', url) or re.search(r'@\^', url) or re.search(r'@~', url):
        lib_name_list.append(name)
        url_list.append(url)
        regex = re.compile('[~^]')
        match = regex.search(url)
        if(match):
            version = url[match.start():]
            df['version_list'] = [version]
            return df
        match = regex.search('#release')
        if(match):
            version = url[match.start():]
            df['version_list'] = [version]
            return df
        url = url.replace('Dep : ','').replace('angular-translate', 'angular-translate/angular-translate').replace('#','/').replace('@', '/')
        url_parser = 'https://raw.githubusercontent.com/'+url+'/package.json'+'?access_token=9b0eb93d180ea04e2eeca4db37deca843036e547'
        url_parser_list.append(url_parser)
        try:
            soup = BeautifulSoup(urllib.request.urlopen(url_parser),'html.parser')
            r = soup.text.encode("utf-8").strip()
            result = json.loads(r)
            if 'version' in result.keys():
                version_list.append(result['version'])
            else:
                v = "URL_VERSION_NOT_FOUND"
                version_list.append(v)
            if 'dependencies' in result.keys():
                dependency_list.append(result['dependencies'])
            else:
                d = "NO_DEPENDENCIES"
                dependency_list.append(d)
        except:
            # soup = BeautifulSoup(urllib.request.urlopen(url_parser), 'html.parser')
            e = "URL_NOT_FOUND"
            version_list.append(e)
            dependency_list.append(e)
        df['lib_name'] = lib_name_list
        df['url_list'] = url_list
        df['url_parser_list'] = url_parser_list
        df['version_list'] = version_list
        df['dependency_list'] = dependency_list
    else:
        df['version_list'] = ["INVALID_URL"]
    return df