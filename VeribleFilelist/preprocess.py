# =============================================================
# @Author: zhangshen
# @Date: 2025-04-11 10:57:23
# @LastEditors: zhangshen
# @LastEditTime: 2025-05-23 17:11:04
# @Description: 
# @Created by RICL of ShanghaiTech SIST
# @FilePath: /TSNN-HDL/tool/VeribleFilelist/preprocess.py
# =============================================================
import re
from collections import OrderedDict

class VerilogPreprocessor:
    def __init__(self, external_defines=None):
        # Use OrderedDict to maintain the order of macro definitions, with later-defined macros having higher priority
        self.defines = OrderedDict()
        
        # Add externally defined macros (highest priority)
        if external_defines:
            self.defines.update(external_defines)
            
        # Compile regular expressions
        self.macro_def_regex = re.compile(r'`define\s+(\w+)(?:\s+(.*?))?\s*(?://.*)?$')
        self.macro_ref_regex = re.compile(r'`(\w+)')
        self.delay_expr_regex = re.compile(r'#\s*([^\(\)\s;]+)\s*;')
        self.conditional_stack = []
        self.skip_level = None
        
    def preprocess(self, input_text):

        self._extract_macros(input_text)
        processed = self._expand_macros(input_text)
        processed = self._process_conditionals(processed)

        self._extract_macros(processed)
        processed = self._expand_macros(processed)
        processed = self._process_conditionals(processed)
        
        processed = self._process_delay_expressions(processed)
        return processed
    
    def _process_delay_expressions(self, text):
        """deal with the delay"""
        def replace_delay(match):
            delay_expr = match.group(1).strip()
            return f'#({delay_expr});'
        
        return self.delay_expr_regex.sub(replace_delay, text)
    
    # todo : the current code should bette support ifndef. all modules should be added to the filelist.
    def _extract_macros(self, text):
        """Extract macro definitions, skipping definitions inside ifndef guard blocks"""
        lines = text.splitlines()
        in_ifndef_guard = False
        guard_macro = None
        
        for line in lines:
            stripped = line.strip()
            
            # Detect the start of an ifndef guard block
            if (not in_ifndef_guard and stripped.startswith('`ifndef')):
                guard_macro = stripped.split()[1]
                in_ifndef_guard = True
                continue
                
            # Detect the corresponding endif
            if in_ifndef_guard and stripped == '`endif':
                in_ifndef_guard = False
                guard_macro = None
                continue
                
            # Skip the content inside ifndef guard blocks
            if in_ifndef_guard:
                continue
                
            # Extract regular macro definitions
            match = self.macro_def_regex.match(stripped)
            if match:
                macro_name, macro_value = match.groups()
                if macro_name not in self.defines:
                    self.defines[macro_name] = macro_value if macro_value else ''
    
    def _expand_macros(self, text):
        """Expand macro definitions, prioritizing externally defined macros"""
        def replace_macro(match):
            macro_name = match.group(1)
            return str(self.defines.get(macro_name, f'`{macro_name}'))
        
        # Replace macros repeatedly until no more macros can be replaced
        old_text, new_text = None, text
        while old_text != new_text:
            old_text = new_text
            new_text = self.macro_ref_regex.sub(replace_macro, old_text)
        return new_text
    
    def _process_conditionals(self, text):
        """Process conditional compilation directives"""
        lines = text.splitlines()
        output_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('`ifdef'):
                macro = stripped.split()[1]
                self.conditional_stack.append(('ifdef', macro))
                if self.skip_level is None:
                    if macro not in self.defines:
                        self.skip_level = len(self.conditional_stack) - 1
                continue
                
            elif stripped.startswith('`ifndef'):
                macro = stripped.split()[1]
                self.conditional_stack.append(('ifndef', macro))
                if self.skip_level is None:
                    if macro in self.defines:
                        self.skip_level = len(self.conditional_stack) - 1
                continue
                
            elif stripped.startswith('`else'):
                if not self.conditional_stack:
                    raise SyntaxError("`else without `ifdef/`ifndef")
                
                if self.skip_level is None:
                    self.skip_level = len(self.conditional_stack) - 1
                elif self.skip_level == len(self.conditional_stack) - 1:
                    self.skip_level = None
                continue
                
            elif stripped.startswith('`endif'):
                if not self.conditional_stack:
                    raise SyntaxError("`endif without `ifdef/`ifndef")
                
                if self.skip_level == len(self.conditional_stack) - 1:
                    self.skip_level = None
                self.conditional_stack.pop()
                continue
                
            if self.skip_level is None:
                output_lines.append(line)
        
        return '\n'.join(output_lines)
    
    def check_conditionals(self, text):
        lines = text.splitlines()
        result = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('`ifdef') or stripped.startswith('`ifndef'):
                macro = stripped.split()[1]
                result = True; break
        return result
