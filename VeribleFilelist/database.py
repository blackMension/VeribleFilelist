# =============================================================
# @Author: ZhangShen
# @Date: 2025-01-10 09:34:36
# @LastEditors: zhangshen
# @LastEditTime: 2025-06-03 15:56:04
# @Description: 
# @Created by RICL of ShanghaiTech SIST
# @FilePath: /TSNN-HDL/tool/VeribleFilelist/database.py
# =============================================================

import os
import pickle
import inspect
import traceback
from collections import deque
from parse import *

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

PATH_CACHE = os.path.abspath(os.path.join(current_dir_path, "./cache"))
PATH_FILELIST = os.path.abspath(os.path.join(current_dir_path, "../VCS/filelist"))
PATH_VERIBLE_VERILOG_SYNTAX = os.path.abspath(os.path.join(current_dir_path, "./verible/bin/verible-verilog-syntax"))

assert os.path.exists(PATH_VERIBLE_VERILOG_SYNTAX), "verible-verilog-syntax not found"
parser = verible_verilog_syntax.VeribleVerilogSyntax(executable=PATH_VERIBLE_VERILOG_SYNTAX)

def check_directory( path_dir ):
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def save_data_to_cache(data, path=""):
    with open(path, "wb") as f:
        pickle.dump(data, f)

def load_data_from_cache(path=""):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data

def get_filelist( directory_list:list ):
    path_modules, path_testbenches, path_includes = [], [], []
    for p in directory_list:
        modules, testbenches, includes = traverse_directory(p)
        path_modules += modules
        path_testbenches += testbenches
        path_includes += includes
    return path_modules, path_testbenches, path_includes

def get_filelist_time( path_list ):
    dict_modification_time = {}
    for path in path_list:
        dict_modification_time[path] = os.path.getmtime(path[1])
    return dict_modification_time

def sort_files_by_time( dict_time_new, dict_time_old ):
    new_files, modified_files, deleted_files = [], [], []
    for key, val in dict_time_new.items():
        if key not in dict_time_old:
            new_files.append(key)
        elif val != dict_time_old[key]:
            modified_files.append(key)
    for key in dict_time_old:
        if key not in dict_time_new:
            deleted_files.append(key)
    return new_files, modified_files, deleted_files

def get_modules_data( path_modules, defines={} ):
    dict_file_module = {}       # key: file, value: modules
    dict_module_file = {}       # key: module, value: file
    dict_module_references = {} # key: module, value: references
    dict_module_includes = {}   # key: module, value: incldue header files
    set_module_conditionals = set({}) # key: module, value: conditionals
    
    for the_module in path_modules:
        the_file_fullname = the_module[0]
        the_path = the_module[1]

        if the_file_fullname.endswith(".v"):
            the_module_type = "verilog"
            the_module_file_shortname = the_file_fullname.replace(".v", "")
        elif the_file_fullname.endswith(".sv"):
            the_module_type = "systemverilog"
            the_module_file_shortname = the_file_fullname.replace(".sv", "")
        else:
            raise Exception("Unknown file type: {}".format(the_file_fullname))

        # todo : the macro should be save to the cache for checking whether update the filelist
        parsed_data, include_conditionals = process_module_with_define( the_path, defines, parser )

        try:
            parsed_infos = get_modules_info( parsed_data )
        except Exception as e:
            print("Error parsing file: {}".format(the_file_fullname))
            print(f"ERROR: {e}")
            print("\nDetailed traceback:")
            traceback.print_exc()
            for error in parsed_data.errors:
                print(f"ERROR: '{the_path}', line {error.line}")
            exit(1)

        module_number = len(parsed_infos)
        if module_number == 0:
            print("No module found in file:{:30}\t[{}]".format(the_file_fullname, the_path))
        elif module_number > 1:
            print("More than one module found in file: {}\t[{}]".format(the_file_fullname, the_path))

        module_name_list = [ info['name'] for info in parsed_infos ]
        module_reference_list = [ info['reference'] for info in parsed_infos ]
        module_include_list = [ info['includes'] for info in parsed_infos ]

        dict_file_module[the_path] = module_name_list
        for module_name in module_name_list:
            dict_module_file[module_name] = the_path
        for module_name, module_reference in zip(module_name_list, module_reference_list):
            dict_module_references[module_name] = module_reference
        for module_name, module_include in zip(module_name_list, module_include_list):
            dict_module_includes[module_name] = module_include

        if include_conditionals:
            set_module_conditionals.update(module_name_list)

    return dict_file_module, dict_module_file, dict_module_references, dict_module_includes, set_module_conditionals

