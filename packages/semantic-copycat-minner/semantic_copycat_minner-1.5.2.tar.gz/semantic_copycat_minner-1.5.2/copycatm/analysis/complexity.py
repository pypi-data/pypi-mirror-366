"""
Cyclomatic complexity analysis for CopycatM.
"""

from typing import Dict, Any, List
from radon.complexity import cc_visit
from radon.visitors import ComplexityVisitor


class ComplexityAnalyzer:
    """Analyze cyclomatic complexity of code."""
    
    def analyze(self, ast_tree: Any, language: str) -> Dict[str, Any]:
        """Analyze complexity of the AST tree."""
        # For Python, use radon if we have the code
        if language == "python" and hasattr(ast_tree, 'code'):
            return self.analyze_python_code(ast_tree.code)
        
        # For other languages or when code is not available, use AST-based analysis
        complexity_metrics = {
            "max_complexity": 0,
            "average_complexity": 0.0,
            "total_functions": 0,
            "complex_functions": 0,  # Functions above threshold
            "complexity_distribution": {},
            "cyclomatic_complexity": 0  # Add this for compatibility
        }
        
        # Calculate complexity from AST
        if hasattr(ast_tree, 'root'):
            complexity = self._calculate_ast_complexity(ast_tree.root)
            complexity_metrics["cyclomatic_complexity"] = complexity
            complexity_metrics["max_complexity"] = complexity
            complexity_metrics["average_complexity"] = float(complexity)
        
        return complexity_metrics
    
    def calculate_function_complexity(self, function_node: Any) -> int:
        """Calculate cyclomatic complexity for a single function."""
        # This would traverse the function AST and count:
        # - if statements
        # - while loops
        # - for loops
        # - case statements
        # - logical operators (&&, ||)
        # - catch blocks
        # - etc.
        
        # Placeholder implementation
        return 1
    
    def _calculate_ast_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity from AST node."""
        complexity = 1  # Base complexity
        
        decision_types = {
            'if_statement', 'while_statement', 'for_statement',
            'case_statement', 'conditional_expression', 'try_statement',
            'elif_clause', 'except_clause', 'or', 'and',
            'for_in_statement', 'do_statement', 'switch_statement'
        }
        
        def count_decisions(n):
            count = 0
            node_type = getattr(n, 'type', '')
            
            if node_type in decision_types:
                count += 1
            
            # Handle children - both list and child() method
            if hasattr(n, 'children'):
                for child in n.children:
                    count += count_decisions(child)
            elif hasattr(n, 'child_count'):
                for i in range(n.child_count):
                    child = n.child(i)
                    if child:
                        count += count_decisions(child)
            
            return count
        
        return complexity + count_decisions(node)
    
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code using radon."""
        try:
            results = cc_visit(code)
            
            if not results:
                return {
                    "max_complexity": 0,
                    "average_complexity": 0.0,
                    "total_functions": 0,
                    "complex_functions": 0,
                    "complexity_distribution": {}
                }
            
            complexities = [result.complexity for result in results]
            max_complexity = max(complexities)
            avg_complexity = sum(complexities) / len(complexities)
            
            # Build distribution
            distribution = {}
            for complexity in complexities:
                distribution[complexity] = distribution.get(complexity, 0) + 1
            
            return {
                "max_complexity": max_complexity,
                "average_complexity": avg_complexity,
                "total_functions": len(results),
                "complex_functions": len([c for c in complexities if c > 3]),
                "complexity_distribution": distribution,
                "cyclomatic_complexity": max_complexity  # Add for compatibility
            }
            
        except Exception:
            # Fallback to basic analysis
            return {
                "max_complexity": 1,
                "average_complexity": 1.0,
                "total_functions": 1,
                "complex_functions": 0,
                "complexity_distribution": {1: 1}
            } 