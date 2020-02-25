import datetime
import re
import time
from distutils.version import Version

'''
This model is used to compare versions and is defined in strict mode with release date property for ease of use
a version consists of major, minor, patch, pre_release, release_date
major, minor, patch must be int
release_date must be in format '2017/01/21'
pre_release should be weighted against keyword list
valid versions:
1.0
5.3-alpha
5.3-alpha.1
2.1.12
2.1.12-beta1021
4.4_build_4.4.000
11.6.5.1.1-20161213
invalid versions:
5.4h.1
3alpha
8231-e2c
v100r002c00spc108
for pre_release:
"alpha" < "beta" < "milestone" < "rc" = "cr" < "snapshot" < "" = "final" = "ga" < "sp"
'''

# Language specific pre-release weights
PRE_RELEASE_WEIGHTS = {
    'c': {
        "alpha": 0,
        "beta": 1,
        "milestone": 2,
        "rc": 3,
        "cr": 3,
        "empty": 4,
        "build": 5,
        "final": 6,
        "ga": 7,
        "sp": 8
    },
}

# Presence of this key in version ranges implies all versions
# are to be matched
ALL_VERSIONS_KEY = 'all_versions'

# Tokens in to be replaced by a '-'
REPLACE_TOKENS = ['####']

NPM_LANG='npm'