def check_valid_database():
    if not os.path.exists(PATH_CACHE):
        return False
    if not os.path.exists(os.path.join(PATH_CACHE, "dict_modification_time.pkl")):
        return False
    if not os.path.exists(os.path.join(PATH_CACHE, "dict_file_module.pkl")):
        return False
    if not os.path.exists(os.path.join(PATH_CACHE, "dict_module_file.pkl")):
        return False
    if not os.path.exists(os.path.join(PATH_CACHE, "dict_module_references.pkl")):
        return False
    return True

def create_database( path_list,  defines={} ):
    path_modules, path_testbenches, path_includes = get_filelist( path_list )
    path_all = path_modules + path_testbenches + path_includes
    dict_modification_time = get_filelist_time(path_all)
    dict_include_dir = {path[0]: path[2] for path in path_includes}
    
    dict_file_module, dict_module_file, dict_module_references, dict_module_includes, set_module_conditionals = get_modules_data(path_modules, defines=defines)
    dict_file_testbench, dict_testbench_file, dict_testbench_references, dict_testbench_includes, set_testbench_conditionals = get_modules_data(path_testbenches, defines=defines)
    
    dict_file_module.update(dict_file_testbench)
    dict_module_file.update(dict_testbench_file)
    dict_module_references.update(dict_testbench_references)
    dict_module_includes.update(dict_testbench_includes)
    set_module_conditionals.update(set_testbench_conditionals)

    check_directory(PATH_CACHE)
    save_data_to_cache(dict_modification_time, os.path.join(PATH_CACHE, "dict_modification_time.pkl"))
    save_data_to_cache(dict_file_module, os.path.join(PATH_CACHE, "dict_file_module.pkl"))
    save_data_to_cache(dict_module_file, os.path.join(PATH_CACHE, "dict_module_file.pkl"))
    save_data_to_cache(dict_module_references, os.path.join(PATH_CACHE, "dict_module_references.pkl"))
    save_data_to_cache(dict_module_includes, os.path.join(PATH_CACHE, "dict_module_includes.pkl"))
    save_data_to_cache(dict_include_dir, os.path.join(PATH_CACHE, "dict_include_dir.pkl"))
    save_data_to_cache(set_module_conditionals, os.path.join(PATH_CACHE, "set_module_conditionals.pkl"))
    print("Database created successfully")

def load_database():
    assert os.path.exists(PATH_CACHE), "Cache not found"
    dict_modification_time = load_data_from_cache(os.path.join(PATH_CACHE, "dict_modification_time.pkl"))
    dict_file_module = load_data_from_cache(os.path.join(PATH_CACHE, "dict_file_module.pkl"))
    dict_module_file = load_data_from_cache(os.path.join(PATH_CACHE, "dict_module_file.pkl"))
    dict_module_references = load_data_from_cache(os.path.join(PATH_CACHE, "dict_module_references.pkl"))
    dict_module_includes = load_data_from_cache(os.path.join(PATH_CACHE, "dict_module_includes.pkl"))
    dict_include_dir = load_data_from_cache(os.path.join(PATH_CACHE, "dict_include_dir.pkl"))
    set_module_conditionals = load_data_from_cache(os.path.join(PATH_CACHE, "set_module_conditionals.pkl"))
    return dict_modification_time, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir, set_module_conditionals

def save_database( dict_modification_time, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir ):
    check_directory(PATH_CACHE)
    save_data_to_cache(dict_modification_time, os.path.join(PATH_CACHE, "dict_modification_time.pkl"))
    save_data_to_cache(dict_file_module, os.path.join(PATH_CACHE, "dict_file_module.pkl"))
    save_data_to_cache(dict_module_file, os.path.join(PATH_CACHE, "dict_module_file.pkl"))
    save_data_to_cache(dict_module_references, os.path.join(PATH_CACHE, "dict_module_references.pkl"))
    save_data_to_cache(dict_module_includes, os.path.join(PATH_CACHE, "dict_module_includes.pkl"))
    save_data_to_cache(dict_include_dir, os.path.join(PATH_CACHE, "dict_include_dir.pkl"))

