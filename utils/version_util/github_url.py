###crawl the version and dependencies tags from github url###

from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
from pandas import Series
import json


def resolve_git_link(df1):
    lib_name = []
    url_list = []
    version_list = []
    dependency_list = []
    original_url = []
    # df1 = pd.read_csv('df1_github_url.csv')
    length = len(df1)
    for y in range (0,length):
        raw_git = 'https://raw.githubusercontent.com/'
        partial_url = df1['url'][y].replace('.com/','|').replace('/blob','').split("|")
        full_url = raw_git+partial_url[1]
        lib_name.append(df1['lib_name'][y])
        url_list.append(df1['url_link_list'][y])
        original_url.append(df1['url_original'][y])
        url = df1['url_link_list'][y]
        try:
            soup = BeautifulSoup(urllib.request.urlopen(url),'html.parser')
            r = soup.text.encode("utf-8")
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
        except Exception as e:
            ver = str(df1['version'][0])
            #Checking if appending v in suffix works
            url = url.replace(ver, 'v' + ver)
            try:
                soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
                r = soup.text.encode("utf-8")
                result = json.loads(r)

                if 'version' in result.keys():
                    version_list.append(result['version'])
                else:
                    v = "URL_VERSION_NOT_FOUND"
                    version_list.append(v)
                if 'dependencies' in result.keys():
                    dependency_list.append(result['dependencies'])
                else:
                    d = "URL_DEPS_NOT_FOUND"
                    dependency_list.append(d)
            except Exception as e:
                e = "URL_NOT_FOUND"
                version_list.append(e)
                dependency_list.append(e)

    df = pd.DataFrame()
    df['lib_name'] = lib_name
    df['original_url'] = original_url
    df['url'] = url_list
    df['version_list'] = version_list
    df['dependencies'] = dependency_list
    return df