class SemanticVersion(Version):
    # "alpha" = "a" < "beta" = "b" < "milestone" < "rc" = "cr" < "snapshot" < "" = "final" = "ga" < "sp"
    pre_release_weight = {
        "build": 0,
        "alpha": 1,
        "beta": 2,
        "milestone": 3,
        "rc": 4,
        "cr": 4,
        "snapshot": 5,
        "final": 7,
        "ga": 8,
        "sp": 9,
        "b": 2,
        "a": 1,
        "m": 3,
        "empty": 6}

    def __init__(self, vstring=None, release_date=None, pre_release_weight=None, language=None):
        self.language = language
        if pre_release_weight:
            self.pre_release_weight = pre_release_weight
        if vstring:
            self.parse(vstring, release_date)

    def parse(self, version_string, release_date=None):
        if not version_string:
            raise ValueError(f"{version_string}: version_string is empty.")

        v_vectors = version_string.split('.')
        v_cnt = len(v_vectors)
        if v_cnt == 1:
            raise ValueError(f"{version_string}: version_string is invalid.")

        major = v_vectors[0]
        if not re.match(r'^\d+$', major):
            raise ValueError(f"{version_string}: major version is invalid.")

        patch = 0
        pre_release = ""

        raw_minor = v_vectors[1]
        if re.match(r'^\d+$', raw_minor):
            minor = raw_minor
        elif re.match(r'^\d+([-_a-zA-Z.]).*$', raw_minor):
            raw_minor = '.'.join(v_vectors[1:])
            index = re.search(r'[-_a-zA-Z.]', raw_minor).start()
            minor = raw_minor[:index]
            pre_release = raw_minor[index:]
            # if minor has pre release info, don look for patch
            v_cnt = 2
        else:
            raise ValueError(f"{version_string}: minor version is invalid.")

        if v_cnt > 2:
            raw_patch = v_vectors[2]
            if re.match(r'^\d+$', raw_patch):
                patch = raw_patch
                pre_release = '.'.join(v_vectors[3:])
            else:
                raw_patch = '.'.join(v_vectors[2:])
                index = re.search(r'[-_a-zA-Z.]', raw_patch).start()
                patch = raw_patch[:index] if raw_patch[:index] else 0
                pre_release = raw_patch[index:]

        try:
            self.major = int(major)
            self.minor = int(minor)
            self.patch = int(patch) if patch else 0
        except ValueError:
            raise ValueError(f"{version_string}: major, minor or patch is invalid.")

        # convert to weight according to priority
        pre_release_weight_key = ""
        for key in list(self.pre_release_weight.keys()):
            if pre_release.__contains__(key):
                pre_release_weight_key = key
                break
            pre_release_weight_key = 'empty' if not pre_release else 'build'

        # Remove _ or - from the beginning of the pre-release string
        if pre_release and pre_release[0] in ('-', '_'):
            if len(pre_release) > 1:
                pre_release = pre_release[1:]
            else:
                pre_release = ''
        self.pre_release = pre_release

        pre_release_num = self.pre_release_weight.get(pre_release_weight_key)
        self.pre_release_num = pre_release_num if pre_release_num else -1

        try:
            release_date = time.mktime(
                datetime.datetime.strptime(release_date, "%Y/%m/%d").timetuple()) if release_date else None
        except ValueError:
            raise ValueError(f"{version_string}: release_date is invalid.")
        self.release_date = release_date
        self.version = tuple(map(int, [major, minor, patch, pre_release_num]))
        self.version_string = version_string

    def next_major(self):
        '''
        if  self.minor is 0 and self.patch is 0:
            return SemanticVersion('.'.join(str(x) for x in [self.major, self.minor, self.patch]))
        else:
            return SemanticVersion('.'.join(str(x) for x in [self.major + 1, 0, 0]))
        '''
        if self.minor is 0 and self.patch is 0:
            return SemanticVersion('.'.join(str(x) for x in [self.major + 1, 0, 0]))
        elif self.minor is not 0 and self.patch is 0:
            return SemanticVersion('.'.join(str(x) for x in [self.major, self.minor + 1, 0]))
        else:
            return SemanticVersion('.'.join(str(x) for x in [self.major, self.minor, self.patch + 1]))

    def next_minor(self):
        if self.patch is not 0:
            return SemanticVersion('.'.join(str(x) for x in [self.major, self.minor, self.patch]))
        else:
            return SemanticVersion(
                '.'.join(str(x) for x in [self.major, self.minor + 1, 0]))

    def next_patch(self):
        if self.pre_release:
            return SemanticVersion('.'.join(str(x) for x in [self.major, self.minor, self.patch]))
        else:
            return SemanticVersion(
                '.'.join(str(x) for x in [self.major, self.minor, self.patch + 1]))

    def __str__(self):
        release_date = str(self.release_date) if self.release_date else 'N.A.'
        return self.version_string + ':' + release_date

    def _cmp(self, other):
        if not isinstance(other, SemanticVersion):
            raise ValueError(f'{other} is not a valid SemanticVersion.')

        if self.language==NPM_LANG and self.pre_release and other.pre_release:
            return base_cmp(self.version_string, other.version_string)

        # if release date is present, use release date
        if self.release_date and other.release_date:
            if self.release_date == other.release_date:
                return 0
            elif self.release_date < other.release_date:
                return -1
            else:
                return 1

        # compare main version number
        if self.version != other.version:
            if self.version < other.version:
                return -1
            else:
                return 1

        # compare pre release weight
        if self.pre_release_num != other.pre_release_num:
            if self.pre_release_num < other.pre_release_num:
                return -1
            else:
                return 1
        else:
            if self.pre_release == other.pre_release:
                return 0
            elif self.pre_release < other.pre_release:
                return -1
            else:
                return 1


