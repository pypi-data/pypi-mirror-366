"""
Algorithmic normalization for cross-language semantic analysis.
"""

import re
from typing import Dict, List, Any, Set, Tuple
from collections import Counter


class AlgorithmicNormalizer:
    """Normalize code to extract algorithmic essence across languages."""
    
    def __init__(self):
        self.variable_map = {}
        self.function_map = {}
        self.var_counter = 0
        self.func_counter = 0
    
    def normalize_function(self, func_node: Any, func_text: str, language: str) -> str:
        """
        Extract normalized algorithmic representation from function.
        
        This creates a language-agnostic representation focusing on:
        - Control flow patterns
        - Variable relationships  
        - Algorithmic operations
        - Mathematical expressions
        """
        self._reset_mappings()
        
        # Extract structural elements
        structure = self._extract_structure(func_node, func_text, language)
        
        # Normalize components
        normalized_parts = []
        normalized_parts.append(f"FUNCTION {self._get_normalized_name('main_func')}")
        
        # Add control flow patterns
        control_flow = self._extract_control_flow(structure)
        normalized_parts.extend(control_flow)
        
        # Add variable operations
        operations = self._extract_operations(structure)
        normalized_parts.extend(operations)
        
        # Add mathematical expressions
        math_exprs = self._extract_mathematical_patterns(structure)
        normalized_parts.extend(math_exprs)
        
        # Join with consistent formatting
        return "\n".join(normalized_parts)
    
    def _reset_mappings(self):
        """Reset variable and function mappings for new function."""
        self.variable_map = {}
        self.function_map = {}
        self.var_counter = 0
        self.func_counter = 0
    
    def _extract_structure(self, func_node: Any, func_text: str, language: str) -> Dict[str, Any]:
        """Extract structural information from function."""
        structure = {
            'control_flow': [],
            'variables': set(),
            'operations': [],
            'function_calls': [],
            'comparisons': [],
            'assignments': [],
            'loops': [],
            'conditionals': [],
            'returns': [],
            'mathematical_ops': []
        }
        
        # Language-specific parsing
        if language == 'python':
            self._parse_python_structure(func_text, structure)
        elif language in ['c', 'cpp']:
            self._parse_c_structure(func_text, structure)
        elif language == 'javascript':
            self._parse_javascript_structure(func_text, structure)
        else:
            # Generic parsing
            self._parse_generic_structure(func_text, structure)
        
        return structure
    
    def _parse_python_structure(self, func_text: str, structure: Dict[str, Any]):
        """Parse Python-specific structures."""
        lines = func_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('"""'):
                continue
                
            # Control flow
            if re.match(r'\s*if\s+', line):
                structure['conditionals'].append(self._normalize_condition(line))
            elif re.match(r'\s*while\s+', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*for\s+', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*return\s+', line):
                structure['returns'].append(self._normalize_return(line))
            
            # Assignments
            if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
                structure['assignments'].append(self._normalize_assignment(line))
            
            # Function calls
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for call in func_calls:
                if call not in ['if', 'while', 'for', 'return', 'print']:
                    structure['function_calls'].append(self._get_normalized_name(call, is_function=True))
            
            # Variables
            variables = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
            for var in variables:
                if var not in ['if', 'while', 'for', 'return', 'and', 'or', 'not', 'in', 'is']:
                    structure['variables'].add(var)
            
            # Mathematical operations
            math_ops = re.findall(r'[\+\-\*\/\%]', line)
            structure['mathematical_ops'].extend(math_ops)
            
            # Comparisons
            comparisons = re.findall(r'(<=|>=|<|>|==|!=)', line)
            structure['comparisons'].extend(comparisons)
    
    def _parse_c_structure(self, func_text: str, structure: Dict[str, Any]):
        """Parse C/C++-specific structures."""
        # Remove comments
        func_text = re.sub(r'//.*$', '', func_text, flags=re.MULTILINE)
        func_text = re.sub(r'/\*.*?\*/', '', func_text, flags=re.DOTALL)
        
        lines = func_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Control flow
            if re.match(r'\s*if\s*\(', line):
                structure['conditionals'].append(self._normalize_condition(line))
            elif re.match(r'\s*while\s*\(', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*for\s*\(', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*return\s+', line):
                structure['returns'].append(self._normalize_return(line))
            
            # Assignments
            if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
                structure['assignments'].append(self._normalize_assignment(line))
            
            # Function calls
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for call in func_calls:
                if call not in ['if', 'while', 'for', 'return', 'printf', 'sizeof']:
                    structure['function_calls'].append(self._get_normalized_name(call, is_function=True))
            
            # Variables
            variables = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
            for var in variables:
                if var not in ['if', 'while', 'for', 'return', 'int', 'char', 'float', 'double', 'void']:
                    structure['variables'].add(var)
            
            # Mathematical operations
            math_ops = re.findall(r'[\+\-\*\/\%]', line)
            structure['mathematical_ops'].extend(math_ops)
            
            # Comparisons
            comparisons = re.findall(r'(<=|>=|<|>|==|!=)', line)
            structure['comparisons'].extend(comparisons)
    
    def _parse_javascript_structure(self, func_text: str, structure: Dict[str, Any]):
        """Parse JavaScript-specific structures."""
        # Remove comments
        func_text = re.sub(r'//.*$', '', func_text, flags=re.MULTILINE)
        func_text = re.sub(r'/\*.*?\*/', '', func_text, flags=re.DOTALL)
        
        lines = func_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Control flow
            if re.match(r'\s*if\s*\(', line):
                structure['conditionals'].append(self._normalize_condition(line))
            elif re.match(r'\s*while\s*\(', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*for\s*\(', line):
                structure['loops'].append(self._normalize_loop(line))
            elif re.match(r'\s*return\s+', line):
                structure['returns'].append(self._normalize_return(line))
            
            # Assignments
            if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=', '=>']):
                structure['assignments'].append(self._normalize_assignment(line))
            
            # Function calls
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for call in func_calls:
                if call not in ['if', 'while', 'for', 'return', 'console', 'Math']:
                    structure['function_calls'].append(self._get_normalized_name(call, is_function=True))
            
            # Variables
            variables = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
            for var in variables:
                if var not in ['if', 'while', 'for', 'return', 'const', 'let', 'var', 'function']:
                    structure['variables'].add(var)
            
            # Mathematical operations
            math_ops = re.findall(r'[\+\-\*\/\%]', line)
            structure['mathematical_ops'].extend(math_ops)
            
            # Comparisons
            comparisons = re.findall(r'(<=|>=|<|>|==|!=|===|!==)', line)
            structure['comparisons'].extend(comparisons)
    
    def _parse_generic_structure(self, func_text: str, structure: Dict[str, Any]):
        """Generic structure parsing for unknown languages."""
        lines = func_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Basic pattern matching
            if re.search(r'\b(if|IF)\b', line):
                structure['conditionals'].append("CONDITIONAL")
            if re.search(r'\b(while|WHILE|for|FOR)\b', line):
                structure['loops'].append("LOOP")
            if re.search(r'\b(return|RETURN)\b', line):
                structure['returns'].append("RETURN")
            
            # Mathematical operations
            math_ops = re.findall(r'[\+\-\*\/\%]', line)
            structure['mathematical_ops'].extend(math_ops)
            
            # Comparisons
            comparisons = re.findall(r'(<=|>=|<|>|==|!=)', line)
            structure['comparisons'].extend(comparisons)
    
    def _get_normalized_name(self, name: str, is_function: bool = False) -> str:
        """Get normalized variable or function name."""
        if is_function:
            if name not in self.function_map:
                self.func_counter += 1
                self.function_map[name] = f"FUNC{self.func_counter}"
            return self.function_map[name]
        else:
            if name not in self.variable_map:
                self.var_counter += 1
                self.variable_map[name] = f"VAR{self.var_counter}"
            return self.variable_map[name]
    
    def _normalize_condition(self, line: str) -> str:
        """Normalize conditional statements."""
        # Extract comparison operators
        if '<=' in line:
            return "CONDITION VAR LE VAR"
        elif '>=' in line:
            return "CONDITION VAR GE VAR"
        elif '<' in line:
            return "CONDITION VAR LT VAR"
        elif '>' in line:
            return "CONDITION VAR GT VAR"
        elif '==' in line:
            return "CONDITION VAR EQ VAR"
        elif '!=' in line:
            return "CONDITION VAR NE VAR"
        else:
            return "CONDITION VAR"
    
    def _normalize_loop(self, line: str) -> str:
        """Normalize loop statements."""
        if 'while' in line.lower():
            return "LOOP WHILE CONDITION"
        elif 'for' in line.lower():
            return "LOOP FOR ITERATOR"
        else:
            return "LOOP"
    
    def _normalize_return(self, line: str) -> str:
        """Normalize return statements."""
        if '+' in line:
            return "RETURN VAR PLUS VAR"
        elif '*' in line:
            return "RETURN VAR MULT VAR"
        elif '(' in line:
            return "RETURN FUNC_CALL"
        else:
            return "RETURN VAR"
    
    def _normalize_assignment(self, line: str) -> str:
        """Normalize assignment statements."""
        if '+' in line:
            return "ASSIGN VAR PLUS VAR"
        elif '-' in line:
            return "ASSIGN VAR MINUS VAR"
        elif '*' in line:
            return "ASSIGN VAR MULT VAR"
        elif '/' in line:
            return "ASSIGN VAR DIV VAR"
        elif '[' in line and ']' in line:
            return "ASSIGN VAR ARRAY_ACCESS"
        else:
            return "ASSIGN VAR VAR"
    
    def _extract_control_flow(self, structure: Dict[str, Any]) -> List[str]:
        """Extract normalized control flow patterns."""
        patterns = []
        
        # Add loops
        for loop in structure['loops']:
            patterns.append(loop)
        
        # Add conditionals
        for cond in structure['conditionals']:
            patterns.append(cond)
        
        # Add function calls
        for call in structure['function_calls']:
            patterns.append(f"CALL {call}")
        
        return patterns
    
    def _extract_operations(self, structure: Dict[str, Any]) -> List[str]:
        """Extract normalized operations."""
        operations = []
        
        # Add assignments
        for assign in structure['assignments']:
            operations.append(assign)
        
        # Add returns
        for ret in structure['returns']:
            operations.append(ret)
        
        return operations
    
    def _extract_mathematical_patterns(self, structure: Dict[str, Any]) -> List[str]:
        """Extract mathematical operation patterns."""
        patterns = []
        
        # Count mathematical operations
        op_counts = Counter(structure['mathematical_ops'])
        for op, count in op_counts.items():
            if op == '+':
                patterns.append(f"MATH_OP ADD {count}")
            elif op == '-':
                patterns.append(f"MATH_OP SUB {count}")
            elif op == '*':
                patterns.append(f"MATH_OP MULT {count}")
            elif op == '/':
                patterns.append(f"MATH_OP DIV {count}")
            elif op == '%':
                patterns.append(f"MATH_OP MOD {count}")
        
        # Count comparison operations
        comp_counts = Counter(structure['comparisons'])
        for comp, count in comp_counts.items():
            if comp in ['<', 'lt']:
                patterns.append(f"COMPARE LT {count}")
            elif comp in ['>', 'gt']:
                patterns.append(f"COMPARE GT {count}")
            elif comp in ['<=', 'le']:
                patterns.append(f"COMPARE LE {count}")
            elif comp in ['>=', 'ge']:
                patterns.append(f"COMPARE GE {count}")
            elif comp in ['==', 'eq']:
                patterns.append(f"COMPARE EQ {count}")
            elif comp in ['!=', 'ne']:
                patterns.append(f"COMPARE NE {count}")
        
        return patterns