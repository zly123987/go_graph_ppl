## Format ids and extract github_urls
###
# input: a raw package id
# output: github url and a formatted id
# ##
def parse_repourl_from_id(id):
    data = {}
    data['id'] = id
    data['address_type'] = id.split('/')[0]
    try:
        if data['address_type'] == 'github.com':
            id = '/'.join(list(data['id'].split('/')[:3]))
            github_url = 'https://' + id
        elif data['address_type'] == 'gopkg.in':
            if data['id'].count('/') == 1:
                pkg_name = data['id'].split('/')[1]
                if '.' in pkg_name:
                    pkg_name = pkg_name.split('.')[0]
                github_url = 'https://github.com/go-' + pkg_name + '/' + pkg_name
                id = data['id'].split('/')[0] + '/' + pkg_name
            elif data['id'].count('/') >= 2:
                pkg_info = data['id'].split('/')
                if '.v' in pkg_info[1]:
                    pkg_name = pkg_info[1].split('.')[0]
                    github_url = 'https://github.com/go-' + pkg_name + '/' + pkg_name
                    id = data['id'].split('/')[0] + '/' + pkg_name
                else:
                    pkg_user = pkg_info[1]
                    pkg_name = pkg_info[2]
                    if '.' in pkg_name:
                        pkg_name = pkg_name.split('.')[0]
                    github_url = 'https://github.com/' + pkg_user + '/' + pkg_name
                    id = '/'.join(data['id'].split('/')[:2]) + '/' + pkg_name
        elif data['address_type'] == 'bitbucket.org':
            github_url = 'https://' + '/'.join(data['id'].split('/')[:3])
            id = '/'.join(data['id'].split('/')[:3])
        elif data['address_type'] == 'k8s.io':
            pkg_info = data['id'].split('/')
            github_url = 'https://github.com/kubernetes/' + pkg_info[1]
            id = '/'.join(data['id'].split('/')[:2])
        elif data['address_type'] == 'code.cloudfoundry.org':
            pkg_info = data['id'].split('/')
            github_url = 'https://github.com/cloudfoundry/' + pkg_info[1]
            id = '/'.join(data['id'].split('/')[:2])
        elif data['address_type'] == 'golang.org':
            pkg_info = data['id'].split('/')
            github_url = 'https://github.com/golang/' + pkg_info[2]
            id = '/'.join(data['id'].split('/')[:3])
        elif data['address_type'] == 'pkg.re':
            pkg_info = data['id'].split('/')
            if len(pkg_info) == 2:
                name = pkg_info[1].split('.')[0]
                user = 'go-' + name
                id = 'pkg.re/' + name
            elif len(pkg_info) >= 3:
                user = pkg_info[1]
                name = pkg_info[2].split('.')[0]
                id = 'pkg.re/' + user + '/' + name
            else:
                print(pkg_info)
            github_url = 'https://github.com/' + user + '/' + name
        elif data['address_type'] == 'gitlab.com':
            github_url = 'https://' + '/'.join(data['id'].split('/')[:3])
            id = '/'.join(data['id'].split('/')[:3])
        elif data['address_type'] == 'go.uber.org':
            pkg_info = data['id'].split('/')
            name = pkg_info[1]
            github_url = 'https://github.com/uber-go/' + name
            id = pkg_info[0] + '/' + name
        elif data['address_type'] == 'cirello.io':
            pkg_info = data['id'].split('/')
            name = pkg_info[1]
            github_url = 'https://github.com/cirello-io/' + name
            id = pkg_info[0] + '/' + name
        else:
            github_url = ''
    except Exception as e:
        print(e, pkg_info)
    return github_url, id