class SpecItem(object):
    """A requirement specification."""

    KIND_ANY = '*'
    KIND_LT = '<'
    KIND_LTE = '<='
    KIND_EQUAL = '=='
    KIND_SHORTEQ = '='
    KIND_EMPTY = ''
    KIND_GTE = '>='
    KIND_GT = '>'
    KIND_NEQ = '!='
    KIND_CARET = '^'
    KIND_TILDE = '~'
    KIND_COMPATIBLE = '~='

    # Map a kind alias to its full version
    KIND_ALIASES = {
        KIND_SHORTEQ: KIND_EQUAL,
        KIND_EMPTY: KIND_EQUAL,
    }

    re_spec = re.compile(r'^(<|<=||=|==|>=|>|!=|\^|~|~=)(\d.*)$')

    def __init__(self, requirement_string, pre_release_weight=None, language=None, name=None):
        self.requirement_string = requirement_string
        self.language = language
        self.name = name
        self.pre_release_weight = pre_release_weight
        kind, spec = self.parse(requirement_string)
        self.kind = kind
        self.spec = spec

    def parse(self, requirement_string):
        if not requirement_string:
            raise ValueError(
                "Invalid empty requirement specification: %r" % requirement_string)

        # Special case: the 'any' version spec.
        if requirement_string == '*':
            return (self.KIND_ANY, '')

        match = self.re_spec.match(requirement_string)
        if not match:
            raise ValueError(
                "Invalid requirement specification: %r" % requirement_string)

        kind, version = match.groups()
        if kind is not '' and kind in self.KIND_ALIASES:
            kind = self.KIND_ALIASES[kind]

        spec = SemanticVersion(
            version, pre_release_weight=self.pre_release_weight)
        return (kind, spec)

    def match_alphabettically(self, version):
        if self.kind == self.KIND_LT:
            return version.version_string < self.spec.version_string
        elif self.kind == self.KIND_LTE:
            return version.version_string <= self.spec.version_string
        elif self.kind == self.KIND_EQUAL:
            return version.version_string == self.spec.version_string
        elif self.kind == self.KIND_GTE:
            return version.version_string >= self.spec.version_string
        elif self.kind == self.KIND_GT:
            return version.version_string > self.spec.version_string
        else:  # pragma: no cover
            raise ValueError('Unexpected match kind: %r, %s, %s' % (self.kind, self.name, self.requirement_string))

    def match(self, version):
        if self.kind == self.KIND_ANY:
            return True
        elif self.kind == self.KIND_NEQ:
            return version != self.spec
        else:
            if self.language == NPM_LANG and self.spec.pre_release and version.pre_release:
                #If a pre release tag of the spec exists, then return false if the version number of both are not same. Ex 3.0.0-alpha does not lie in >=2.0.0-rc,<3.0.0
                if self.spec.major != version.major or self.spec.minor != version.minor or self.spec.patch != version.patch:
                    return False
                #If version number is same, then compare lexicographically
                else:
                    return self.match_alphabettically(version)
            # elif self.language == NPM_LANG and not self.spec.pre_release and version.pre_release:
            #     return False
            else:
                if self.kind == self.KIND_LT:
                    return version < self.spec
                elif self.kind == self.KIND_LTE:
                    return version <= self.spec
                elif self.kind == self.KIND_EQUAL:
                    return version == self.spec
                elif self.kind == self.KIND_GTE:
                    return version >= self.spec
                elif self.kind == self.KIND_GT:
                    return version > self.spec

                elif self.kind == self.KIND_CARET:
                    if self.spec.major != 0:
                        upper = self.spec.next_major()
                    elif self.spec.minor != 0:
                        upper = self.spec.next_minor()
                    else:
                        upper = self.spec.next_patch()
                    return self.spec <= version < upper
                elif self.kind == self.KIND_TILDE:
                    return self.spec <= version < self.spec.next_minor()
                elif self.kind == self.KIND_COMPATIBLE:
                    if self.spec.patch is not None:
                        upper = self.spec.next_minor()
                    else:
                        upper = self.spec.next_major()
                    return self.spec <= version < upper
                else:  # pragma: no cover
                    raise ValueError('Unexpected match kind: %r, %s, %s' % (self.kind, self.name, self.requirement_string))

    def __str__(self):
        return '%s%s' % (self.kind, self.spec)

    def __repr__(self):
        return '<SpecItem: %s %r>' % (self.kind, self.spec)

    def __eq__(self, other):
        if not isinstance(other, SpecItem):
            return NotImplemented
        return self.kind == other.kind and self.spec == other.spec

    def __hash__(self):
        return hash((self.kind, self.spec))


