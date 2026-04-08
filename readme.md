<!--
 * @Author: zhangshen
 * @Date: 2025-06-03 16:08:14
 * @LastEditors: zhangshen
 * @LastEditTime: 2026-04-08 08:55:00
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
```bash
cd VeribleFilelist
./initial.sh
cd ..
```

### Install the necessary python package
```bash
pip install anytree
```

### Basic Usage

Generate filelist with relative paths (default, saved to current working directory):
```bash
python ./VeribleVCSFilelist/VeribleFilelist/main.py -t MktApp -s ./src
```

Generate filelist with absolute paths:
```bash
python ./VeribleVCSFilelist/VeribleFilelist/main.py -t MktApp -s ./src --absolute-path
```

Generate filelist to a specific directory:
```bash
# Relative paths
python ./VeribleVCSFilelist/VeribleFilelist/main.py -t MktApp -s ./src -p ./verif/sim

# Absolute paths
python ./VeribleVCSFilelist/VeribleFilelist/main.py -t MktApp -s ./src -p ./verif/sim --absolute-path
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-t`, `--topmodule` | Top module name |
| `-s`, `--search-paths` | Directories to search for source files (required) |
| `-p`, `--path-save` | Output directory for filelist (default: current working directory) |
| `-d`, `--defines` | Macro defines (e.g., `+define+NAME1+define+NAME2=value`) |
| `-b`, `--build-database` | Force rebuild the database |
| `-c`, `--clean-filelist` | Clean existing filelist files |
| `--absolute-path` | Use absolute paths instead of relative paths (default: relative) |

### Filelist Output Format

**Relative paths** (when filelist is in `./verif/sim/`):
```
+incdir+../../src
../../src/FdkPackage.sv
../../src/MktPackage.sv
...
```

**Absolute paths**:
```
+incdir+/Volumes/SSD/Workstation/jiukun-mkt/src
/Volumes/SSD/Workstation/jiukun-mkt/src/FdkPackage.sv
...
```

### Try the VeribleVCSFilelist
```bash
cd VCS
make topmodule="count_ones_tb" compile run
```

## Requirements

```bash
pip install anytree
```

## Features

- Automatically scans directories for SystemVerilog/Verilog source files
- Handles `include` files (`.h`, `.svh`, `.vh`)
- Processes `macro`, `ifdef`, and `ifndef` directives
- Generates filelist with relative or absolute paths
- Supports multiple search paths
- Caches module dependencies for faster subsequent runs
