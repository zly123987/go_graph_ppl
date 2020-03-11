package main

import "C"
import (
	"fmt"
	"go/parser"
	"go/token"
	"io/ioutil"
	"strings"
)

func Ioutil(name string) string{
	if contents,err := ioutil.ReadFile(name);err == nil {
		//因为contents是[]byte类型，直接转换成string类型后会多一行空格,需要使用strings.Replace替换换行符
		result := string(contents)
		return result
	}
	return ""
}


//export Parse
func Parse(p * C.char) * C.char {
	fset := token.NewFileSet() // positions are relative to fset
	var path = C.GoString(p)
	src := Ioutil(path)

	// Parse src but stop after processing the imports.
	f, err := parser.ParseFile(fset, "", src, parser.ImportsOnly)
	if err != nil {
		fmt.Println(err)
		return C.CString("error")
	}
	var imports []string
	for _, s := range f.Imports {
		imports = append(imports, s.Path.Value)
	}
	// Print the imports from the file's AST.
	return C.CString(strings.Join(imports, "|"))
}
func main()  {
	fset := token.NewFileSet() // positions are relative to fset
	dir := "/home/lcwj3/go_repos/go_repo_sample/go_repos/Alg-G/errors.go"
	src := Ioutil(dir)
	var src_split = strings.Split(src, "\n")
	for _, s := range src_split{
		fmt.Println(s)
	}
	// Parse src but stop after processing the imports.
	f, err := parser.ParseFile(fset, "", src, parser.ImportsOnly)
	if err != nil {
		fmt.Println(err, dir)
	}
	var imports []string
	for _, s := range f.Imports {
		imports = append(imports, s.Path.Value)
	}
	fmt.Println(imports)
	// Print the imports from the file's AST.
	return
}