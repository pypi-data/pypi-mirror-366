"""
GNN-based similarity detector for code analysis.

This module integrates GNN similarity detection with the existing
analysis pipeline to provide advanced code similarity analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

from .graph_builder import CodeGraphBuilder
from .gnn_model import CodeGNNModel, SimpleGNNModel

logger = logging.getLogger(__name__)


class GNNSimilarityDetector:
    """GNN-based similarity detector for code analysis."""
    
    def __init__(self, use_pytorch: bool = False):
        """
        Initialize GNN similarity detector.
        
        Args:
            use_pytorch: Whether to use PyTorch-based GNN (requires torch-geometric)
        """
        self.graph_builder = CodeGraphBuilder()
        self.use_pytorch = use_pytorch
        
        if use_pytorch:
            try:
                self.gnn_model = CodeGNNModel()
                logger.debug("GNN: Using PyTorch-based model")
            except ImportError:
                logger.debug("GNN: PyTorch not available, falling back to simple model")
                self.gnn_model = SimpleGNNModel()
                self.use_pytorch = False
        else:
            self.gnn_model = SimpleGNNModel()
            logger.debug("GNN: Using simple graph-based model")
    
    def analyze_code_similarity(self, ast_tree1: Any, ast_tree2: Any, 
                              language1: str, language2: str) -> Dict[str, Any]:
        """
        Analyze similarity between two code ASTs using GNN.
        
        Args:
            ast_tree1: First AST tree
            ast_tree2: Second AST tree
            language1: Language of first code
            language2: Language of second code
            
        Returns:
            Dictionary with similarity analysis results
        """
        # Build graphs from ASTs
        graph1 = self.graph_builder.build_graph_from_ast(ast_tree1, language1)
        graph2 = self.graph_builder.build_graph_from_ast(ast_tree2, language2)
        
        # Extract graph features
        features1 = self.graph_builder.get_graph_features(graph1)
        features2 = self.graph_builder.get_graph_features(graph2)
        
        # Compute similarity
        if self.use_pytorch:
            similarity_score = self.gnn_model.predict_similarity(graph1, graph2)
        else:
            similarity_score = self.gnn_model.compute_graph_similarity(graph1, graph2)
        
        # Analyze structural differences
        structural_analysis = self._analyze_structural_differences(graph1, graph2)
        
        return {
            'similarity_score': similarity_score,
            'graph_features_1': features1,
            'graph_features_2': features2,
            'structural_analysis': structural_analysis,
            'gnn_model_type': 'pytorch' if self.use_pytorch else 'simple',
            'graph1_nodes': graph1.number_of_nodes(),
            'graph2_nodes': graph2.number_of_nodes(),
            'graph1_edges': graph1.number_of_edges(),
            'graph2_edges': graph2.number_of_edges()
        }
    
    def _analyze_structural_differences(self, graph1: nx.Graph, 
                                      graph2: nx.Graph) -> Dict[str, Any]:
        """
        Analyze structural differences between two graphs.
        
        Args:
            graph1: First graph
            graph2: Second graph
            
        Returns:
            Dictionary with structural analysis
        """
        analysis = {
            'node_type_distribution_1': {},
            'node_type_distribution_2': {},
            'structural_metrics': {},
            'common_patterns': [],
            'unique_patterns_1': [],
            'unique_patterns_2': []
        }
        
        # Analyze node type distributions
        for node, data in graph1.nodes(data=True):
            node_type = data.get('type', 'unknown')
            analysis['node_type_distribution_1'][node_type] = \
                analysis['node_type_distribution_1'].get(node_type, 0) + 1
        
        for node, data in graph2.nodes(data=True):
            node_type = data.get('type', 'unknown')
            analysis['node_type_distribution_2'][node_type] = \
                analysis['node_type_distribution_2'].get(node_type, 0) + 1
        
        # Compute structural metrics
        analysis['structural_metrics'] = {
            'density_diff': abs(nx.density(graph1) - nx.density(graph2)),
            'avg_degree_diff': abs(
                sum(dict(graph1.degree()).values()) / max(graph1.number_of_nodes(), 1) -
                sum(dict(graph2.degree()).values()) / max(graph2.number_of_nodes(), 1)
            ),
            'clustering_diff': abs(
                nx.average_clustering(graph1) - nx.average_clustering(graph2)
            )
        }
        
        # Find common and unique patterns
        patterns1 = self._extract_patterns(graph1)
        patterns2 = self._extract_patterns(graph2)
        
        analysis['common_patterns'] = list(set(patterns1) & set(patterns2))
        analysis['unique_patterns_1'] = list(set(patterns1) - set(patterns2))
        analysis['unique_patterns_2'] = list(set(patterns2) - set(patterns1))
        
        return analysis
    
    def _extract_patterns(self, graph: nx.Graph) -> List[str]:
        """
        Extract structural patterns from graph.
        
        Args:
            graph: NetworkX graph
            
        Returns:
            List of pattern strings
        """
        patterns = []
        
        # Extract function patterns
        function_nodes = [n for n, d in graph.nodes(data=True) 
                         if d.get('type') == 'function']
        if function_nodes:
            patterns.append(f"functions_{len(function_nodes)}")
        
        # Extract class patterns
        class_nodes = [n for n, d in graph.nodes(data=True) 
                      if d.get('type') == 'class']
        if class_nodes:
            patterns.append(f"classes_{len(class_nodes)}")
        
        # Extract control flow patterns
        control_nodes = [n for n, d in graph.nodes(data=True) 
                        if d.get('type') == 'control']
        if control_nodes:
            patterns.append(f"control_flow_{len(control_nodes)}")
        
        # Extract call patterns
        call_nodes = [n for n, d in graph.nodes(data=True) 
                     if d.get('type') == 'call']
        if call_nodes:
            patterns.append(f"function_calls_{len(call_nodes)}")
        
        return patterns
    
    def get_similarity_hash(self, graph: nx.Graph) -> str:
        """
        Generate a similarity hash for a graph.
        
        Args:
            graph: NetworkX graph
            
        Returns:
            Similarity hash string
        """
        features = self.graph_builder.get_graph_features(graph)
        
        # Create hash from features
        import hashlib
        feature_str = f"{features['num_nodes']}_{features['num_edges']}_{features['avg_degree']:.3f}_{features['density']:.3f}"
        
        # Add node type distribution
        for node_type, count in features['node_types'].items():
            feature_str += f"_{node_type}_{count}"
        
        return hashlib.md5(feature_str.encode()).hexdigest()[:16]
    
    def compare_multiple_graphs(self, graphs: List[nx.Graph]) -> Dict[str, float]:
        """
        Compare multiple graphs and return similarity matrix.
        
        Args:
            graphs: List of NetworkX graphs
            
        Returns:
            Dictionary with similarity scores
        """
        similarities = {}
        
        for i, graph1 in enumerate(graphs):
            for j, graph2 in enumerate(graphs):
                if i < j:  # Only compare each pair once
                    key = f"graph_{i}_vs_graph_{j}"
                    
                    if self.use_pytorch:
                        similarity = self.gnn_model.predict_similarity(graph1, graph2)
                    else:
                        similarity = self.gnn_model.compute_graph_similarity(graph1, graph2)
                    
                    similarities[key] = similarity
        
        return similarities 