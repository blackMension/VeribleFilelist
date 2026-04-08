# =============================================================
# @Author: ZhangShen
# @Date: 2025-01-09 15:01:23
# @LastEditors: zhangshen
# @LastEditTime: 2025-05-23 16:50:56
# @Description: 
# @Created by RICL of ShanghaiTech SIST
# @FilePath: /TSNN-HDL/tool/VeribleFilelist/parse.py
# =============================================================

import re
import os
import sys
import anytree
import verible_verilog_syntax
from preprocess import VerilogPreprocessor

def get_all_instance( data_tree ):
    search_list = data_tree.find_all({"tag": "kGateInstance"})
    instance_list = [n.parent.parent for n in search_list]
    return instance_list

def get_module_name( instance_base ):
    module_name = instance_base.find({"tag": ["kInstantiationType","kUnqualifiedId"]}).find({"tag": "SymbolIdentifier"})
    return module_name.text

def get_instacne_name( instance_base ):
    module_name = instance_base.find({"tag": ["kGateInstanceRegisterVariableList","kGateInstance"]}).find({"tag": "SymbolIdentifier"})
    return module_name.text

def get_modules_info( data ):
    glb_includes = []
    for include_tree in data.tree.find_all({"tag": "kPreprocessorInclude"}):
        include_items = include_tree.find_all({"tag": "TK_StringLiteral"})
        glb_includes += [ i.text.replace('"','') for i in include_items ]
    
    glb_imports = []
    for import_tree in data.tree.find_all({"tag": "kPackageImportItem"}):
        import_items = import_tree.find_all({"tag": "SymbolIdentifier"})
        glb_imports += [ i.text for i in import_items ]
    
    modules_info = []
    
    for module in data.tree.iter_find_all({"tag": "kInterfaceDeclaration"}):
        module_info = {
            "header_text": "",
            "name": "",
            "ports": [],
            "parameters": [],
            "imports": [],
            "includes": [],
            "instance": [],
            "reference": set([])
        }

        # Find module header
        header = module.find({"tag": "kModuleHeader"})
        if not header:
            continue
        module_info["header_text"] = header.text

        # Find module name
        name = header.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]},
                            iter_=anytree.PreOrderIter)
        if not name:
            continue
        module_info["name"] = name.text

        # Get the list of ports
        for port in header.iter_find_all({"tag": ["kPortDeclaration", "kPort"]}):
            port_id = port.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
            module_info["ports"].append(port_id.text)

        # Get the list of parameters
        for param in header.iter_find_all({"tag": ["kParamDeclaration"]}):
            param_id = param.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
            module_info["parameters"].append(param_id.text)

        # Get the list of imports
        for pkg in module.iter_find_all({"tag": ["kPackageImportItem"]}):
            module_info["imports"].append(pkg.find( {"tag" : "SymbolIdentifier"} ).text)
        module_info["imports"] += glb_imports
        
        module_info["includes"] += glb_includes
        
        instance_list = get_all_instance(module)
        instance_info = []
        reference_set = set([])
        for instance_base in instance_list:
            module_name = get_module_name(instance_base)
            instance_name = get_instacne_name(instance_base)
            instance_info.append( (module_name, instance_name) )
            reference_set.add( module_name )
        module_info["instance"] = instance_info
        module_info["reference"] = reference_set
        module_info["reference"].update( set(module_info["imports"]) )

        modules_info.append(module_info)
    
    for package in data.tree.iter_find_all({"tag": "kPackageDeclaration"}):
        module_info = {
            "header_text": "",
            "name": "",
            "ports": [],
            "parameters": [],
            "imports": [],
            "includes": [],
            "instance": [],
            "reference": set([])
        }
        module_info["name"] = package.find( {"tag" : "SymbolIdentifier"} ).text

        # Get the list of parameters
        for param in package.iter_find_all({"tag": ["kParamDeclaration"]}):
            param_id = param.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
            module_info["parameters"].append(param_id.text)

        for pkg in package.iter_find_all({"tag": ["kPackageImportItem"]}):
            module_info["imports"].append(pkg.find( {"tag" : "SymbolIdentifier"} ).text)
        module_info["imports"] += glb_imports
        
        module_info["includes"] += glb_includes
        
        module_info["reference"] = set(module_info["imports"]) 
        
        modules_info.append(module_info)
    
    for module in data.tree.iter_find_all({"tag": "kModuleDeclaration"}):
        module_info = {
            "header_text": "",
            "name": "",
            "ports": [],
            "parameters": [],
            "imports": [],
            "includes": [],
            "instance": [],
            "reference": set([])
        }

        # Find module header
        header = module.find({"tag": "kModuleHeader"})
        if not header:
            continue
        module_info["header_text"] = header.text

        # Find module name
        name = header.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]},
                            iter_=anytree.PreOrderIter)
        if not name:
            continue
        module_info["name"] = name.text

        # Get the list of ports
        for port in header.iter_find_all({"tag": ["kPortDeclaration", "kPort"]}):
            port_id = port.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
            module_info["ports"].append(port_id.text)

        # Get the list of parameters
        for param in header.iter_find_all({"tag": ["kParamDeclaration"]}):
            param_id = param.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
            module_info["parameters"].append(param_id.text)

        # Get the list of imports
        for pkg in module.iter_find_all({"tag": ["kPackageImportItem"]}):
            module_info["imports"].append(pkg.find( {"tag" : "SymbolIdentifier"} ).text)
        module_info["imports"] += glb_imports
        
        module_info["includes"] += glb_includes
        
        instance_list = get_all_instance(module)
        instance_info = []
        reference_set = set([])
        for instance_base in instance_list:
            module_name = get_module_name(instance_base)
            instance_name = get_instacne_name(instance_base)
            instance_info.append( (module_name, instance_name) )
            reference_set.add( module_name )
        module_info["instance"] = instance_info
        module_info["reference"] = reference_set
        module_info["reference"].update( set(module_info["imports"]) )

        modules_info.append(module_info)
    return modules_info

