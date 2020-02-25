# version-util

reference:
[Requirements](https://scantist.atlassian.net/wiki/spaces/FS/pages/189431809/Library+Version+Parsing+Grammar)


input:
* Spec: >=x.y.z(,<x.y.z)?
> maximum two conditions allowed
 
> if version falls in exact major minor of one of the two condition, consider this Spec as mandatory
* library: library_id
* Version number will be in proper format: master.minor.patch.suffix, eg 5.0.3.alpha-1
    * master shall be integer
    * minor can be empty or integer
    * patch has a keyword list
    * suffix can be arbitrary string
    
> https://github.com/vdurmont/semver4j

output:
* library_version list: library_version_ids

Requirements:
* choose the closest criteria to process
    * eg. if criteria contains >=3.1,<3.10.2, then all 3.1.x will use this criteria
    * eg. if criteria contains >=v3.1,<v3.10.2 and <4.5, then all 3.1.x will use this criteria >=v3.1,<v3.10.2, others will check against <4.5
* priority: lib_ver release date > text input


> keeping in mind that "1" < "1.0" < "1.0.0"

> 1.0.5 > 1.0.5b7 or 2.0 (2345) > 2.0 (2100)

> For Java: "alpha" < "beta" < "milestone" < "rc" = "cr" < "snapshot" < "" = "final" = "ga" < "sp"