class Spec(object):
    def __init__(self, *specs_strings, pre_release_weight=None, language=None, name=None):
        self.name = name
        self.pre_release_weight = pre_release_weight
        self.language = language
        subspecs = [self.parse(spec) for spec in specs_strings]
        self.specs = sum(subspecs, ())

    def parse(self, specs_string):
        self.spec_or = []
        # Split specs_string by || and ,
        spec_texts = re.split(",|\\|\\|", specs_string)
        if ('||' in specs_string):
            for list in specs_string.split("||"):
                spec_and = []
                for s in list.split(","):
                    spec_and.append(SpecItem(s, self.pre_release_weight, None, self.name))
                self.spec_or.append(spec_and)
        return tuple(SpecItem(spec_text, self.pre_release_weight, self.language, self.name) for spec_text in spec_texts)

    def match(self, version):
        if(self.language == 'npm'):
            # If no range is having pre-released tag, then return false if the input version is having prereleased tag
            if all(not specItem.spec.pre_release for specItem in self.specs) and version.pre_release:
                return False
        """Check whether a Version satisfies the Spec."""
        if (self.spec_or):
            return any(all(spec.match(version) for spec in spec_and) for spec_and in self.spec_or)
        return all(spec.match(version) for spec in self.specs)

    def filter(self, versions):
        """Filter an iterable of versions satisfying the Spec."""
        for version in versions:
            if self.match(version):
                yield version

    def select(self, versions):
        """Select the best compatible version among an iterable of options."""
        options = list(self.filter(versions))
        if options:
            return max(options)
        return None

    def __contains__(self, version):
        if isinstance(version, SemanticVersion):
            return self.match(version)
        return False

    def __iter__(self):
        return iter(self.specs)

    def __str__(self):
        return ','.join(str(spec) for spec in self.specs)

    def __repr__(self):
        return '<Spec: %r>' % (self.specs,)

    def __eq__(self, other):
        if not isinstance(other, Spec):
            return NotImplemented

        return set(self.specs) == set(other.specs)

    def __hash__(self):
        return hash(self.specs)


def compare(v1, v2, language=None):
    pre_release_weight = PRE_RELEASE_WEIGHTS.get(language)
    first_ver = SemanticVersion(v1, pre_release_weight=pre_release_weight)
    sec_ver = SemanticVersion(v2, pre_release_weight=pre_release_weight)
    #If language is npm, then use the npm prereleased weights instead of default list
    # If both have pre released tags, then compare alphabettically
    if language == NPM_LANG and first_ver.pre_release and sec_ver.pre_release:
        return base_cmp(first_ver.version_string, sec_ver.version_string)
    return base_cmp(SemanticVersion(v1), SemanticVersion(v2))


def match(spec, version):
    return Spec(spec).match(SemanticVersion(version))


def validate(version_string):
    """Validates a version string againt the SemVer specification."""
    try:
        SemanticVersion.parse(version_string)
        return True
    except ValueError:
        return False


def base_cmp(x, y):
    if x == y:
        return 0
    elif x > y:
        return 1
    elif x < y:
        return -1
    else:
        # Fix Py2's behavior: cmp(x, y) returns -1 for unorderable types
        return NotImplemented


def check_spec_close_match(version, spec):
    for spec_item in spec.specs:
        if spec_item.spec is not '' and spec_item.spec.major == version.major and spec_item.spec.minor == version.minor:
            return True
    return False


def check_version_in_criteria(criterias, version):
    ret = False

    # Get all specs that match the major, minor of current version
    matching_specs = list(filter(
        lambda x: check_spec_close_match(version, x), criterias))
    # If any matching spec has a lower and upper bound, treat with priority
    # i.e., sufficient to compare matching specs
    has_confident_spec = len(list(filter(
        lambda x: len(x.specs) == 2, matching_specs))) > 0
    compare_specs = matching_specs if has_confident_spec else criterias
    for spec in compare_specs:
        ret = ret or spec.match(version)
    return ret


def clean_version(version_string):
    """ Handle unclean versions in the db / from NVD
    """
    # If a single digit without any minor/patch, append '.0'
    if re.match('^(\d+)$', version_string):
        version_string += '.0'

    # Replace invalid tokens in the version with a '-'
    # TODO: confirm
    for token in REPLACE_TOKENS:
        version_string = version_string.replace(token, '-')
    return version_string


def normalize_version(version_string):
    """ Handle unclean NVD versions like 1.2.3.alpha vs 1.2.3-alpha
    """

    # Replace all non alphanumeric chars with '-'
    return ''.join(e.lower() if e.isalnum() else '-' for e in version_string)