def process_module_files( path_list:list, parser ):
    data_list = parser.parse_files(path_list)
    data_values = list(data_list.values())
    return data_values

def process_module_file( path_file:str, parser ):
    data = parser.parse_file(path_file)
    return data

def process_testbench_file( path_file:str, parser ):
    with open(path_file, 'r') as f:
        string_tb = f.read()
        
    pattern = r"`define\s+TB_MODULE_NAME\s+(\w+)"
    match = re.search(pattern, string_tb)
    assert match, "TB_MODULE_NAME not found"
    module_name = match.group(1) 
    string_new = string_tb.replace("`TB_MODULE_NAME", module_name)
    data = parser.parse_string(string_new)
    return data

def process_module_with_define( path_file:str, defines:dict, parser ):
    with open(path_file, 'r') as f:
        string_v = f.read()
    preprocessor = VerilogPreprocessor( defines )
    include_conditionals = preprocessor.check_conditionals(string_v)
    content_preprocess = preprocessor.preprocess(string_v)
    data = parser.parse_string(content_preprocess)
    return data, include_conditionals

def process_module_without_define(path_file:str, parser):
    with open(path_file, 'r') as f:
        string_v = f.read()
    data = parser.parse_string(string_v)
    return data

def traverse_directory(directory):
    path_modules_list = []
    path_testbenches_list = []
    path_includes_list = []
    for dirpath, dirs, files in os.walk(directory):
        folder_name = os.path.basename(dirpath)
        save_list = path_modules_list
        if folder_name == 'testbench':
            save_list = path_testbenches_list
        elif folder_name == 'abandon':
            dirs[:] = []
            continue
        for the_file in files:
            if the_file.endswith('.v') or the_file.endswith('.sv'):
                file_path = os.path.join(dirpath, the_file)
                absolute_file_path = os.path.abspath(file_path)
                save_list.append((the_file,absolute_file_path))
            elif the_file.endswith('.svh') or the_file.endswith('.h') or the_file.endswith('.vh'):
                file_path = os.path.join(dirpath, the_file)
                absolute_file_path = os.path.abspath(file_path)
                dir_path = os.path.abspath(dirpath)
                path_includes_list.append((the_file,absolute_file_path, dir_path))
    return path_modules_list, path_testbenches_list, path_includes_list
