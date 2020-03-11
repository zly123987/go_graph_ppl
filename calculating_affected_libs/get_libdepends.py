import json
from lib.database import get_mongo_connection
from calculating_affected_libs.get_libaffect import _get_updated_vul_info
import pymongo
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db
c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)

def update_libdepends(added_libdepends):
    golang = c['golang']['go_libdepends']

    for lib, dep in added_libdepends.items():
        existing_dep = golang.find_one({'name': lib})
        if existing_dep:
            golang.update_one(existing_dep,{'$set':{'versions': dep}})
        else:
            print(lib)
            golang.insert({
                'name': lib,
                'versions': dep
            }, check_keys=False)

def update_reverse_libdepends(added_libdepends):
    golang = c['golang']['go_libdepended']
    for lib, deps in added_libdepends.items():
        for branch in deps.keys():
            for dep_lib in deps[branch].keys():
                existing = golang.find_one({'name': dep_lib})
                if existing:
                    depended_list = existing['dep']
                    if lib not in depended_list:
                        depended_list.append(lib)
                        golang.update_one(existing, {'$set': {'dep': depended_list}})
                else:
                    golang.insert({
                        'name': dep_lib,
                        'dep': [lib]
                    }, check_keys=False)

def get_all_affected_libs(vul_libs):
    depended = {}
    for lib in c['golang']['go_libdepended'].find():
        depended[lib['name']] = lib['dep']
    print('github.com/golang/go' in depended.keys())
    temp = vul_libs
    temp2 = []
    all_affected = vul_libs
    while temp:
        for i in temp:
            if i in depended.keys():
                temp2.extend(depended[i])
                temp2 = list(set(temp2))
                for each in temp2:
                    if each in all_affected:
                        temp2.remove(each)
        temp = temp2
        print(len(temp2))
        all_affected.extend(temp2)
        temp2 = []
    open('affected_libs.json', 'w').write(json.dumps(all_affected))


def filter_affecte_libs():
    added_libdepends = json.load(open('../all_dependencies.json', 'r'))
    update_libdepends(added_libdepends)
    update_reverse_libdepends(added_libdepends)
    vulnerable_libs = _get_updated_vul_info()
    get_all_affected_libs(vulnerable_libs)


if __name__=='__main__':
    # added_libdepends = json.load(open('all_dependencies.json', 'r'))
    # update_libdepends(added_libdepends)
    # update_reverse_libdepends(added_libdepends)
    vulnerable_libs = ['github.com/seccomp/libseccomp-golang', 'github.com/couchbase/sync_gateway', 'github.com/ethereum/go-ethereum', 'github.com/sylabs/singularity', 'github.com/google/fscrypt', 'github.com/minio/minio', 'github.com/appc/docker2aci', 'github.com/docker/docker-ce', 'github.com/cockroachdb/cockroach', 'github.com/rkt/rkt', 'github.com/rancher/rancher', 'github.com/mastercactapus/proxyprotocol', 'github.com/kolide/fleet', 'github.com/kubevirt/containerized-data-importer', 'github.com/google/gvisor', 'github.com/opencontainers/runc', 'github.com/mholt/archiver', 'github.com/git-lfs/git-lfs', 'github.com/hashicorp/packer', 'github.com/go-gitea/gitea', 'github.com/goharbor/harbor', 'github.com/github/hub', 'github.com/btcsuite/go-socks', 'github.com/kubernetes/kubernetes', 'github.com/istio/istio', 'github.com/go-ldap/ldap', 'github.com/docker/docker-credential-helpers', 'github.com/gardener/gardener', 'github.com/containous/traefik', 'github.com/ehang-io/nps', 'github.com/gophish/gophish', 'github.com/jinzhu/gorm', 'github.com/astaxie/beego', 'github.com/golang/gddo', 'github.com/pydio/cells', 'github.com/snapcore/snapd', 'github.com/remind101/empire', 'github.com/satori/go.uuid', 'github.com/gogs/gogs', 'github.com/uber/prototool', 'github.com/uber/astro', 'github.com/grafana/grafana', 'github.com/apache/thrift', 'github.com/hashicorp/consul', 'github.com/heketi/heketi', 'github.com/kubernetes/kube-state-metrics', 'github.com/projectatomic/oci-register-machine', 'github.com/lxc/lxd', 'github.com/openshift/origin', 'github.com/concourse/concourse', 'github.com/cloudfoundry/cli', 'github.com/prometheus/prometheus', 'github.com/pusher/oauth2_proxy', 'github.com/docker/libcontainer', 'github.com/robbert229/jwt', 'github.com/openshift/source-to-image', 'github.com/miekg/dns', 'github.com/facebook/fbthrift', 'github.com/rclone/rclone', 'github.com/cloudfoundry/loggregator', 'github.com/hashicorp/nomad', 'github.com/etcd-io/etcd', 'github.com/square/go-jose', 'github.com/golang/go', 'github.com/hybridgroup/gobot', 'github.com/elastic/beats', 'github.com/containers/libpod', 'github.com/apache/trafficcontrol', 'github.com/cactus/go-camo', 'github.com/bitly/oauth2_proxy', 'github.com/helm/helm', 'github.com/containernetworking/plugins', 'github.com/wtfutil/wtf', 'github.com/pwnlandia/agave', 'github.com/nats-io/nats-server', 'github.com/moby/moby']
    # vulnerable_libs = _get_updated_vul_info()
    get_all_affected_libs(vulnerable_libs)

