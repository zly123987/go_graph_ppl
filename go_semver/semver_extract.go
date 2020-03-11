package main
import (
	"golang.org/x/mod/semver"
	"C"
	"sort"
	"strings"
	"fmt"
)

type Version struct {
	version_number string
}
func NewVersion(ver string) *Version{
	var version = new(Version)
	version.version_number = ver
	return version
}
func (p *Version) String() string {
	return fmt.Sprintf("( %s )", p.version_number)
}

type VersionList []*Version


func (list VersionList) Len() int {
	return len(list)
}

func (list VersionList) Less(i, j int) bool {
	if compareVersion(C.CString(list[i].version_number), C.CString(list[j].version_number)) < 0 {
		return true
	} else {
		return false
	}
}

func (list VersionList) Swap(i, j int) {
	var temp *Version = list[i]
	list[i] = list[j]
	list[j] = temp
}

//export getMajor
func getMajor(in * C.char) *C.char{
	var out = semver.Major(C.GoString(in))
	return C.CString(out)
}
//export getMajorMinor
func getMajorMinor(in * C.char) *C.char{
	var out = semver.MajorMinor(C.GoString(in))
	return C.CString(out)
}

//export compareVersion
func compareVersion(v1, v2 * C.char) int{
	var res = semver.Compare(C.GoString(v1), C.GoString(v2))
	return res
}

//export isValidVersion
func isValidVersion(ver * C.char) bool {
	var isValid = semver.IsValid(C.GoString(ver))
	return isValid
}


//export sortVers
func sortVers(vers * C.char) * C.char{
	// input:
	// 		verlist: a list structured as 'v1|v3|v2'
	// output:
	//		sorted_list: a list structured as 'v1|v2|v3'
	var ver_list_string = C.GoString(vers)
	var verlist = strings.Split(ver_list_string, "|")
	var versionlist VersionList
	for _, vn := range verlist {
		var version = Version{vn}
		versionlist = append(versionlist, &version)
	}
	sort.Sort(versionlist)
	var sorted_list []string
	for _, vn := range versionlist {
		sorted_list = append(sorted_list, vn.version_number)
	}
	return C.CString(strings.Join(sorted_list, "|"))
}


func main() {
	//var tests = []struct {
	//	in  string
	//	out string
	//}{
	//	{"bad", ""},
	//	{"v1-alpha.beta.gamma", ""},
	//	{"v1-pre", ""},
	//	{"v1+meta", ""},
	//	{"v1-pre+meta", ""},
	//	{"v1.2-pre", ""},
	//	{"v1.2+meta", ""},
	//	{"v1.2-pre+meta", ""},
	//	{"v1.0.0-alpha", "v1.0.0-alpha"},
	//	{"v1.0.0-alpha.1", "v1.0.0-alpha.1"},
	//	{"v1.0.0-alpha.beta", "v1.0.0-alpha.beta"},
	//	{"v1.0.0-beta", "v1.0.0-beta"},
	//	{"v1.0.0-beta.2", "v1.0.0-beta.2"},
	//	{"v1.0.0-beta.11", "v1.0.0-beta.11"},
	//	{"v1.0.0-rc.1", "v1.0.0-rc.1"},
	//	{"v1", "v1.0.0"},
	//	{"v1.0", "v1.0.0"},
	//	{"v1.0.0", "v1.0.0"},
	//	{"v1.2", "v1.2.0"},
	//	{"v1.2.0", "v1.2.0"},
	//	{"v1.2.3-456", "v1.2.3-456"},
	//	{"v1.2.3-456.789", "v1.2.3-456.789"},
	//	{"v1.2.3-456-789", "v1.2.3-456-789"},
	//	{"v1.2.3-456a", "v1.2.3-456a"},
	//	{"v1.2.3-pre", "v1.2.3-pre"},
	//	{"v1.2.3-pre+meta", "v1.2.3-pre"},
	//	{"v1.2.3-pre.1", "v1.2.3-pre.1"},
	//	{"v1.2.3-zzz", "v1.2.3-zzz"},
	//	{"v1.2.3", "v1.2.3"},
	//	{"v1.2.3+meta", "v1.2.3"},
	//	{"v1.2.3+meta-pre", "v1.2.3"},
	//	{"v1.2.3+meta-pre.sha.256a", "v1.2.3"},
	//}
	//in := "v1.2.3+meta-pre.sha.256a"
	//out := semver.MajorMinor(in)
	//want := ""
	//if i := strings.Index(out, "."); i >= 0 {
	//	want = out[:i]
	//}
	//if out != want {
	//	fmt.Println(in, out, want)
	//}

	//
	//var c = sortVers([]string{"v1.0.0", "v1.1.0", "v1.0.1", "v1.0.1-nvcnnvskn"})
	//fmt.Println(c)
}




