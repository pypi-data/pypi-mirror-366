"""
Control structure block extractor for identifying and hashing code blocks.

This module extracts control structures (loops, conditionals, try-catch blocks)
and generates hashes for each block to enable fine-grained similarity detection.
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from ..hashing import FuzzyHasher, SemanticHasher

logger = logging.getLogger(__name__)


class ControlStructureType(Enum):
    """Types of control structures."""
    IF_STATEMENT = "if_statement"
    FOR_LOOP = "for_loop"
    WHILE_LOOP = "while_loop"
    DO_WHILE_LOOP = "do_while_loop"
    SWITCH_CASE = "switch_case"
    TRY_CATCH = "try_catch"
    WITH_STATEMENT = "with_statement"
    FOREACH_LOOP = "foreach_loop"
    CONDITIONAL_EXPRESSION = "conditional_expression"


class ControlBlockExtractor:
    """
    Extracts control structure blocks from AST and generates hashes.
    
    Control structures are important for:
    - Algorithm identification
    - Code similarity detection
    - Mutation detection
    - Pattern matching
    """
    
    def __init__(self):
        """Initialize control block extractor."""
        self.fuzzy_hasher = FuzzyHasher()
        self.semantic_hasher = SemanticHasher()
        
        # Language-specific control structure mappings
        self.control_structures = {
            'python': {
                'if_statement': ['if_statement'],
                'for_loop': ['for_statement', 'for_in_clause'],
                'while_loop': ['while_statement'],
                'try_catch': ['try_statement'],
                'with_statement': ['with_statement'],
                'conditional_expression': ['conditional_expression']
            },
            'javascript': {
                'if_statement': ['if_statement'],
                'for_loop': ['for_statement', 'for_in_statement', 'for_of_statement'],
                'while_loop': ['while_statement'],
                'do_while_loop': ['do_statement'],
                'switch_case': ['switch_statement'],
                'try_catch': ['try_statement'],
                'conditional_expression': ['ternary_expression']
            },
            'java': {
                'if_statement': ['if_statement'],
                'for_loop': ['for_statement', 'enhanced_for_statement'],
                'while_loop': ['while_statement'],
                'do_while_loop': ['do_statement'],
                'switch_case': ['switch_statement', 'switch_expression'],
                'try_catch': ['try_statement', 'try_with_resources_statement'],
                'conditional_expression': ['ternary_expression']
            },
            'c': {
                'if_statement': ['if_statement'],
                'for_loop': ['for_statement'],
                'while_loop': ['while_statement'],
                'do_while_loop': ['do_statement'],
                'switch_case': ['switch_statement'],
                'conditional_expression': ['conditional_expression']
            },
            'cpp': {
                'if_statement': ['if_statement'],
                'for_loop': ['for_statement', 'for_range_loop'],
                'while_loop': ['while_statement'],
                'do_while_loop': ['do_statement'],
                'switch_case': ['switch_statement'],
                'try_catch': ['try_statement'],
                'conditional_expression': ['conditional_expression']
            }
        }
    
    def extract_control_blocks(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """
        Extract all control structure blocks from AST.
        
        Args:
            ast_tree: AST tree from parser
            language: Programming language
            
        Returns:
            List of control blocks with hashes and metadata
        """
        blocks = []
        
        if not hasattr(ast_tree, 'root'):
            logger.debug("AST tree has no root")
            return blocks
        
        # Get language-specific control structures
        lang_structures = self.control_structures.get(language, self.control_structures['python'])
        
        # Walk the AST and extract control blocks
        self._extract_blocks_recursive(ast_tree.root, lang_structures, blocks, language)
        
        # Generate hashes for each block
        for block in blocks:
            self._generate_block_hashes(block)
        
        return blocks
    
    def _extract_blocks_recursive(self, node: Any, lang_structures: Dict[str, List[str]], 
                                 blocks: List[Dict[str, Any]], language: str, 
                                 parent_context: Optional[Dict[str, Any]] = None) -> None:
        """Recursively extract control blocks from AST."""
        if not node:
            return
        
        # Check if this node is a control structure
        node_type = getattr(node, 'type', '')
        control_type = self._get_control_type(node_type, lang_structures)
        
        if control_type:
            # Extract block information
            block = self._create_control_block(node, control_type, language, parent_context)
            blocks.append(block)
            
            # Update parent context for nested blocks
            parent_context = {
                'type': control_type.value,
                'start_line': block['location']['start_line'],
                'depth': parent_context['depth'] + 1 if parent_context else 1
            }
        
        # Process children
        if hasattr(node, 'children'):
            for child in node.children:
                self._extract_blocks_recursive(child, lang_structures, blocks, language, parent_context)
    
    def _get_control_type(self, node_type: str, lang_structures: Dict[str, List[str]]) -> Optional[ControlStructureType]:
        """Map node type to control structure type."""
        for control_type, node_types in lang_structures.items():
            if node_type in node_types:
                try:
                    return ControlStructureType(control_type)
                except ValueError:
                    return None
        return None
    
    def _create_control_block(self, node: Any, control_type: ControlStructureType, 
                             language: str, parent_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a control block entry with metadata."""
        # Extract location information
        start_point = getattr(node, 'start_point', (0, 0))
        end_point = getattr(node, 'end_point', (0, 0))
        
        # Extract code text
        node_text = getattr(node, 'text', '')
        if isinstance(node_text, bytes):
            code_text = node_text.decode('utf-8', errors='ignore')
        else:
            code_text = str(node_text) if node_text else ''
        
        # Extract complexity metrics
        complexity_metrics = self._calculate_block_complexity(node, control_type)
        
        # Extract nested structure information
        nested_info = self._extract_nested_structures(node, language)
        
        return {
            'type': control_type.value,
            'location': {
                'start_line': start_point[0] + 1,
                'end_line': end_point[0] + 1,
                'start_column': start_point[1],
                'end_column': end_point[1]
            },
            'code': code_text,
            'normalized_code': self._normalize_control_block(node, control_type, language),
            'parent_context': parent_context,
            'complexity_metrics': complexity_metrics,
            'nested_structures': nested_info,
            'language': language,
            'ast_node': node
        }
    
    def _normalize_control_block(self, node: Any, control_type: ControlStructureType, 
                                language: str) -> str:
        """Normalize control block for comparison."""
        normalized = f"{control_type.value.upper()}\n"
        
        if control_type == ControlStructureType.IF_STATEMENT:
            normalized += self._normalize_if_statement(node, language)
        elif control_type in [ControlStructureType.FOR_LOOP, ControlStructureType.FOREACH_LOOP]:
            normalized += self._normalize_for_loop(node, language)
        elif control_type == ControlStructureType.WHILE_LOOP:
            normalized += self._normalize_while_loop(node, language)
        elif control_type == ControlStructureType.TRY_CATCH:
            normalized += self._normalize_try_catch(node, language)
        elif control_type == ControlStructureType.SWITCH_CASE:
            normalized += self._normalize_switch_case(node, language)
        else:
            normalized += "CONTROL_BLOCK"
        
        return normalized
    
    def _normalize_if_statement(self, node: Any, language: str) -> str:
        """Normalize if statement structure."""
        parts = []
        
        # Extract condition
        condition_node = self._find_child_by_type(node, ['condition', 'expression', 'binary_expression'])
        if condition_node:
            parts.append("CONDITION(EXPRESSION)")
        
        # Check for else/elif
        has_else = self._has_child_type(node, ['else_clause', 'else_statement'])
        has_elif = self._has_child_type(node, ['elif_clause', 'elseif_statement'])
        
        if has_elif:
            parts.append("ELIF_BRANCHES")
        if has_else:
            parts.append("ELSE_BRANCH")
        
        # Extract body characteristics
        body_info = self._analyze_block_body(node)
        parts.extend(body_info)
        
        return "\n".join(parts)
    
    def _normalize_for_loop(self, node: Any, language: str) -> str:
        """Normalize for loop structure."""
        parts = []
        
        # Detect loop type
        if language == 'python':
            if self._has_child_type(node, ['in']):
                parts.append("FOR_IN_LOOP")
            else:
                parts.append("FOR_LOOP")
        else:
            if self._has_child_type(node, ['for_in_statement', 'for_of_statement']):
                parts.append("FOR_IN_LOOP")
            else:
                parts.append("FOR_LOOP")
        
        # Extract iterator pattern
        parts.append("ITERATOR(VAR)")
        
        # Extract body characteristics
        body_info = self._analyze_block_body(node)
        parts.extend(body_info)
        
        return "\n".join(parts)
    
    def _normalize_while_loop(self, node: Any, language: str) -> str:
        """Normalize while loop structure."""
        parts = ["WHILE_CONDITION(EXPRESSION)"]
        
        # Extract body characteristics
        body_info = self._analyze_block_body(node)
        parts.extend(body_info)
        
        return "\n".join(parts)
    
    def _normalize_try_catch(self, node: Any, language: str) -> str:
        """Normalize try-catch structure."""
        parts = ["TRY_BLOCK"]
        
        # Check for catch blocks
        catch_count = self._count_child_type(node, ['catch_clause', 'catch_block'])
        if catch_count > 0:
            parts.append(f"CATCH_BLOCKS({catch_count})")
        
        # Check for finally
        if self._has_child_type(node, ['finally_clause', 'finally_block']):
            parts.append("FINALLY_BLOCK")
        
        return "\n".join(parts)
    
    def _normalize_switch_case(self, node: Any, language: str) -> str:
        """Normalize switch/case structure."""
        parts = ["SWITCH_EXPRESSION"]
        
        # Count cases
        case_count = self._count_child_type(node, ['case_statement', 'switch_case'])
        parts.append(f"CASES({case_count})")
        
        # Check for default
        if self._has_child_type(node, ['default_statement', 'default_case']):
            parts.append("DEFAULT_CASE")
        
        return "\n".join(parts)
    
    def _analyze_block_body(self, node: Any) -> List[str]:
        """Analyze the body of a control block."""
        characteristics = []
        
        if not node:
            return characteristics
        
        # Count different statement types
        assignments = self._count_child_type(node, ['assignment', 'assignment_expression'])
        calls = self._count_child_type(node, ['call', 'call_expression', 'function_call'])
        returns = self._count_child_type(node, ['return_statement', 'return'])
        
        if assignments > 0:
            characteristics.append(f"ASSIGNMENTS({assignments})")
        if calls > 0:
            characteristics.append(f"CALLS({calls})")
        if returns > 0:
            characteristics.append(f"RETURNS({returns})")
        
        # Check for nested control structures
        nested_controls = self._count_nested_controls(node)
        if nested_controls > 0:
            characteristics.append(f"NESTED_CONTROLS({nested_controls})")
        
        return characteristics
    
    def _calculate_block_complexity(self, node: Any, control_type: ControlStructureType) -> Dict[str, Any]:
        """Calculate complexity metrics for a control block."""
        metrics = {
            'type_complexity': self._get_type_complexity(control_type),
            'nesting_depth': self._calculate_nesting_depth(node),
            'statement_count': self._count_statements(node),
            'branch_count': self._count_branches(node),
            'cyclomatic_contribution': self._calculate_cyclomatic_contribution(node, control_type)
        }
        
        # Calculate overall complexity score
        metrics['complexity_score'] = (
            metrics['type_complexity'] * 0.3 +
            metrics['nesting_depth'] * 0.2 +
            min(metrics['statement_count'] / 10, 1.0) * 0.2 +
            metrics['branch_count'] * 0.15 +
            metrics['cyclomatic_contribution'] * 0.15
        )
        
        return metrics
    
    def _get_type_complexity(self, control_type: ControlStructureType) -> float:
        """Get base complexity for control structure type."""
        complexities = {
            ControlStructureType.IF_STATEMENT: 0.3,
            ControlStructureType.FOR_LOOP: 0.5,
            ControlStructureType.WHILE_LOOP: 0.5,
            ControlStructureType.DO_WHILE_LOOP: 0.5,
            ControlStructureType.SWITCH_CASE: 0.6,
            ControlStructureType.TRY_CATCH: 0.7,
            ControlStructureType.WITH_STATEMENT: 0.4,
            ControlStructureType.FOREACH_LOOP: 0.4,
            ControlStructureType.CONDITIONAL_EXPRESSION: 0.2
        }
        return complexities.get(control_type, 0.5)
    
    def _extract_nested_structures(self, node: Any, language: str) -> Dict[str, Any]:
        """Extract information about nested control structures."""
        lang_structures = self.control_structures.get(language, self.control_structures['python'])
        nested = {
            'total_nested': 0,
            'max_depth': 0,
            'nested_types': []
        }
        
        self._count_nested_recursive(node, lang_structures, nested, 0)
        
        return nested
    
    def _count_nested_recursive(self, node: Any, lang_structures: Dict[str, List[str]], 
                               nested: Dict[str, Any], depth: int) -> None:
        """Recursively count nested control structures."""
        if not hasattr(node, 'children'):
            return
        
        for child in node.children:
            node_type = getattr(child, 'type', '')
            control_type = self._get_control_type(node_type, lang_structures)
            
            if control_type:
                nested['total_nested'] += 1
                nested['max_depth'] = max(nested['max_depth'], depth + 1)
                if control_type.value not in nested['nested_types']:
                    nested['nested_types'].append(control_type.value)
                
                # Recurse with increased depth
                self._count_nested_recursive(child, lang_structures, nested, depth + 1)
            else:
                # Continue at same depth
                self._count_nested_recursive(child, lang_structures, nested, depth)
    
    def _generate_block_hashes(self, block: Dict[str, Any]) -> None:
        """Generate various hashes for a control block."""
        # Direct hash of normalized code
        normalized = block['normalized_code']
        block['hashes'] = {
            'sha256': hashlib.sha256(normalized.encode()).hexdigest(),
            'md5': hashlib.md5(normalized.encode()).hexdigest()[:16],
            'structure_hash': self._generate_structure_hash(block)
        }
        
        # Fuzzy hash for similarity
        if len(normalized) > 50:  # TLSH needs minimum length
            block['hashes']['tlsh'] = self.fuzzy_hasher.tlsh(normalized)
        
        # Semantic hash
        block['hashes']['simhash'] = self.semantic_hasher.generate_simhash(normalized)
        
        # Context-aware hash (includes parent context)
        parent_context = block.get('parent_context') or {}
        parent_type = parent_context.get('type', 'root') if parent_context else 'root'
        context_str = f"{parent_type}:{normalized}"
        block['hashes']['context_hash'] = hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    def _generate_structure_hash(self, block: Dict[str, Any]) -> str:
        """Generate a hash based on control structure characteristics."""
        structure_data = {
            'type': block['type'],
            'complexity': block['complexity_metrics']['complexity_score'],
            'nested_types': block['nested_structures']['nested_types'],
            'characteristics': self._analyze_block_body(block.get('ast_node'))
        }
        
        structure_str = str(sorted(structure_data.items()))
        return hashlib.sha256(structure_str.encode()).hexdigest()[:16]
    
    # Helper methods
    def _find_child_by_type(self, node: Any, types: List[str]) -> Optional[Any]:
        """Find first child node of given types."""
        if not hasattr(node, 'children'):
            return None
        
        for child in node.children:
            if hasattr(child, 'type') and child.type in types:
                return child
        
        return None
    
    def _has_child_type(self, node: Any, types: List[str]) -> bool:
        """Check if node has child of given types."""
        return self._find_child_by_type(node, types) is not None
    
    def _count_child_type(self, node: Any, types: List[str]) -> int:
        """Count children of given types."""
        if not hasattr(node, 'children'):
            return 0
        
        count = 0
        for child in node.children:
            if hasattr(child, 'type') and child.type in types:
                count += 1
            # Recurse
            count += self._count_child_type(child, types)
        
        return count
    
    def _count_statements(self, node: Any) -> int:
        """Count total statements in block."""
        if not hasattr(node, 'children'):
            return 0
        
        count = 0
        statement_types = ['statement', 'expression_statement', 'assignment', 'call', 'return']
        
        for child in node.children:
            if hasattr(child, 'type') and any(st in child.type for st in statement_types):
                count += 1
            count += self._count_statements(child)
        
        return count
    
    def _count_branches(self, node: Any) -> int:
        """Count branches in control structure."""
        branch_types = ['if_statement', 'elif_clause', 'else_clause', 'case_statement', 
                       'catch_clause', 'when_clause']
        return self._count_child_type(node, branch_types)
    
    def _calculate_cyclomatic_contribution(self, node: Any, control_type: ControlStructureType) -> float:
        """Calculate cyclomatic complexity contribution."""
        base_contributions = {
            ControlStructureType.IF_STATEMENT: 1.0,
            ControlStructureType.FOR_LOOP: 1.0,
            ControlStructureType.WHILE_LOOP: 1.0,
            ControlStructureType.DO_WHILE_LOOP: 1.0,
            ControlStructureType.SWITCH_CASE: 0.5,  # Each case adds complexity
            ControlStructureType.TRY_CATCH: 0.5,  # Each catch adds complexity
            ControlStructureType.CONDITIONAL_EXPRESSION: 1.0
        }
        
        contribution = base_contributions.get(control_type, 0.5)
        
        # Add for branches
        if control_type == ControlStructureType.SWITCH_CASE:
            contribution += self._count_child_type(node, ['case_statement']) * 0.5
        elif control_type == ControlStructureType.IF_STATEMENT:
            contribution += self._count_child_type(node, ['elif_clause', 'elseif_clause']) * 1.0
        
        return contribution
    
    def _calculate_nesting_depth(self, node: Any) -> int:
        """Calculate maximum nesting depth within block."""
        return self._extract_nested_structures(node, 'python')['max_depth']
    
    def _count_nested_controls(self, node: Any) -> int:
        """Count nested control structures."""
        return self._extract_nested_structures(node, 'python')['total_nested']