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

import models

from models import (
    SemanticVersion,
    Spec,SpecItem,
    check_version_in_criteria,
    match_version_ranges,
    clean_ranges,
    compare,
    sort_versions_asc
)

from version_cleaning import clean_ver


def main():
    # this is a test
    version1 = SemanticVersion('1.0')
    version2 = SemanticVersion('5.3-alpha')
    version3 = SemanticVersion('5.3-alpha1')
    version4 = SemanticVersion('2.1.12')
    version5 = SemanticVersion('2.3.12-beta1021')
    version6 = SemanticVersion('4.4_build_4.4.000')
    version7 = SemanticVersion('11.6.5.1.1-20161213')
    version8 = SemanticVersion('3.0b1')
    version9 = SemanticVersion('2.0alpha1-20020829')
    version10 = SemanticVersion('0.94.5a-mapr')
    version11 = SemanticVersion('1.4.0rc3')
    version12 = SemanticVersion('1.2.rc1')

    print(f'{version1}: {version1.version}')
    print(f'{version2}: {version2.version}')
    print(f'{version3}: {version3.version}')
    print(f'{version4}: {version4.version}')
    print(f'{version5}: {version5.version}')
    print(f'{version6}: {version6.version}')
    print(f'{version7}: {version7.version}')
    print(f'{version8}: {version8.version}')
    print(f'{version9}: {version9.version}')
    print(f'{version10}: {version10.version}')
    print(f'{version11}: {version11.version}')
    print(f'{version12}: {version12.version}')

    # Begin tests
    print (" Begin Spec Tests ...")
    s = Spec('>=0.1.1')  # At least 0.1.1
    assert s.match(version2)==True
    s2 = Spec('>=2.1.1,<2.3.0')
    assert s2.match(version5)==False
    assert len(s2.specs)==2
    # Match all versions
    s3 = Spec('*')
    assert s3.match(version5)==True

    result = check_version_in_criteria([s, s2], version5)
    assert result==False

    # Tests for match_version_ranges
    assert match_version_ranges('1.3.3', ['<2.0.0,>1.0.0'])==True # True
    assert match_version_ranges('1.3.3', ['<2.0.0,>1.0.0'], ['>1.5.0'])==True  # True
    assert match_version_ranges('1.3.3', ['<2.0.0,>1.0.0'], ['>1.3.0'])==False  # False
    assert match_version_ranges('1.3.3b', ['>1.3.3'])==False  # False
    assert match_version_ranges('1.3.3b', ['>1.3.3'], language='c')==True # True
    # Multiple version specs for the same major+minor versions
    assert match_version_ranges('1.0.1d', ['>=1.0.1a', '>=1.0.2,<1.0.2h'], language='c')==True # True
    assert match_version_ranges('1.2.3', ['>=1.2.5,<1.2.8', '>=0.5.0'])==False  # False
    # Uses exact match for non standard version spec
    # True, prints exception for invalid version string
    print ("Test Exception")
    assert match_version_ranges('version_1_3_3', ['version_1_3_3', 'version_1_4_4'])==True
    # Fix unclean versions in db
    assert match_version_ranges('1.2####alpha', ['<1.3'])==True # True
    assert match_version_ranges('1', ['<1.3'])==True  # True
    # Test error handling for unclean versions
    # Prints exception for invalid version string in range
    print ("Test Exception")
    assert match_version_ranges('1.2', ['<1.3', '>4.2:alpha'])==True  # True
    # Prints exception for invalid version number
    print ("Test Exception")
    assert match_version_ranges('4.2:beta', ['<1.3', '>4.2-alpha'])==False # False

    # Version cleaning tests
    assert clean_ver('2_7')=='2.7.0' # True
    assert clean_ver('2.7Alpha1')=='2.7.0-alpha1'  # True
    assert clean_ver('.7')=='0.7.0'  # True

    # Match Version Ranges
    assert match_version_ranges("4.9.0", [">4.8.0"])==True #True
    assert match_version_ranges("4.8.0", [">= 4.8.0"])==True #True
    assert match_version_ranges("5.1.0", [">=4.8.0"])==True #True
    assert match_version_ranges("4.7.0", ["<4.8.0"])==True #True
    assert match_version_ranges("4.6.0", ["<=4.8.0"])==True #True
    assert match_version_ranges("4.8.0", ["<=4.8.0"])==True #True
    assert match_version_ranges("0.1.0", [">1.0.2 <=2.3.4"])==False #False
    assert match_version_ranges("1.1.0", [">1.0.2 <=2.3.4"])==True #True
    assert match_version_ranges("1.1.0", ["1.0.0 - 2.3.1"])==True #True
    assert match_version_ranges("3.0.1", ["<1.0.0 || >=2.3.1"])==True #True

    print(" Testing ranges with 'v' in first or second postion followed by version")
    assert match_version_ranges("4.0.0", ["~v4"])==True #True
    assert match_version_ranges("3.0.0", ["^v4.0.0"])==False #False

    assert match_version_ranges("0.0.2", ["^0.0.2"])==True #True
    assert match_version_ranges("3.1.1", ["^3.1.1"])==True  # True
    assert match_version_ranges("1.0.2", ["~0.15.7"])==False #False
    assert match_version_ranges("1.1.0", ["~1.0.0"])==False # False

    print(" Testing range containing x with operator in front ")
    assert match_version_ranges("2.3.1", ["~2.3.x"])==True # True
    assert match_version_ranges("2.4.0", ["~2.3.x"])==False # False
    assert match_version_ranges("2.4.0", ["^2.3.x"])==True #True
    assert match_version_ranges("3.0.0", ["^2.3.x"])==False #False

    print(" Testing range containing only x with no operator in front ")
    assert match_version_ranges("1.1.1", ["1.1.x"])==True #True
    assert match_version_ranges("1.2.1", ["1.x.x"])==True  # True
    assert match_version_ranges("1.2.1", ["1.x"])==True # True
    assert match_version_ranges("2.2.1", ["1.x.x"])==False  # False
    assert match_version_ranges("2.2.1", ["1.x"])==False  # False

    print(" Testing range containing * with operator in front ")
    assert match_version_ranges("2.3.1", ["~2.3.*"])==True #True
    assert match_version_ranges("2.4.0", ["~2.3.*"])==False #False
    assert match_version_ranges("2.4.0", ["^2.3.*"])==True #True
    assert match_version_ranges("3.0.0", ["^2.3.*"])==False #False

    print(" Testing range containing only * with no operator in front ")
    assert match_version_ranges("1.1.1", ["1.1.*"])==True #True
    assert match_version_ranges("1.2.1", ["1.*.*"])==True # True
    assert match_version_ranges("1.2.1", ["1.*"])==True # True
    assert match_version_ranges("2.2.1", ["1.*.*"])==False # False
    assert match_version_ranges("2.2.1", ["1.*"])==False  # False

    print(" Testing range with no minor and patch ")
    assert match_version_ranges("1.2.0", ["1"])==True  # True
    assert match_version_ranges("1.2.1", ["^1"])==True  # True
    assert match_version_ranges("1.2.1", ["~1"])==True  # True
    assert match_version_ranges("2.0.0", ["^1"])==False  # False

    print(" Testing range containing all the versions ")
    assert match_version_ranges("4.6.0", ["*"])==True #True
    assert match_version_ranges("5.6.0", [""])==True #True
    assert match_version_ranges("5.6.0", ["^x"])==True  # True
    assert match_version_ranges("5.6.0", ["*.*.*"])==True  # True
    assert match_version_ranges("5.6.0", ["^*"])==True # True
    assert match_version_ranges("1.2.0", ["x.x.x"])==True # True
    assert match_version_ranges("1.2.0", ["x.*"])==True # True
    assert match_version_ranges("1.2.0", ["x.x"])==True  # True
    assert match_version_ranges("1.2.0", ["^x.x.x"])==True  # True
    assert match_version_ranges("1.2.0", ["~*"])==True  # True
    assert match_version_ranges("1.2.0", ["*.*"])==True  # True

    print(" Testing range containing multiple || and , ")
    assert match_version_ranges("1.8.0", [">=1.8.0,<2.0.0||>=2.1.0,<3.0.0"])==True #True
    assert match_version_ranges("3.1.0", [">=1.8.0,<2.0.0||>=2.1.0,<3.0.0"])==False #False
    assert match_version_ranges("2.2.0", [">=1.8.0,<2.0.0||>=2.1.0,<3.0.0"])==True #True

    print(" Testing range containing multiple || and , with no patch version specified ")
    assert match_version_ranges("1.2.0", [">=2.3 || >=1.2,<2"])==True #True

    print(" Testing range containing && ")
    assert match_version_ranges("1.2.0", [">=0.7.25 && <4.0.0"])==True # True
    assert match_version_ranges("4.2.0", [">=0.7.25 && <4.0.0"])==False  # False

    print(" Testing ranges containing - in between with operator in range parts ")
    assert match_version_ranges("4.2.0", ["^3.0.0 - ^4.1.0"])==True  # True
    assert match_version_ranges("2.2.0", ["^3.0.0 - 4.1.0"])==False # False
    assert match_version_ranges("3.2.0", ["3.0.0 - ^4.1.0"])==True  # True

    assert match_version_ranges("4.1.0", ["*4.1.0"])==True  # True
    assert match_version_ranges("4.2.0", ["*4.1.0"])==False  # False

    assert match_version_ranges("1.9.2", [">=1.9.1 - 1.9.7"])==True  # True

    print(" Testing ranges containing ~>= in front ")
    assert match_version_ranges("9.0.4", ["~>=9.0.3"])==True  # True
    assert match_version_ranges("9.1.2", ["~>=9.0.3"])==False  # False

    print(" Testing ranges containing ^= in front ")
    assert match_version_ranges("6.2.4", ["^=6.0.3"])==True  # True
    assert match_version_ranges("7.1.2", ["^=6.0.3"])==False  # False

    print(" Testing version cleaning ", clean_ver("1.4.0.SNAPSHOT"))
    assert clean_ver("1.4.0.SNAPSHOT") == "1.4.0-snapshot"
    assert clean_ver("1.4.0.RC") == "1.4.0-rc"
    assert clean_ver("1.4.0.RC1") == "1.4.0-rc1"
    assert clean_ver("1.4.0.RELEASE") == "1.4.0-release"
    assert clean_ver("1.0.0.cr") == "1.0.0-cr"
    assert clean_ver("1.0.0.b1", 'maven') == "1.0.0-b1"
    assert clean_ver("1.0.0.SEC", 'maven') == "1.0.0-sec"
    assert clean_ver("1.4.0.m1", 'maven') == "1.4.0-m1"

    print(" Testing range cleaning and matching version in range with official pre-released tags ")
    assert clean_ranges(["^2.0.0-rc.17"]) == ['>=2.0.0-rc.17,<3.0.0']
    assert clean_ranges(["~2.0.0-rc.17"]) == ['>=2.0.0-rc.17,<2.1.0']

    assert match_version_ranges("3.0.0-rc.17", ["^2.0.0-rc.17"], language="npm") == False
    assert match_version_ranges("2.0.0-rc.17", ["^2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("2.0.0-alpha.17", ["^2.0.0-rc.17"], language="npm") == False
    assert match_version_ranges("2.0.0-rc.18", ["^2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("2.0.0-rc.16", ["^2.0.0-rc.17"], language="npm") == False
    assert match_version_ranges("2.0.0", ["^2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("3.0.0", ["^2.0.0-rc.17"], language="npm") == False

    print(" Testing range cleaning and matching version in range with non-official pre-released tags ")
    assert clean_ranges(["^2.0.0-z.17"]) == ['>=2.0.0-z.17,<3.0.0']
    assert clean_ranges(["~2.0.0-a.17"]) == ['>=2.0.0-a.17,<2.1.0']
    assert match_version_ranges("3.0.0-z.17", ["^2.0.0-a.17"], language="npm") == False
    assert match_version_ranges("2.0.0-z.17", ["^2.0.0-a.17"], language="npm") == True
    assert match_version_ranges("2.0.0-m.17", ["^2.0.0-r.17"], language="npm") == False
    assert match_version_ranges("2.0.0", ["^2.0.0-z.17"], language="npm") == True #Testing with released version
    assert match_version_ranges("3.0.0", ["^2.0.0-z.17"], language="npm") == False #Testing with released version
    assert match_version_ranges("4.0.0", [">=2.0.0-z.17,<5.0.0"], language="npm") == True
    assert match_version_ranges("2.0.0-rc.17", ["^2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("2.1.0-rc.17", ["~2.0.0-rc.17"], language="npm") == False
    assert match_version_ranges("2.0.0-rc.17", ["~2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("2.0.0-rc.18", ["~2.0.0-rc.17"], language="npm") == True
    assert match_version_ranges("2.1.0-alpha", ["~2.0.0-rc.17"], language="npm") == False
    assert match_version_ranges('3.0.0-cee', ['^2.4.1'], language='npm') == False
    assert match_version_ranges('2.5.0-cee', ['~2.4.1'], language='npm') == False
    assert match_version_ranges('5.0.0-a', ['>=2.0.0 <5.0.0-rc'], language='npm') == True
    assert match_version_ranges('2.0.0-a', ['>=2.0.0 <5.0.0-rc'], language='npm') == False
    assert match_version_ranges('3.0.0-a', ['>=2.0.0 <5.0.0-rc'], language='npm') == False
    assert match_version_ranges('5.0.0-alpha.1', ['^4.14.1'], language='npm') == False

    print(" Testing comparison between prereleased versions and prereleased with released versions")
    assert compare("1.2.0-z", "1.2.0-s", language='npm') == True
    assert compare("1.2.0", "1.2.0-rc", language="npm") == True
    assert compare("1.2.0-rc", "1.2.0-alpha", language="npm") == True
    assert compare("1.2.0-rc.18", "1.2.0-rc.17", language="npm") == True
    assert compare("1.2.0-rc", "1.2.0-final", language="npm") == True

    print(" Testing comparison between released versions ")
    assert compare("2.2.0", "1.2.0", language='npm') == True
    assert compare("1.2.0.2", "1.2.0.1", language='npm') == True
    assert compare("1.2.0.2", "1.2.0.1", language='npm') == True

    print(" Testing sorting of versions(asc) having both prereleased and released versions ")
    print(sort_versions_asc(["1.2.0-final", "1.2.0-rc"], language='npm'))
    print(sort_versions_asc(["1.2.0-final.17", "1.2.0-final.16", "1.2.0-final.1"], language='npm'))
    print(sort_versions_asc(["1.2.0", "1.2.0-rc", "2.0.0", "2.0.0-z", "2.0.0-f", "2.0.0-f.2", "2.0.0-f.1"], language='npm'))
    print(sort_versions_asc(["1.2.0", "1.2.0.1", "2.0.0.1", "2.0.0", "3.0.0"], language="npm"))

if __name__ == '__main__':
    main()
