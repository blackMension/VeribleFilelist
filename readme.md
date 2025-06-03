<!--
 * @Author: zhangshen
 * @Date: 2025-06-03 16:08:14
 * @LastEditors: zhangshen
 * @LastEditTime: 2025-06-03 16:28:36
 * @Description: 
 * Created by RICL of ShanghaiTech SIST
 * @FilePath: /SNN/Tools/VeribleVCSFilelist/readme.md
-->

# VeribleVCSFilelist

## Usage

`VeribleVCSFilelist` can free you from manually creating the filelist files for VCS.

`VeribleVCSFilelist` can automatically scan the directories and automatically generate the filelist used in VCS simulation. 
`VeribleVCSFilelist` support the function of processing the cases of `macro`, `ifdef`, and `ifndef`.

## Guide

### Download the necessary Veribile binary files
```
cd VeribleFilelist
./initial.sh
cd ..
```

### Install the necessary python package
```
pip install anytree
```

### Try the VeribleVCSFilelist
```
cd VCS
make topmodule="count_ones_tb" compile run
```

## Requirements

```
pip install anytree
```
