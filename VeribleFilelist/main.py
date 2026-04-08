# =============================================================
# @Author: zhangshen
# @Date: 2025-03-26 20:55:37
# @LastEditors: zhangshen
# @LastEditTime: 2025-05-23 17:33:18
# @Description: 
# @Created by RICL of ShanghaiTech SIST
# @FilePath: /TSNN-HDL/tool/VeribleFilelist/main.py
# =============================================================
import argparse
import sys
from database import Database
import re

# path_list = [ "../../src", "../../lib/CustomLibrary/src", "../../lib/ThirdLibrary"] 
# define_prefix = "`define USE_VCS_SIMULATION"
defines = {"USE_VCS_SIMULATION": ""}

def parse_vcs_defines(defines_str):
    defines = {}
    pattern = r'\+define\+(\w+)(?:=\\"([^\\"]*)\\")?'
    for match in re.finditer(pattern, defines_str):
        define_name = match.group(1)
        define_value = match.group(2) if match.group(2) is not None else ""
        defines[define_name] = define_value
    return defines

def parse_arguments():
    parser = argparse.ArgumentParser(description="This is a toool for generating the filelist for vcs simulation.")
    parser.add_argument(
        '-t', '--topmodule',
        type=str,
        required=False,
        help="The top module of the design."
    )
    parser.add_argument(
        '-c', '--clean-filelist',
        required=False,
        action="store_true",
        help="Clean fielist."
    )
    parser.add_argument(
        '-b', '--build-database',
        required=False,
        action="store_true",
        help="Clean fielist."
    )
    parser.add_argument(
        '-p', '--path-save',
        type=str,
        required=False,
        help="Save Path. Default is current working directory."
    )
    parser.add_argument(
        '-s', '--search-paths',
        type=str,
        nargs='+',
        required=True,
        help="List of paths to search for source files."
    )
    parser.add_argument(
        '-d', '--defines',
        type=str,
        required=False,
        help="List of defines."
    )
    parser.add_argument(
        '--absolute-path',
        required=False,
        action="store_true",
        help="Use absolute paths in filelist instead of relative paths."
    )
    args = parser.parse_args()
    if args.defines is not None:
        new_defines = parse_vcs_defines(args.defines)
        defines.update(new_defines)
    print(defines)
    return args

def main(args):
    if args.topmodule is None and args.clean_filelist is None:
        print("Please specify the top module or clean filelist.")
        sys.exit(1)

    if args.clean_filelist is not None or args.topmodule is not None or args.build_database is not None:
        db = Database(args.search_paths, defines)

    if args.topmodule is not None:
        db.update_conditional_modules(args.topmodule)
        # 根据 --absolute-path 参数决定是否使用相对路径
        use_relative_path = not args.absolute_path
        db.generate_filelist_file(args.topmodule, args.path_save, use_relative_path=use_relative_path)

    if args.clean_filelist :
        db.clean_filelist_file(args.path_save)

    if args.build_database:
        db.build_database()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)