def clean_ranges(version_ranges):
    """ Clean version number portion of every condition.
    Arguments:
        version_ranges {list} -- list of version range conditions
    Returns:
        [list] -- cleaned list of conditions
    """

    def clean_condition(cond):
        # Handling cases like ">= 1.1.0" by removing space to make it valid
        cond = cond.replace(" ", "")
        ops = ['>=', '<=', '>', '<']
        op = ''
        for operator in ops:
            if operator in cond:
                op = operator
                break
        return op + clean_version(re.sub(f'{op}|=', '', cond))

    clean_ranges = []

    def append_op(ver_range, op):
        if (op not in ver_range):
            ver_range = op + ver_range
        return ver_range

    def get_range_combo(range_str):
        splt = range_str.split(",")
        ranges = []
        n = 1
        first_ver = ''
        for st in splt:
            if (n % 2 == 0):
                ranges.append(first_ver + "," + st)
            first_ver = st
            n += 1
        return ranges

    def convert_bracket_ranges_into_std(range):
        first_element = range[0] if range else ''
        sec_element = range[1] if range else ''

        first_bracket = first_element[0] if first_element else ''
        sec_bracket = sec_element[-1] if sec_element else ''

        start_limit = first_element.replace(first_bracket, "")
        end_limit = sec_element.replace(sec_bracket, "")
        # Handling cases like (,1.0] or (,1.0)
        if (not start_limit and end_limit):

            if (sec_bracket == "]"):
                return "<=" + end_limit
            elif (sec_bracket == ")"):
                return "<" + end_limit
        # Handling cases like [1.0,) or (1.0,)
        elif (start_limit and not end_limit):
            if (first_bracket == "["):
                return ">=" + start_limit
            elif (first_bracket == "("):
                return ">" + start_limit
        # Handling cases like (1.0,2.0) or [1.0,2.0]
        elif (start_limit and end_limit):
            if (first_bracket == "[" and sec_bracket == "]"):
                return ">=" + start_limit + ",<=" + end_limit
            elif (first_bracket == "(" and sec_bracket == ")"):
                return ">" + start_limit + ",<" + end_limit
            elif (first_bracket == "[" and sec_bracket == ")"):
                return ">=" + start_limit + ",<" + end_limit
            elif (first_bracket == "(" and sec_bracket == "]"):
                return ">" + start_limit + ",<=" + end_limit

        return range

    # Split deps by ||
    # Convert each spec into a range with > / >= and/or < / <= or ~/^ or all_versions
    # Replace ^ and ~ with >/<
    def convert_into_std_range(range_str):
        """ Converts given input range to a standardized range
        """
        try:
            import re
            if not range_str:
                range_str = ''
            # Remove v if followed by a digit
            if re.match(r'[\s\S]*v\d+', range_str):
                range_str = range_str.replace('v', '')
            # Remove leading / trailing spaces
            range_str = range_str.strip()
            # Remove space between op and ver number
            range_str = re.sub(r'(?<=[><=~^])\s', '', range_str)
            # If ' - ' in string, it is a range, change format
            range_parts = range_str.split(' - ')
            if len(range_parts) == 2:
                # Handle cases like - ^3.0.0 - ^4.1.0
                if (range_parts[0][0] == "^" or range_parts[1][0] == "^"):
                    range_parts[0] = range_parts[0].replace("^", "")
                    range_str = '>=' + range_parts[0]
                    if (range_parts[1][0] == "^"):
                        range_str += f',<{int(range_parts[1][1]) + 1}.0.0'
                    else:
                        range_parts[1] = range_parts[1].replace("^", "")
                        range_str += ',<=' + range_parts[1]
                else:
                    if ('>=' not in range_parts[0]):
                        range_parts[0] = '>=' + range_parts[0]
                    if ('<=' not in range_parts[1]):
                        range_parts[1] = ',<=' + range_parts[1]

                    range_str = range_parts[0] + range_parts[1]

            # Replace && string with a ','
            range_str = range_str.replace(' && ', ',')
            # Replace ~>= string with ~
            range_str = range_str.replace('~>=', '~')
            # Replace ~> string with ~
            range_str = range_str.replace('~>', '~')
            # Replace any other space with a ','
            range_str = range_str.replace(' ', ',')
            # If 2 conditions are specified in the same range without a ','
            # add it
            pattern = re.compile(r'(?<=[\w\d])(?P<op>[><])')
            range_str = pattern.sub(r',\g<op>', range_str)
            # Replace => with >= and =< with <=
            range_str = range_str.replace('=<', '<=').replace('=>', '>=')
            # Remove = in the beginning
            range_str = re.sub('^=', '', range_str)
            # Remove extra = in the beginning in case there were two ==
            range_str = re.sub('^=', '', range_str)

            # Handle x, 0 and missing 0s in each part of the range
            range_parts = range_str.split(',')
            new_range_parts = []
            for part in range_parts:
                # Extract operator
                res = re.match(r'([><=~^*]*)(\d+)', part)
                value = part
                op = ''
                if res and res[1]:
                    op = res[1]
                    value = value.replace(op, '')

                # Handle x and * in versions
                res = re.match(r'(\d+)\.[x\*]', value)
                if res:
                    value = f'{"" if op else "^"}{res[1]}.0.0'
                else:
                    res = re.match(r'(\d+)\.(\d+)\.[x\*]', value)
                    if res:
                        value = f'{"" if op else "~"}{res[1]}.{res[2]}.0'
                # all_vers_list = ['*', 'x', 'x.x.x', '^*', '*.*.*', '^x', '', 'x.*', '>=x', '~x.x.x', '^x.x.x', 'x.x', '~*', '*.*', '^x.x']
                all_vers = re.fullmatch(r'([^a-zA-Z0-9]*[x.*]*[^a-zA-Z0-9]*)', value)
                if all_vers:
                    value = 'all_versions'
                # If only 1 or 2 digits in version, append .0
                res = re.match('(\d+)\.(\d+)\.(\d+)', value)
                if res:
                    pass
                else:
                    res = re.match('(\d+)\.(\d+)(.*)', value)
                    if res:
                        value = f'{res[1]}.{res[2]}.0{res[3] if res[3] else ""}'
                    else:
                        res = re.match('(\d+)(.*)', value)
                        if res:
                            if (op is "" or op is "^" or op is "~"):
                                new_range_parts.append(f'{"^"}{res[1]}.0.0{res[2] if res[2] else ""}')
                            else:
                                new_range_parts.append(f'{op}{res[1]}.0.0{res[2] if res[2] else ""}')
                            value = ''
                if value:
                    if (op == "^="):
                        op = "^"
                    if (op == "*"):
                        new_range_parts.append(f'{value}')
                    else:
                        new_range_parts.append(f'{op}{value}')

            # Put back the range and replace 2 or more dots with 1
            range_str = ','.join(new_range_parts)
            range_str = re.sub('\.{2,}', '.', range_str)
            # Convert into lower and/or upper bound if
            # ^ or ~ in string
            if range_str[0] == '~' or range_str[0] == '^':
                op = range_str[0]
                res = re.match('[\^~](\d+)\.(\d+)\.(\d+)', range_str)
                if res:
                    pre_rel_tag = range_str.replace(res.group(0), '')
                    range_str = f'>={res[1]}.{res[2]}.{res[3]}'
                    range_str += f'{pre_rel_tag}' if pre_rel_tag else ''
                    if op == '^':
                        range_str += f',<{int(res[1]) + 1}.0.0'
                    else:
                        range_str += f',<{res[1]}.{int(res[2]) + 1}.0'
        except Exception as e:
            print('Error: ', range_str, str(e))
        return range_str

    for ver_range in version_ranges:
        import re
        match_brackets = re.search(r"[\[\(\)\]]", ver_range)
        if (match_brackets):
            if ("," not in ver_range):
                ver_range = ver_range.replace("]", '')
                ver_range = ver_range.replace("[", '')
            else:
                sub_ranges = get_range_combo(ver_range)
                new_range_parts = []
                for range in sub_ranges:
                    new_range_parts.append(convert_bracket_ranges_into_std(range.split(",")))
                ver_range = '||'.join(new_range_parts)
        if ("||" in ver_range):
            conds = list(map(lambda x: clean_condition(convert_into_std_range(x)), ver_range.split('||')))
            clean_ranges.append('||'.join(conds))
        else:
            ver_range = convert_into_std_range(ver_range)
            conds = list(map(lambda x: clean_condition(x), ver_range.split(',')))
            clean_ranges.append(','.join(conds))

    return clean_ranges