def update_database( path_list, defines={} ):
    dict_modification_time, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir, set_module_conditionals = load_database()

    def update_dict_data( dict_tuple ):
        dict_file_module_new, dict_module_file_new, dict_module_references_new, dict_module_includes_new, set_module_conditionals_new = dict_tuple
        dict_file_module.update(dict_file_module_new)
        dict_module_file.update(dict_module_file_new)
        dict_module_references.update(dict_module_references_new)
        dict_module_includes.update(dict_module_includes_new)
        set_module_conditionals.update(set_module_conditionals_new)

    path_modules, path_testbenches, path_includes = get_filelist( path_list )
    path_all = path_modules + path_testbenches + path_includes
    dict_modification_time_new = get_filelist_time(path_all)
    dict_include_dir = {path[0]: path[2] for path in path_includes}
    
    new_files, modified_files, deleted_files = sort_files_by_time( dict_modification_time_new, dict_modification_time )
    if len(new_files) == 0 and len(modified_files) == 0 and len(deleted_files) == 0:
        print("No file changed, database is not updated.")
        return False
    else:
        print("There are {} new files, {} changed files, {} deleted files".format(len(new_files), len(modified_files), len(deleted_files)))
    
    new_files_module, modified_files_module, deleted_files_module = set(new_files) & set(path_modules), set(modified_files) & set(path_modules), set(deleted_files) & set(path_modules)
    new_files_testbench, modified_files_testbench, deleted_files_testbench = set(new_files) & set(path_testbenches), set(modified_files) & set(path_testbenches), set(deleted_files) & set(path_testbenches)
    # new_files_include, modified_files_include, deleted_files_include = set(new_files) & set(path_includes), set(modified_files) & set(path_includes), set(deleted_files) & set(path_includes)
    
    dict_tuple_new = get_modules_data(new_files_module, defines=defines)
    update_dict_data(dict_tuple_new)
    dict_tuple_new = get_modules_data(new_files_testbench, defines=defines)
    update_dict_data(dict_tuple_new)
    
    for tfile in modified_files_module | modified_files_testbench:
        module_old = dict_file_module.pop(tfile[1])
        for module in module_old:
            if module in dict_module_file:
                dict_module_file.pop(module)
            if module in dict_module_references:
                dict_module_references.pop(module)
            if module in dict_module_includes:
                dict_module_includes.pop(module)
    dict_tuple_new = get_modules_data(modified_files_module, defines=defines)
    update_dict_data(dict_tuple_new)
    dict_tuple_new = get_modules_data(modified_files_testbench, defines=defines)
    update_dict_data(dict_tuple_new)

    for tfile in deleted_files_module | deleted_files_testbench:
        module_old = dict_file_module.pop(tfile[1])
        for module in module_old:
            dict_module_file.pop(module)
            dict_module_references.pop(module)
            if module in dict_module_includes:
                dict_module_includes.pop(module)
    
    save_database( dict_modification_time_new, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir )
    print("Database updated successfully")
    return True

def update_database_by_conditional_modules( module_set, defines={} ):
    dict_modification_time, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir, set_module_conditionals = load_database()

    def update_dict_data( dict_tuple ):
        dict_file_module_new, dict_module_file_new, dict_module_references_new, dict_module_includes_new, set_module_conditionals_new = dict_tuple
        dict_file_module.update(dict_file_module_new)
        dict_module_file.update(dict_module_file_new)
        dict_module_references.update(dict_module_references_new)
        dict_module_includes.update(dict_module_includes_new)
        set_module_conditionals.update(set_module_conditionals_new)

    # *: 根据define的变化从set_module_conditionals选择需要变更的模块，而不是更新全部
    print(module_set)
    print(set_module_conditionals)
    partial_modules = set_module_conditionals & module_set
    conditionals_files = [ (os.path.basename(dict_module_file[module]), dict_module_file[module]) for module in partial_modules ]
    conditionals_files = list(set(conditionals_files))  # remove duplicates
    print("updating conditional modules:\n",[i[0] for i in conditionals_files])
    for tfile in conditionals_files:
        module_old = dict_file_module.pop(tfile[1])
        for module in module_old:
            if module in dict_module_file:
                dict_module_file.pop(module)
            if module in dict_module_references:
                dict_module_references.pop(module)
            if module in dict_module_includes:
                dict_module_includes.pop(module)
    dict_tuple_new = get_modules_data(conditionals_files, defines=defines)
    update_dict_data(dict_tuple_new)
    
    # print("updated reference:")
    # for m in partial_modules:
    #     print(m, dict_module_references[m])

    return dict_modification_time, dict_file_module, dict_module_file, dict_module_references, dict_module_includes, dict_include_dir, set_module_conditionals

def get_all_submodule_by_module( top_module:str, dict_module_references:dict ):
    status = True
    visited = set()
    
    def dfs(module):
        nonlocal status
        if module in visited:
            return
        visited.add(module)
        for reference in dict_module_references.get(module, []):
            dfs(reference)
    
    if top_module not in dict_module_references:
        print(f"[ERROR] Top module[{top_module}] not found in dict_module_references")
        return set([]), False
    dfs(top_module)
    return visited, status

