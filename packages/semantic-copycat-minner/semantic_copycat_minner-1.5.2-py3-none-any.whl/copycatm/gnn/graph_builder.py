"""
Graph builder for converting AST nodes to graph representations.

This module converts code AST structures into graph representations
suitable for Graph Neural Network analysis.
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import hashlib


class CodeGraphBuilder:
    """Builds graph representations from AST nodes for GNN analysis."""
    
    def __init__(self):
        self.node_types = {
            'function_def': 'function',
            'class_def': 'class',
            'if_statement': 'control',
            'for_statement': 'control',
            'while_statement': 'control',
            'assignment': 'assignment',
            'call': 'call',
            'variable': 'variable',
            'literal': 'literal',
            'operator': 'operator',
            'import': 'import',
            'return': 'return',
            'default': 'node'
        }
    
    def build_graph_from_ast(self, ast_tree: Any, language: str) -> nx.Graph:
        """
        Convert AST tree to NetworkX graph representation.
        
        Args:
            ast_tree: AST tree from parser
            language: Programming language
            
        Returns:
            NetworkX graph with node and edge features
        """
        graph = nx.Graph()
        
        if hasattr(ast_tree, 'root'):
            self._process_node(ast_tree.root, graph, language, parent_id=None)
        
        return graph
    
    def _process_node(self, node: Any, graph: nx.Graph, language: str, 
                     parent_id: Optional[str] = None) -> str:
        """
        Process AST node and add to graph.
        
        Args:
            node: AST node
            graph: NetworkX graph
            language: Programming language
            parent_id: Parent node ID
            
        Returns:
            Node ID for this node
        """
        if not hasattr(node, 'type'):
            return None
        
        # Create node ID
        node_id = self._generate_node_id(node, language)
        
        # Determine node type
        node_type = self.node_types.get(node.type, self.node_types['default'])
        
        # Extract node features
        features = self._extract_node_features(node, language)
        
        # Add node to graph
        graph.add_node(node_id, 
                      type=node_type,
                      ast_type=node.type,
                      language=language,
                      features=features,
                      text=getattr(node, 'text', ''),
                      line_start=getattr(node, 'start_point', [0, 0])[0] if hasattr(node, 'start_point') else 0,
                      line_end=getattr(node, 'end_point', [0, 0])[0] if hasattr(node, 'end_point') else 0)
        
        # Add edge to parent
        if parent_id:
            graph.add_edge(parent_id, node_id, edge_type='parent_child')
        
        # Process children
        if hasattr(node, 'children'):
            for child in node.children:
                child_id = self._process_node(child, graph, language, node_id)
                if child_id:
                    graph.add_edge(node_id, child_id, edge_type='parent_child')
        
        return node_id
    
    def _generate_node_id(self, node: Any, language: str) -> str:
        """Generate unique node ID."""
        node_hash = hashlib.md5(
            f"{language}:{node.type}:{getattr(node, 'text', '')}".encode()
        ).hexdigest()[:8]
        return f"{language}_{node.type}_{node_hash}"
    
    def _extract_node_features(self, node: Any, language: str) -> Dict[str, Any]:
        """Extract features from AST node."""
        features = {
            'type': node.type,
            'text_length': len(getattr(node, 'text', '')),
            'has_children': hasattr(node, 'children') and len(node.children) > 0,
            'is_leaf': not hasattr(node, 'children') or len(node.children) == 0,
            'language': language
        }
        
        # Add language-specific features
        if language == 'python':
            features.update(self._extract_python_features(node))
        elif language in ['javascript', 'typescript']:
            features.update(self._extract_js_features(node))
        
        return features
    
    def _extract_python_features(self, node: Any) -> Dict[str, Any]:
        """Extract Python-specific features."""
        features = {}
        
        if node.type == 'function_def':
            features['is_function'] = True
            features['function_name'] = getattr(node, 'text', '').split('(')[0] if '(' in getattr(node, 'text', '') else ''
        elif node.type == 'class_def':
            features['is_class'] = True
            features['class_name'] = getattr(node, 'text', '').split('(')[0] if '(' in getattr(node, 'text', '') else ''
        elif node.type in ['if_statement', 'for_statement', 'while_statement']:
            features['is_control_flow'] = True
        elif node.type == 'call':
            features['is_function_call'] = True
        elif node.type == 'assignment':
            features['is_assignment'] = True
        
        return features
    
    def _extract_js_features(self, node: Any) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript-specific features."""
        features = {}
        
        if node.type == 'function_declaration':
            features['is_function'] = True
        elif node.type == 'class_declaration':
            features['is_class'] = True
        elif node.type in ['if_statement', 'for_statement', 'while_statement']:
            features['is_control_flow'] = True
        elif node.type == 'call_expression':
            features['is_function_call'] = True
        elif node.type == 'assignment_expression':
            features['is_assignment'] = True
        
        return features
    
    def get_graph_features(self, graph: nx.Graph) -> Dict[str, Any]:
        """
        Extract graph-level features for similarity analysis.
        
        Args:
            graph: NetworkX graph
            
        Returns:
            Dictionary of graph features
        """
        features = {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'node_types': {},
            'avg_degree': 0,
            'density': 0,
            'diameter': 0,
            'avg_clustering': 0
        }
        
        if graph.number_of_nodes() > 0:
            # Count node types
            for node, data in graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                features['node_types'][node_type] = features['node_types'].get(node_type, 0) + 1
            
            # Calculate graph metrics
            features['avg_degree'] = sum(dict(graph.degree()).values()) / graph.number_of_nodes()
            features['density'] = nx.density(graph)
            
            if nx.is_connected(graph):
                features['diameter'] = nx.diameter(graph)
            
            features['avg_clustering'] = nx.average_clustering(graph)
        
        return features 