def check_version_in_ranges(version, version_ranges, pre_release_weight=None, language=None):
    """ Check if the given version is in the given version ranges.
    Arguments:
        version {string} -- version number being checked
        version_ranges {string} -- version range conditions at least one
                                   of which should be satisfied for a match
    Keyword Arguments:
        pre_release_weight {dict} -- custom pre-release weight (default: {None})
    Returns:
        {bool} -- True if version in any of the ranges.
    """

    # Check if ALL_VERSIONS_KEY is one of the conditions, then
    # no further checks required
    match = len(list(filter(lambda x: x.lower() ==
                                      ALL_VERSIONS_KEY.lower(), version_ranges))) > 0

    if not match:
        try:
            exact_match_conds = list(
                filter(lambda x: not ('>' in x or '<' in x or '^' in x or (re.fullmatch(r'([^a-zA-Z0-9]*[x.*]*[^a-zA-Z0-9]*)', x)) or '~' in x or "*" in x),
                       version_ranges))
            range_conds = list(
                set(version_ranges).difference(set(exact_match_conds)))

            # Check exact matches first
            for cond in exact_match_conds:
                match = match or normalize_version(
                    cond) == normalize_version(version)

            if not match:
                # Check the ranges
                specs = []
                for condition in range_conds:
                    try:
                        specs.append(
                            Spec(condition, pre_release_weight=pre_release_weight, language=language))
                    except Exception as e:
                        print(f'Error: {e}')
                match = check_version_in_criteria(specs, SemanticVersion(
                    version, pre_release_weight=pre_release_weight))
        except Exception as e:
            print(f'Error: {e}')

    return match


