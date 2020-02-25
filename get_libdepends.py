import json
from lib.database import get_mongo_connection
from collections import defaultdict
import pymongo
mongo = get_mongo_connection()
MONGO_HOST = mongo.host
MONGO_PORT = int(mongo.port)
MONGO_USER = mongo.user
MONGO_PWD = mongo.password
MONGO_AUTH = mongo.auth_source
MONGO_DB = mongo.db

DIRECT_AFFECTED_LIBS = ['github.com/hybridgroup/gobot', 'github.com/minio/minio', 'github.com/google/gvisor',
                       'github.com/grafana/grafana', 'github.com/golang/go', 'github.com/opencontainers/runc',
                       'github.com/mholt/archiver', 'github.com/appc/docker2aci', 'github.com/git-lfs/git-lfs',
                       'github.com/cactus/go-camo', 'github.com/kolide/fleet', 'github.com/hashicorp/consul',
                       'github.com/go-ldap/ldap', 'github.com/hashicorp/nomad', 'github.com/containers/libpod',
                       'github.com/kubernetes/kube-state-metrics', 'github.com/btcsuite/go-socks',
                       'github.com/docker/docker-ce', 'github.com/nats-io/nats-server', 'github.com/google/fscrypt',
                       'github.com/heketi/heketi', 'github.com/ethereum/go-ethereum', 'github.com/etcd-io/etcd',
                       'github.com/rancher/rancher', 'github.com/rkt/rkt', 'github.com/apache/trafficcontrol',
                       'github.com/helm/helm', 'github.com/docker/libcontainer', 'github.com/jinzhu/gorm',
                       'github.com/prometheus/prometheus', 'github.com/istio/istio', 'github.com/goharbor/harbor',
                       'github.com/rclone/rclone', 'github.com/openshift/origin', 'github.com/wtfutil/wtf',
                       'github.com/containernetworking/plugins', 'github.com/cloudfoundry/loggregator',
                       'github.com/openshift/source-to-image', 'github.com/lxc/lxd', 'github.com/miekg/dns',
                       'github.com/couchbase/sync_gateway', 'github.com/satori/go.uuid', 'github.com/sylabs/singularity',
                       'github.com/pydio/cells', 'github.com/hashicorp/packer', 'github.com/golang/gddo',
                       'github.com/docker/docker-credential-helpers', 'github.com/uber/prototool',
                       'github.com/kubernetes/kubernetes', 'github.com/bitly/oauth2_proxy', 'github.com/snapcore/snapd',
                       'github.com/apache/thrift', 'github.com/gardener/gardener', 'github.com/cockroachdb/cockroach',
                       'github.com/pusher/oauth2_proxy', 'github.com/robbert229/jwt', 'github.com/elastic/beats',
                       'github.com/facebook/fbthrift', 'github.com/containous/traefik', 'github.com/go-gitea/gitea',
                       'github.com/cloudfoundry/cli', 'github.com/pwnlandia/agave', 'github.com/concourse/concourse',
                       'github.com/github/hub', 'github.com/astaxie/beego', 'github.com/seccomp/libseccomp-golang',
                       'github.com/square/go-jose', 'github.com/uber/astro', 'github.com/moby/moby',
                       'github.com/remind101/empire', 'github.com/gogs/gogs', 'github.com/kubevirt/containerized-data-importer',
                       'github.com/gophish/gophish', 'github.com/mastercactapus/proxyprotocol',
                       'github.com/projectatomic/oci-register-machine']

def get_libdepends():
    c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
    golang = c['golang']['go_dependencies']
    a = golang.find()
    libdepends = defaultdict(list)
    for i in a:
        if 'master' not in i['versions']:
            continue
        for key, value in i['versions']['master'].items():
            libdepends[i['name']].append(key)

    print(len(libdepends))

def get_reverse_libdepends():
    c = pymongo.MongoClient(MONGO_HOST, port=MONGO_PORT)
    # rev = c['golang']['go_dependencies_reverse']
    golang = c['golang']['go_dependencies']
    a = golang.find()
    libdepended = defaultdict(list)
    for i in a:
        if 'master' not in i['versions']:
            continue
        for key, value in i['versions']['master'].items():
            libdepended[key].append(i['name'])
    for key in libdepended:
        libdepended[key] = list(set(libdepended[key]))
    print(len(libdepended))
    open('reverse_dep.json', 'w').write(json.dumps(libdepended))

def get_affected_libs():
    depended = json.load(open('reverse_dep.json'))
