import pandas as pd
import re
from utils.version_util.github_url import resolve_git_link
from utils.version_util.gitlab_url import resolve_gitlab_link
from utils.version_util.additional_list_url_parser import resolve_other_links
from utils.version_util.models import Spec, clean_ranges, SemanticVersion
from utils.version_util.version_cleaning import clean_ver

def get_clean_range_from_url(dep_name, dep_range):
    # split records in url_list.csv into 4 categories
    # 1: Github, 2: file_dependency 3: GIT (gitlab) 4. others
    counter = 0
    count_file_dependency = 0
    final = []
    gitlab_name = []
    gitlab_url = []
    file_dependency_name = []
    file_dependency_url = []
    url_link_list = []
    hashtag_list = []
    lib_name = []
    abstract_keyword = []
    url_original = []
    url_list = []
    res = pd.DataFrame()
    if ('github' in dep_range):
        if('#semver' in dep_range):
            res = resolve_other_links(dep_name, dep_range)
        else:
            # category: github
            parse_url = re.split('github:|https://|git://|git@|http://|.com:|.com/', dep_range)
            counter += 1
            length = len(parse_url)
            result = parse_url[length - 1].replace('#', '|').replace('.git', '|').replace('.tar.gz', '|').split('|')
            result = result[0].replace('/releases', '/tarball').replace('/archive', '/tarball').split('/tarball')
            name_url = []
            name_url.append(dep_name)
            name_url.append(result[0])
            df1 = pd.DataFrame()
            if '/archive/' in dep_range:
                processing = dep_range.replace('/archive/', '.tar').replace('.zip', '.tar').split('.tar')
                cleaned_version = processing[1]
                df1['version'] = [cleaned_version] if cleaned_version else [processing[1]]
                url_processing = '/' + cleaned_version if cleaned_version else '/' + processing[1]
            elif '#' in dep_range:
                processing = dep_range.split('#')
                cleaned_version = processing[1]
                df1['version'] = [cleaned_version] if cleaned_version else [processing[1]]
                url_processing = '/' + cleaned_version if cleaned_version else '/' + processing[1]
            else:
                url_processing = '/master'
                df1['version'] = ['master']
            url_link = 'https://raw.githubusercontent.com/' + result[0] + url_processing + '/package.json'
            url_link_list.append(url_link)
            name_url.append(dep_range)
            hashtag_list.append(url_processing)
            final.append(name_url)
            final_length = len(final)

            for i in range(final_length):
                url = 'https://github.com/' + final[i][
                    1] + '/blob/master/package.json' + '?access_token=9b0eb93d180ea04e2eeca4db37deca843036e547'
                lib_name.append(final[i][0])
                abstract_keyword.append(final[i][1])
                url_original.append(final[i][2])
                # category: lib_name
                url_list.append(url)
            df1['lib_name'] = lib_name
            df1['url'] = url_list
            df1['abstract_keyword'] = abstract_keyword
            df1['url_original'] = url_original
            df1['url_link_list'] = url_link_list
            df1['hashtag_or_commit_id'] = hashtag_list
            res = resolve_git_link(df1)
    elif ('file:' in dep_range):
        # category: file_dependency
        count_file_dependency += 1
        file_dependency_name.append(dep_name)
        file_dependency_url.append(dep_range)
        df2 = pd.DataFrame()
        df2['file_dependency_name'] = file_dependency_name
        df2['file_dependency_url'] = file_dependency_url
        # return resolve_git_link(df2)
    elif ('git' in dep_range):
        # category: gitlab
        if ('git' in dep_range):
            if ('#semver' in dep_range):
                res = resolve_other_links(dep_name, dep_range)
            else:
                gitlab_name.append(dep_name)
                gitlab_url.append(dep_range)
                df3 = pd.DataFrame()
                df3['lib_name'] = gitlab_name
                df3['url'] = gitlab_url
                # df3.to_csv('df3_gitlab.csv')
                res = resolve_gitlab_link(df3)
    else:
        res = resolve_other_links(dep_name, dep_range)
    if (res.empty == False):
        version = res['version_list'].to_string(index=False)
        version = version.replace(' ', '')
        # version = clean_ranges([version])
        return version if version else "INVALID_URL"
    else:
        return "INVALID_URL"

def is_url(str):
    #TODO: find a best way to judge a url
    regex = re.compile('[@#/:]')
    if not regex.search(str):
        return False
    else:
        return True

'''
    Gets the clean standard dependency range for version ranges and github/gitlab/other urls.
    In case of url, this returns a range or a version. Usually range is preceded by #semver/#/@ in the input url.
    If a range has a version, then this returns the clean version from the url specified.
    Otherwise, gets the version from the master node or commit id specified.
    Arguments:
            dep_name {string} -- name of the dependency library
            dep_range {string} -- version range or the url - git/gitlab/local dependency etc
    Returns:
            cleaned ranges or cleaned urls. 
            If one of them is invalid, then below strings are returned
            ["INVALID_RANGE"] -- If range cannot be resolved into standard range.
            ["INVALID_URL"] -- If the range is an invalid url.
            ["URL_NOT_FOUND"] -- If url is not found
            ["URL_VERSION_NOT_FOUND"] -- If version is not found from the input url
'''
def get_clean_dep_range(dep_name, dep_range):
    #Check if its url, return the version/range received from the url or return invalid url if its not parsable
    if is_url(dep_range):
        return get_clean_range_from_url(dep_name, dep_range)
    else:
        #First clean the range to a standard format, then return invalid_range if its not parsable, otherwise return cleaned range
        cleaned_ranges = clean_ranges([dep_range])
        try:
            spec = Spec(cleaned_ranges[0])
            return cleaned_ranges[0]
        except:
            return "INVALID_RANGE"