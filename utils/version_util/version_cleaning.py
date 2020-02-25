import re


IGNORE_VERSION_KEYWORDS = ['branch', 'merge', 'fix', 'test', 'before', 'after',
                           'with', 'point', 'cve-', 'ce-', 'commit', 'start',
                           'initial', 'first', 'last', 'wip']
KNOWN_UPDATES = ['alpha', 'beta', 'milestone', 'rc', 'cr', 'snapshot',
                 'final', 'ga', 'sp', 'pre', 'pre-release', 'pr',
                 'test', 'dev', 'release']
LANGUAGE_SPECIFIC_KNOWN_UPDATES = {'maven' : ['m', 'SEC', 'b']}
SKIP_STANDARDIZATION = ['bsd-mailx', 'iputils']

def tag_clean_first(lib, ver_list):
    """ Customized repo tag cleaning - pending refactoring
    """

    tmp_ver = None
    if lib == 'binutils':
        tmp_ver = [i.replace('binutils-', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'gdb':
        tmp_ver = [i.replace('gdb_', '').replace('gdb-', '').replace('-release',
                                                                     '').split('-')[0].replace('_', '.') for i in ver_list if 'release' in i]
    elif lib == 'dnsmasq':
        tmp_ver = [i.split('test')[0].split('rc')[0].replace('v', '')
                   for i in ver_list]
    elif lib == 'curl':
        tmp_ver = [i.replace('curl-', '').replace('_', '.') for i in ver_list]
    elif lib == 'busybox':
        tmp_ver = [i.replace('_pre', '-pre').replace('_rc',
                                                     '-rc').replace('00', '0.0').replace('_', '.') for i in ver_list]
    elif lib == 'zlib':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libarchive':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'openssl':
        tmp_ver = [i.replace('OpenSSL-fips-', '').replace('OpenSSL_',
                                                          '').replace('_', '.') for i in ver_list]
    elif lib == 'openvpn':
        tmp_ver = [i.replace('v', '').replace('_', '-') for i in ver_list]
    elif lib == 'sqlite':
        tmp_ver = [i.replace('version-', '') for i in ver_list]
    elif lib == 'linux':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libxml2':
        tmp_ver = [i.replace('v', '').replace('LIBXML2_', '').replace(
            'LIBXML', '').replace('_', '.') for i in ver_list]
    elif lib == 'dbus':
        tmp_ver = [i.replace('dbus-', '') for i in ver_list]
    elif lib == 'ffmpeg':
        tmp_ver = [i.replace('v', '').replace('n', '')
                   for i in ver_list if '-dev' not in i]
    elif lib == 'libexif':
        tmp_ver = [i.replace('libexif-', '').replace('-release',
                                                     '').replace('_', '.') for i in ver_list if 'libexif-' in i]
    elif lib == 'libexpat':
        tmp_ver = [i.replace('V', '').replace('R_', '').replace(
            '_', '.') for i in ver_list if '_' in i]
    elif lib == 'libplist':
        tmp_ver = [i.replace('v', '') for i in ver_list if '.' in i]
    elif lib == 'libpng':
        tmp_ver = [i.replace('v1', '1').replace('v0', '0').replace(
            'beta', '-beta').replace('rc', '-rc') for i in ver_list if 'v' in i]
    elif lib == 'libtiff':
        tmp_ver = [i.replace('Release-v', '').replace('-', '.').replace('beta', '-beta').replace(
            '.alpha', 'alpha').replace('alpha', '-alpha') for i in ver_list if 'Release-v' in i]
    elif lib == 'tcpdump':
        tmp_ver = [i.replace('tcpdump-', '').replace('-bp', '')
                   for i in ver_list if 'tcpdump-' in i]
    elif lib == 'gcc':
        tmp_ver = [i.replace('gcc-', '').replace('-release', '').replace('_', '.')
                   for i in ver_list if '-release' in i]
    elif lib == 'strace':
        tmp_ver = [i.replace('v', '') for i in ver_list if 'v' in i]
    elif lib == 'libfs':
        tmp_ver = [i.replace('libFS-', '') for i in ver_list if 'libFS' in i]
    elif lib == 'sysklogd':
        tmp_ver = [i.replace('v', '')
                   for i in ver_list if 'v' in i and '.' in i]
    elif lib == 'gnutls':
        tmp_ver = [i.replace('gnutls_', '').replace('_', '.')
                   for i in ver_list if 'gnutls_' in i]
    elif lib == 'pillow':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'freerdp':
        tmp_ver = [i for i in ver_list]
    elif lib == 'open-iscsi':
        tmp_ver = [i for i in ver_list]
    elif lib == 'openldap':
        tmp_ver = [i.replace('OPENLDAP_REL_ENG_', '').replace(
            'LMDB_', '').replace('_', '.') for i in ver_list]
    elif lib == 'libxi':
        tmp_ver = [i.replace('libXi-', '') for i in ver_list if 'libXi-' in i]
    elif lib == 'glibc':
        tmp_ver = [i.replace('glibc-', '')
                   for i in ver_list if 'glibc-' in i and '/' not in i]
    elif lib == 'flac':
        tmp_ver = [i for i in ver_list]
    elif lib == 'mesa':
        tmp_ver = [i.replace('mesa-', '') for i in ver_list]
    elif lib == 'libvpx':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'pixman':
        tmp_ver = [i.replace('pixman-', '') for i in ver_list]
    elif lib == 'libimobiledevice':
        tmp_ver = [i for i in ver_list]
    elif lib == 'libcap':
        tmp_ver = [i.replace('libcap-korg-', '').replace('libcap-', '')
                   for i in ver_list if '.' in i]
    elif lib == 'vino':
        tmp_ver = [i for i in ver_list if '.' in i]
    elif lib == 'protobuf':
        tmp_ver = [i.replace('v', '') for i in ver_list if '.' in i]
    elif lib == 'ppp':
        tmp_ver = [i.replace('ppp-', '') for i in ver_list if '.' in i]
    elif lib == 'glib':
        tmp_ver = [i for i in ver_list if '.' in i]
    elif lib == 'libxtst':
        tmp_ver = [i.replace('libXtst-', '')
                   for i in ver_list if 'libXtst' in i]
    elif lib == 'iputils':  # FIXME
        tmp_ver = [i for i in ver_list]
    elif lib == 'libvirt':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libsndfile':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'aspell':
        tmp_ver = [i.replace('rel-', '') for i in ver_list]
    elif lib == 'e2fsprogs':  # ignore debian/ ?
        tmp_ver = [i.replace('v', '') for i in ver_list if '/' not in i]
    elif lib == 'gparted':
        tmp_ver = [i.replace('GPARTED_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'libwebp':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'rdesktop':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'cairo':
        tmp_ver = [i for i in ver_list]
    elif lib == 'brltty':
        tmp_ver = [i.replace('BRLTTY-', '') for i in ver_list]
    elif lib == 'initramfs-tools':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'polkit':
        tmp_ver = [i.replace('POLICY_KIT_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'taglib':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'taglib':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'qt5':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'json-c':
        tmp_ver = [i.replace('json-c-', '') for i in ver_list]
    elif lib == 'gmime':
        tmp_ver = [i.replace('GMIME_', '').replace('_', '.') for i in ver_list]
    elif lib == 'shadow':
        tmp_ver = [i for i in ver_list if '.' in i]
    elif lib == 'libevent':
        tmp_ver = [i.replace('release-', '').replace('-stable', '')
                   for i in ver_list]
    elif lib == 'libfishsound':
        tmp_ver = [i.replace('Speex-', '') for i in ver_list if '.' in i]
    elif lib == 'libx11':
        tmp_ver = [i.replace('libX11-', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'graphviz':
        tmp_ver = [i.replace('stable_release_', '')
                   for i in ver_list if '.' in i]
    elif lib == 'multipath-tools':
        tmp_ver = [i for i in ver_list]
    elif lib == 'orc':
        tmp_ver = [i.replace('orc-', '') for i in ver_list if '.' in i]
    elif lib == 'dbus-glib':
        tmp_ver = [i.replace('dbus-glib-', '').replace('dbus-glib_', '')
                   for i in ver_list if '.' in i]
    elif lib == 'libvorbis':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libxt':
        tmp_ver = [i.replace('libXt-', '').replace('_', '-')
                   for i in ver_list if 'libXt' in i]
    elif lib == 'groff':
        tmp_ver = [i.replace('groff-', '').replace('_', '.')
                   for i in ver_list if ('.' in i or 'groff' in i)]
    elif lib == 'libmatroska':
        tmp_ver = [i.replace('release-', '') for i in ver_list]
    elif lib == 'liblouis':
        tmp_ver = [i.replace('liblouis_', '').replace('LIBLOUIS_', '').replace(
            'v', '').replace('_', '.') for i in ver_list]
    elif lib == 'libical':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'lua':
        tmp_ver = [i.replace('v', '').replace(
            '_', '.').replace('-', '.') for i in ver_list]
    elif lib == 'ceph':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'xen':
        tmp_ver = [i.replace('RELEASE-', '')
                   for i in ver_list if 'shim' not in i]
    elif lib == 'cpio':
        tmp_ver = [i.replace('release_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'libgdata':
        tmp_ver = [i.replace('LIBGDATA_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'accountsservice':
        tmp_ver = [i for i in ver_list if '.' in i]
    elif lib == 'libav':
        tmp_ver = [i.replace('v', '').replace('_', '-') for i in ver_list]
    elif lib == 'libxslt':
        tmp_ver = [i.replace('LIBXSLT_', '').replace(
            'v', '').replace('_', '.') for i in ver_list]
    elif lib == 'ghostscript':
        tmp_ver = [i.replace('ghostpdl-', '').replace('rc', '-rc')
                   for i in ver_list]
    elif lib == 'xmlsec':
        tmp_ver = [i.replace('xmlsec-', '').replace('_', '.')
                   for i in ver_list if 'xmlsec' in i]
    elif lib == 'guile':
        tmp_ver = [i.replace('v', '').replace('release_', '').replace(
            '-', '.') for i in ver_list if '/' not in i]
    elif lib == 'util-linux':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'openexr':
        tmp_ver = [i.replace('v', '').replace('OPENEXR_VIEWERS_', '').replace(
            'OPENEXR_', '').replace('_', '.') for i in ver_list if ('OPEN' in i or 'v' in i)]
    elif lib == 'screen':
        tmp_ver = [i.replace('v.', '') for i in ver_list]
    elif lib == 'dhcp':
        tmp_ver = [i.replace('v', '').replace('_', '.') for i in ver_list]
    elif lib == 'lame':
        tmp_ver = [i.replace('RELEASE__', '').replace('lame', '').replace(
            '_with_psymodel_v3_99_5', '').replace('_', '.') for i in ver_list if ('RELEASE' in i or 'lame' in i)]
    elif lib == 'harfbuzz':
        tmp_ver = [i for i in ver_list]
    elif lib == 'libssh2':
        tmp_ver = [i.replace('libssh2-', '').replace('RELEASE.', '')
                   for i in ver_list]
    elif lib == 'libgsf':
        tmp_ver = [i.replace('LIBGSF_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'git':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'ocaml':
        tmp_ver = [i.replace('+', '-') for i in ver_list]
    elif lib == 'bsd_mailx':  # FIXME
        tmp_ver = [i.replace('upstream/', '')
                   for i in ver_list if 'upstream' in i]
    elif lib == 'pdfium':  # FIXME
        tmp_ver = [i for i in ver_list]
    elif lib == 'libxcursor':
        tmp_ver = [i.replace('libXcursor-', '')
                   for i in ver_list if 'libXcursor' in i]
    elif lib == 'openjpeg':
        tmp_ver = [i.replace('version.', '').replace('v', '')
                   for i in ver_list]
    elif lib == 'tbb':  # FIXME
        tmp_ver = [i for i in ver_list]
    elif lib == 'procps':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'iproute2':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libidn2':
        tmp_ver = [i.replace('libidn2-', '') for i in ver_list]
    elif lib == 'yelp':
        tmp_ver = [i for i in ver_list]
    elif lib == 'gtk':
        tmp_ver = [i for i in ver_list]
    elif lib == 'nano':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libxp':
        tmp_ver = [i.replace('libXp-', '') for i in ver_list if 'libXp' in i]
    elif lib == 'geoip':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'gupnp':
        tmp_ver = [i.replace('gupnp-', '') for i in ver_list]
    elif lib == 'libxvmc':
        tmp_ver = [i.replace('libXvMC-', '')
                   for i in ver_list if 'libXvMC' in i]
    elif lib == 'libebml':
        tmp_ver = [i.replace('release-', '') for i in ver_list]
    elif lib == 'ibus':
        tmp_ver = [i for i in ver_list]
    elif lib == 'lvm2':
        tmp_ver = [i.replace('v', '').replace('_', '.') for i in ver_list]
    elif lib == 'hostapd':
        tmp_ver = [i.replace('hostap_', '').replace(
            'hostap-', '').replace('_', '.') for i in ver_list if 'hostap' in i]
    elif lib == 'pulseaudio':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'fuse':
        tmp_ver = [i.replace('fuse-', '').replace('fuse_',
                                                  '').replace('_', '.') for i in ver_list]
    elif lib == 'libproxy':
        tmp_ver = [i.replace('libproxy-', '') for i in ver_list]
    elif lib == 'bind9':
        tmp_ver = [i.replace('v', '').replace('_', '.') for i in ver_list]
    elif lib == 'xfsprogs':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libgtop':
        tmp_ver = [i.replace('LIBGTOP_', '').replace('_', '.')
                   for i in ver_list]
    elif lib == 'libsrtp':
        tmp_ver = [i.replace('v', '') for i in ver_list if '.' in i]
    elif lib == 'file':
        tmp_ver = [i.replace('FILE', '').replace('_', '.') for i in ver_list]
    elif lib == 'libxext':
        tmp_ver = [i.replace('libXext-', '')
                   for i in ver_list if 'libXext' in i]
    elif lib == 'graphite':
        tmp_ver = [i.replace('Release_', '').replace('r', '')
                   for i in ver_list]
    elif lib == 'python':
        tmp_ver = [i.replace('v', '') for i in ver_list if '.' in i]
    elif lib == 'libssh':
        tmp_ver = [i.replace('libssh-', '').replace('release-',
                                                    '').replace('-', '.') for i in ver_list]
    elif lib == 'grep':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'systemd':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'spice':
        tmp_ver = [i.replace('v', '').replace('spice-client-', '').replace(
            'spice-server-', '').replace('spice-common-', '') for i in ver_list]
    elif lib == 'linux-pam':
        tmp_ver = [i.replace('v', '').replace(
            'Linux-PAM-', '').replace('_', '.').replace('-', '.') for i in ver_list]
    elif lib == 'lz4':  # FIXME
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'librsync':
        tmp_ver = [i.replace('v', '') for i in ver_list]
    elif lib == 'libgxps':
        tmp_ver = [i for i in ver_list]
    elif lib == 'libtool':
        tmp_ver = [i.replace('release-', '').replace('v',
                                                     '').replace('-', '.') for i in ver_list]
    elif lib == 'libpcap':
        tmp_ver = [i.replace('libpcap-', '').replace('libpcap_',
                                                     '').replace('_', '.') for i in ver_list]
    elif lib == 'gimp':
        tmp_ver = [i.replace('GIMP_', '').replace(
            '_RC', '-RC').replace('_', '.') for i in ver_list]
    elif lib == 'libvncserver':
        tmp_ver = [i.replace('LibVNCServer-', '').replace('X11VNC_REL_',
                                                          '').replace('X11VNC_', '').replace('_', '.') for i in ver_list]
    return tmp_ver


def ignore_keyword_check(ver):
    matches = list(filter(lambda x: x in ver, IGNORE_VERSION_KEYWORDS))
    if len(matches):
        return True
    return False


def get_suffix(serial, extra, update, language=None):
    # print (serial if serial else 's',
    #        extra if extra else 'e', update if update else 'u')
    known_updates = KNOWN_UPDATES
    if(language):
        known_updates.extend(LANGUAGE_SPECIFIC_KNOWN_UPDATES.get(language))
    clean_data = {
        'serial': '',
        'update': ''
    }

    # Clean the update
    res = re.match(r'^(?:\W*)(\w*.*)', update)
    if res:
        update = res[1]
    for s in known_updates:
        try:
            if update.index(s.lower()) == 0:
                # Valid update version, prefix with '-'
                clean_data['update'] = update
                break
        except:
            pass

    # If update not already found, check if suffix holds this info
    if not clean_data['update']:
        res = re.match(r'^(?:\W*)(\w*.*)', serial)
        if res:
            serial = res[1]
        for s in known_updates:
            try:
                if serial.index(s.lower()) == 0:
                    # Valid update version, prefix with '-'
                    clean_data['update'] = serial
                    break
            except:
                pass
    if not clean_data['update']:
        clean_data['serial'] = serial

    if extra:
        # Remove non alphanumeric characters in the beginning of the string
        extra = re.sub(r'^\W*', '', extra)
        if extra:
            if clean_data['serial']:
                clean_data['serial'] += '-' + extra
            elif clean_data['update']:
                clean_data['update'] += '-' + extra

    # Do one last cleansing on the update string
    # beta_01, beta-01, beta01, beta-01-1, will all be converted to beta01
    if clean_data['update']:
        if 'pre-release' in clean_data['update']:
            clean_data['update'].replace('pre-release', 'pre')
        res = re.match(
            r'^(?:\W*)([A-Za-z]*)(?:[\W_]*)(\d*)', clean_data['update'])
        clean_data['update'] = res[1] + res[2]

    suffix_string = clean_data['serial']
    if clean_data['update']:
        suffix_string += '-' + clean_data['update']
    # If suffix begins with a number, hyphenate
    if re.match('(^\d)', suffix_string):
        suffix_string = '-' + suffix_string
    return suffix_string


def clean_ver(ver, language=None):
    """ Generic version standardization script
    """

    if not ver:
        ver = ''

    # Basic clean up, NVD versions cleaning
    ver = ver.lower()
    ver = (ver
           .replace('####', '-')
           .replace('.x', '.0')
           .replace('-*', '')
           .replace('-sparc', '')
           .replace('-x86', ''))

    parts = ver.split(':')

    # Check if version is to be ignored
    # If no digit in version, ignore
    if not re.search(r'[A-Za-z\d]', parts[0]):
        return None
    elif ignore_keyword_check(ver):
        return None

    # Deal with +dfsg in version number for back-propagated vulns
    # from Debian version list
    suffix = ''
    idx = ver.find('+dfsg')
    if idx > -1:
        suffix = ver[idx:]

    # Simple substitutions
    ver = re.sub(r'[\\/]', '', ver)
    ver = re.sub(r'\.{2,}', '.', ver)
    ver = re.sub(r'\-{2,}', '-', ver)
    ver = re.sub(r'\_{2,}', '_', ver)

    c = ver.split(':')[0]

    if len(c) > 2:
        if c[:2] in ['a.', 'b.', 'c.']:
            c = c[2:]
    if len(c) > 1 and c[0] == 'v':
        c = c[1:]

    if len(c) > 1:
        if c[-1] == '-':
            c = c[:-1]

    if len(c) > 1:
        if c[-1] == '-':
            c = c[:-1]

    try:
        if c.index('build_') == 0:
            c = c[6:]
    except:
        pass

    # If . is the first character and there is only 1 number, prefix 0
    if re.match(r'^(\.\d+)\.{0}[\D\w]*$', c):
        c = '0' + c
    elif c[0] == '.' and len(c) > 1:
        # If . is the first character, remove it
        c = c[1:]

    # Convert 2.3.4(2a) to 2.3.4.2a
    res = re.match(r'(\d+[\.-])+\d+(\(\d\w+\))', c)
    if res:
        c = c.replace(res.group(2), '.' + res.group(2)[1:-1])

    # Replace other brackets
    c = c.replace('(', '').replace(')', '')

    # Extract the number
    res = re.match(r'(^(?:[\d]+\.){1,5}\d+)(?:[\W_]*)([A-Za-z\d]*)', c)
    if not res:
        res = re.search(r'((?:[\d]+_){1,5}\d+)(?:[\W_]*)([A-Za-z\d]*)', c)
    if not res:
        res = re.search(r'((?:[\d]+-){1,5}\d+)(?:[\W_]*)([A-Za-z\d]*)', c)
    if not res:
        res = re.search(r'((?:[\d]+\.){1,5}\d+)(?:[\W_]*)([A-Za-z\d]*)', c)

    # Get the vernum + suffix
    update = ''  # ver.split(':')[1]
    if res:
        matches = res.groups()
        vernum, serial, extra = matches[0], matches[1], ''
        vernum = vernum.replace('_', '.').replace('-', '.')
        # Eg: Convert 11 to 11.0.0
        vernum_parts = vernum.split('.')
        if len(vernum_parts) == 1:
            vernum += '.0.0'
        elif len(vernum_parts) == 2:
            vernum += '.0'
        if len(matches) > 2:
            extra = matches[2]

        if not suffix:
            suffix = get_suffix(serial, extra, update, language)
        cleaned_version = vernum + suffix
        return cleaned_version

    # Cannot do a good match, try matching 1 number only
    res = re.match('^(\d+)', c)
    if res:
        vernum = res.group(1) + '.0.0'
        if len(res.groups()) > 2:
            return vernum + '-' + res.group(2)
        else:
            return vernum

    # Default
    if update:
        cleaned_version = c + '-' + update
    else:
        cleaned_version = c
    return cleaned_version