def get_filelist_by_module(top_module: str, dict_module_file, dict_module_references):
    filelist = []
    filelist_set = set()
    status = True
    visited = set()
    
    def dfs(module):
        nonlocal status
        if module in visited:
            return
        visited.add(module)
        if module not in dict_module_file:
            print(f"[ERROR] Module[{module}] not found in dict_module_file")
            status = False ; return
        for reference in dict_module_references.get(module, []):
            if reference not in dict_module_file:
                print(f"[ERROR] Reference[{reference}] not found in {dict_module_file[module]}")
                status = False ; continue
            dfs(reference)
        if dict_module_file[module] not in filelist_set:
            filelist.append(dict_module_file[module])
            filelist_set.add(dict_module_file[module])
    
    if top_module not in dict_module_references:
        print(f"[ERROR] Top module[{top_module}] not found in dict_module_references")
        return [], False
    dfs(top_module)
    return filelist, status

def get_incdir_by_module(top_module: str, dict_module_references, dict_module_includes, dict_include_dir):
    incdir_list = []
    incdir_set = set()
    status = True
    visited = set()
    
    def dfs(module):
        nonlocal status
        if module in visited:
            return
        visited.add(module)
        if module not in dict_module_includes:
            print(f"[ERROR] Module[{module}] not found in dict_module_includes")
            status = False ; return
        for reference in dict_module_references.get(module, []):
            if reference not in dict_module_includes:
                print(f"[ERROR] Reference[{reference}] not found in {dict_module_includes[module]}")
                status = False ;continue
            dfs(reference)
        for the_include in dict_module_includes[module]:
            if dict_include_dir[the_include] not in incdir_set:
                incdir_list.append(dict_include_dir[the_include])
                incdir_set.add(dict_include_dir[the_include])
    
    if top_module not in dict_module_references:
        print(f"[ERROR] Top module[{top_module}] not found in dict_module_references")
        return [], False
    dfs(top_module)
    return incdir_list, status

class Database():
    def __init__(self, path_list=["../../src", "../../lib/CustomLibrary/verilog/src"], defines={}):
        self.current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.path_list = [os.path.abspath(os.path.join(self.current_path, p)) for p in path_list]
        self.parse = parser
        self.defines = defines
        if not check_valid_database():
            print("Database not found, creating database...")
            create_database(self.path_list, self.defines)
            print("Database created successfully")
        else:
            update_database(self.path_list, self.defines)
        database_vars = load_database()
        self.get_database(database_vars)
    
    def get_database(self, database_vars):
        self.dict_modification_time, self.dict_file_module, self.dict_module_file, self.dict_module_references, self.dict_module_includes, self.dict_include_dir, self.set_module_conditionals = database_vars
    
    def build_database(self):
        print("Rebuilding database...")
        create_database(self.path_list, self.defines)
        print("Database rebuilt successfully")
    
    def get_filelist_by_module( self, top_module:str ):
        the_filelist, status_filelist = get_filelist_by_module( top_module, self.dict_module_file, self.dict_module_references )
        the_incdir, status_incdir = get_incdir_by_module( top_module, self.dict_module_references, self.dict_module_includes, self.dict_include_dir )
        status = status_filelist and status_incdir
        the_incdir = ["+incdir+"+i for i in the_incdir ]
        return the_incdir + the_filelist, status
    
    def generate_filelist_file( self, top_module:str, save_dir="" ):
        save_dir = PATH_FILELIST if save_dir == None or save_dir == "" else save_dir
        os.makedirs(save_dir, exist_ok=True)
        path_save = os.path.abspath(os.path.join(save_dir, f"{top_module}.f"))
        filelist, status = self.get_filelist_by_module( top_module )
        with open(path_save, "w") as f:
            for file in filelist:
                f.write(file + "\n")
        if status:
            print("Filelist generated successfully")
        else:
            print("!!! Filelist generated failed")
    
    def update_conditional_modules(self, top_module:str):
        submodules, status = get_all_submodule_by_module(top_module, self.dict_module_references)
        database_vars = update_database_by_conditional_modules(submodules, defines=self.defines)
        self.get_database(database_vars)
    
    def clean_filelist_file( self, save_dir="" ):
        save_dir = PATH_FILELIST if save_dir == None or save_dir == "" else save_dir
        path_save = os.path.abspath(os.path.join(self.current_path, save_dir))
        for the_file in os.listdir(path_save):
            if the_file.endswith(".f"):
                os.remove(os.path.join(save_dir, the_file))
        print("Filelist cleaned successfully")