def match_version_ranges(version_number, include_ranges, exclude_ranges=None, language=None):
    """ Check if version in include range. If yes, check if version in
        exclude range.
    Arguments:
        version_number {string} -- version number being checked
        include_ranges {list} -- version range conditions at least one of which
                                 should be satisfied for a match
    Keyword Arguments:
        exclude_ranges {list} -- version range conditions none of which should
                                 should be satisfied for a match (default: {None})
        language {string} -- language setting to use language-specific prefix
                             (default: {None})
    Returns:
        {bool} -- True if version in include ranges and not in exclude ranges.
    """

    if not exclude_ranges:
        exclude_ranges = []

    # If language is set, try to get pre-release weight
    pre_release_weight = None
    if language:
        pre_release_weight = PRE_RELEASE_WEIGHTS.get(language)

    # Clean the version number and all the versions in the ranges
    clean_version_number = clean_version(version_number)
    clean_include_ranges = clean_ranges(include_ranges)
    clean_exclude_ranges = clean_ranges(exclude_ranges)

    # Check include and exclude range
    match = check_version_in_ranges(
        clean_version_number, clean_include_ranges, pre_release_weight, language) and not check_version_in_ranges(
        clean_version_number, clean_exclude_ranges, pre_release_weight, language)

    return match


def sort_versions_asc(versions, language=None):
    semvers = []
    for v in versions:
        try:
            sv = SemanticVersion(v, language=language)
            semvers.append((v, sv))
        except:
            pass

    sorted_semvers = sorted(semvers, key=lambda x: x[1])
    sorted_vers = list(map(lambda x: (x[0], x[1].major, x[1].minor, x[1].patch,
                                      x[1].pre_release, x[1].pre_release_num),
                           sorted_semvers))
    return sorted_vers
