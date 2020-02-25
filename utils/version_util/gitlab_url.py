###crawl the version and dependencies tags from https://registry.npmjs.org###
import time
import pandas as pd
import json
from bs4 import BeautifulSoup
import urllib.request

def resolve_gitlab_link(contents):
    lib_name = []
    url_list = []
    tag_list = []
    parse_url = []
    version_list = []
    dependencies_list = []
    # contents = pd.read_csv('C:\\Users\\Wen Jie\\Desktop\\dependencies\\git_file.csv')
    length = len(contents)
    version = None
    dependencies = None

    for i in range(length):
        lib_name.append(contents['lib_name'][i])
        url_list.append(contents['url'][i])
        names = str(contents['lib_name'][i])

        if '#' in contents['url'][i]:
            content_split = contents['url'][i].split('#')

            if content_split[1][0] == 'v':
                tag = content_split[1].replace('v','')
            else:
                tag = content_split[1]
            if tag == 'master':
                tag = 'latest'

        elif '/archive' in contents['url'][i]:
            if 'ref=v' in contents['url'][i]:
                content_split = contents['url'][i].split('ref=v')
                content_split = content_split[1]
                tag = content_split
            else:
                tag = 'latest'
        else:
            tag = 'latest'

        if tag == 'latest':
            parser = 'https://registry.npmjs.org/'+names+'/'+str(tag)
        else:
            parser = 'https://registry.npmjs.org/'+names
        parse_url.append(parser)
        tag_list.append(tag)

        try:
            soup = BeautifulSoup(urllib.request.urlopen(parser),'html.parser')
            time.sleep(1)
            r = soup.text.encode("utf-8")
            s = json.loads(r)
            #get the latest version
            if tag == 'latest':
                if 'version' in s.keys():
                    version = s['version']
                else:
                    version = 'URL_VERSION_NOT_FOUND'
                if 'dependencies' in s.keys():
                    dependencies = s['dependencies']
                else:
                    dependencies = 'URL_DEPS_NOT_FOUND'

            else:
                version_key_list = list(s['versions'].keys())
                n = len(version_key_list)
                if '.' in tag:
                    for count in range (n):
                        if 'version' in (s['versions'][version_key_list[count]]).keys():
                            if s['versions'][version_key_list[count]]['version'] == tag:
                                version = s['versions'][version_key_list[count]]['version']
                                if 'dependencies' in (s['versions'][version_key_list[count]]).keys():
                                    dependencies = s['versions'][version_key_list[count]]['dependencies']
                                else:
                                    dependencies = 'URL_DEPS_NOT_FOUND'
                else:
                    for l in range(n):
                        if 'gitHead' in (s['versions'][version_key_list[l]]).keys():
                            if s['versions'][version_key_list[l]]['gitHead'] == tag:
                                if 'version' in s['versions'][version_key_list[l]].keys():
                                    version = s['versions'][version_key_list[l]]['version']
                                else:
                                    version = 'URL_VERSION_NOT_FOUND'
                                if 'dependencies' in (s['versions'][version_key_list[l]]).keys():
                                    dependencies = s['versions'][version_key_list[l]]['dependencies']
                                else:
                                    dependencies = 'NO_DEPENDENCIES'
            if version == None:
                     version = 'URL_VERSION_NOT_FOUND'
            if dependencies == None:
                     dependencies = 'URL_DEPS_NOT_FOUND'
        except:
                version = 'URL_NOT_FOUND'
                dependencies = 'URL_NOT_FOUND'

        version_list.append(version)
        dependencies_list.append(dependencies)
        version = None
        dependencies = None
    df = pd.DataFrame()
    df['lib_name'] = lib_name
    df['url_list'] = url_list
    df['tag_list'] = tag_list
    df['parse_url'] = parse_url
    df['version_list'] = version_list
    df['dependencies_list'] = dependencies_list
    return df