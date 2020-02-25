### How to build so file for golang
- After you have finished your code in go, please put ```//export {function name}``` on top of the function you want to expose,  e.g. ```semver_extract.go```.   
- run ```go build -buildmode=c-shared -o semver.so semver_extract.go```, then you will be able to find a so file in the same folder, and it can be copied to be other place to use.  
- As for the way to call so file in python, please refer to ```./repocloneref/extract_dependencies/test_semver.py```.