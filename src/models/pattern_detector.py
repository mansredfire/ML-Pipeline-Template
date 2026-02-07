"""Record chain detection - Enhanced with comprehensive chain patterns"""

from typing import List, Dict, Set, Tuple, Optional
import networkx as nx
import numpy as np
from itertools import combinations
import json
from pathlib import Path


class PatternDetector:
    """
    Detects pattern chains and multi-step pattern paths
    
    Enhanced Features:
    - 25+ pre-defined chain patterns
    - Graph-based chain discovery
    - Modern API/Cloud pattern chains
    - GraphQL chaining chains
    - Financial event cascade patterns
    - Business logic chaining chains
    """
    
    def __init__(self):
        self.chain_patterns = self._build_chain_patterns()
        self.record_graph = None
        self.discovered_chains = []
        self.chain_scores = {}
    
    def _build_chain_patterns(self) -> List[Dict]:
        """Define financial event cascade patterns"""
        
        patterns = [
            # ==================== EARNINGS CASCADES ====================
            {
                'name': 'Bad Results Lead to More Bad News',
                'types': ['Stock Goes Down', 'Analyst Says Sell', 'Bad Forecast'],
                'description': 'When a company misses expectations, analysts lower their ratings, then the company lowers its own predictions',
                'steps': [
                    'Company reports results that are worse than predicted',
                    'Analysts lower their ratings on the stock',
                    'Company says future results will be lower than expected'
                ],
                'impact': 'Stock price drops over several weeks',
                'chain_complexity': 'low',
                'prerequisites': ['Stock Goes Down']
            },
            {
                'name': 'Lower Predictions Threaten Investor Payouts',
                'types': ['Bad Forecast', 'Analyst Says Sell', 'Pays More Dividends'],
                'description': 'When a company lowers predictions, investors worry the company cant keep paying dividends',
                'steps': [
                    'Company lowers its own predictions for the future',
                    'Analysts lower their ratings because things look worse',
                    'The board considers cutting or stopping dividend payments'
                ],
                'impact': 'Investors who want dividends leave, pushing price down more',
                'chain_complexity': 'medium',
                'prerequisites': ['Bad Forecast']
            },
            # ==================== POSITIVE CASCADES ====================
            {
                'name': 'Good Results Lead to More Good News',
                'types': ['Stock Goes Up', 'Analyst Says Buy', 'Good Forecast'],
                'description': 'When a company beats expectations, analysts raise ratings, then the company raises its own predictions',
                'steps': [
                    'Company reports better results than expected',
                    'Analysts raise their ratings and price targets',
                    'Company raises predictions for the rest of the year'
                ],
                'impact': 'Stock price keeps going up',
                'chain_complexity': 'low',
                'prerequisites': ['Stock Goes Up']
            },
            {
                'name': 'Company Shows Confidence by Buying Own Stock',
                'types': ['Stock Goes Up', 'Buying Back Stock', 'Analyst Says Buy'],
                'description': 'After good results, the company buys back its own shares — a sign management believes the stock is cheap',
                'steps': [
                    'Company reports good results',
                    'The board approves buying back stock',
                    'Analysts see the buyback as a sign management believes in the company'
                ],
                'impact': 'Earnings per share go up, stock gets more valuable',
                'chain_complexity': 'low',
                'prerequisites': ['Stock Goes Up']
            },
            # ==================== MERGER CHAINS ====================
            {
                'name': 'Buying Another Company Causes Problems',
                'types': ['Company Merger', 'Bad Forecast', 'Analyst Says Sell'],
                'description': 'When a company buys another company, combining them is harder than expected and predictions get lowered',
                'steps': [
                    'Company announces it is buying another company',
                    'Combining the companies costs more than expected',
                    'Company lowers predictions and analysts lower ratings'
                ],
                'impact': 'Stock price does poorly for 6-12 months',
                'chain_complexity': 'high',
                'prerequisites': ['Company Merger']
            },
            {
                'name': 'Selling a Business Unit Boosts the Stock',
                'types': ['Company Merger', 'Buying Back Stock', 'Analyst Says Buy'],
                'description': 'Company sells part of its business, uses the money to buy back stock, and analysts raise ratings',
                'steps': [
                    'Company sells a part of its business for a good price',
                    'Uses the money to buy back stock',
                    'Analysts raise ratings because the company is more focused'
                ],
                'impact': 'Stock price goes up as the company becomes simpler',
                'chain_complexity': 'medium',
                'prerequisites': ['Company Merger']
            },
            # ==================== REGULATORY CASCADES ====================
            {
                'name': 'Government Approval Opens New Opportunity',
                'types': ['Government Action', 'Analyst Says Buy', 'Good Forecast'],
                'description': 'When the government approves a new product, the company can sell it and make more money',
                'steps': [
                    'Government approves a new product',
                    'Analysts raise ratings because the company can sell to more customers',
                    'Company raises predictions to include money from the new product'
                ],
                'impact': 'Big jump in stock value from new growth',
                'chain_complexity': 'medium',
                'prerequisites': ['Government Action']
            },
            {
                'name': 'Government Problem Causes Chain Reaction',
                'types': ['Government Action', 'Bad Forecast', 'Pays More Dividends'],
                'description': 'A government investigation or new rule hurts the business and reduces how much cash the company makes',
                'steps': [
                    'Government investigation or bad ruling announced',
                    'Company lowers predictions because of costs from government rules',
                    'Dividend payments at risk because the company has less cash'
                ],
                'impact': 'Uncertainty keeps the stock price low',
                'chain_complexity': 'high',
                'prerequisites': ['Government Action']
            },
            # ==================== DIVIDEND CASCADES ====================
            {
                'name': 'Cutting Dividends Makes Everything Worse',
                'types': ['Pays More Dividends', 'Analyst Says Sell', 'Stock Goes Down'],
                'description': 'When a company cuts its dividend, investors panic and sell, revealing even bigger problems',
                'steps': [
                    'Company reduces or stops paying dividends',
                    'Investors who need dividends are forced to sell, analysts lower ratings',
                    'Next quarter shows results are getting even worse'
                ],
                'impact': 'Big stock price drop as investors switch out',
                'chain_complexity': 'medium',
                'prerequisites': ['Pays More Dividends']
            },
            {
                'name': 'Raising Dividends Builds Confidence',
                'types': ['Pays More Dividends', 'Stock Goes Up', 'Analyst Says Buy'],
                'description': 'When a company raises its dividend, it shows the business is healthy, leading to more good news',
                'steps': [
                    'Company increases dividend more than expected',
                    'Next set of results beats the now-higher expectations',
                    'Analysts raise ratings because growth looks solid'
                ],
                'impact': 'Stock gets a higher price because investors trust the company',
                'chain_complexity': 'low',
                'prerequisites': ['Pays More Dividends']
            },
        ]
        
        return patterns

    def detect_chains(self, record_types: List[str]) -> List[Dict]:
        """
        Detect if record types form known pattern chains
        
        Args:
            record_types: List of record types found
            
        Returns:
            List of detected chains with metadata
        """
        
        detected_chains = []
        type_set = set(record_types)
        
        for pattern in self.chain_patterns:
            required_types = set(pattern['types'])
            
            # Check if all required types are present
            if required_types.issubset(type_set):
                # Calculate chain score
                score = self.calculate_chain_score(pattern, record_types)
                
                chain_info = pattern.copy()
                chain_info['relevance_score'] = score
                chain_info['present_types'] = list(required_types)
                chain_info['missing_prerequisites'] = []
                
                detected_chains.append(chain_info)
            
            # Also detect partial chains (useful for recommendations)
            elif len(required_types.intersection(type_set)) >= 2:
                missing = required_types - type_set
                chain_info = pattern.copy()
                chain_info['relevance_score'] = self.calculate_chain_score(pattern, record_types) * 0.5
                chain_info['present_types'] = list(required_types.intersection(type_set))
                chain_info['missing_prerequisites'] = list(missing)
                chain_info['partial'] = True
                
                # Only include partial chains if they're high severity
                if pattern['severity'] in ['critical', 'high']:
                    detected_chains.append(chain_info)
        
        # Sort by relevance score
        detected_chains.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        self.discovered_chains = detected_chains
        
        return detected_chains
    
    def calculate_chain_score(self, chain: Dict, 
                              record_types: List[str]) -> float:
        """
        Calculate relevance score for a chain
        
        Factors:
        - Base severity (40%)
        - Chain likelihood (30%)
        - Attack complexity (20%)
        - Record prevalence (10%)
        
        Returns:
            Score from 0-10
        """
        
        # Base severity score (40% weight)
        severity_scores = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5
        }
        base_score = severity_scores.get(chain['severity'], 5.0) * 0.4
        
        # Likelihood multiplier (30% weight)
        likelihood = chain.get('likelihood', 0.5) * 10 * 0.3
        
        # Complexity factor (20% weight) - inverse relationship
        complexity_scores = {
            'low': 10.0,
            'medium': 6.0,
            'high': 3.0
        }
        complexity = chain.get('chain_complexity', 'medium')
        complexity_score = complexity_scores.get(complexity, 6.0) * 0.2
        
        # Record prevalence (10% weight)
        # More steps = higher complexity
        chain_length = len(chain['types'])
        prevalence_score = (1.0 / (1.0 + (chain_length - 2) * 0.3)) * 10 * 0.1
        
        # Combined score
        total_score = base_score + likelihood + complexity_score + prevalence_score
        
        return round(total_score, 2)
    
    def build_record_graph(self, record_types: List[str]) -> nx.DiGraph:
        """
        Build directed graph of record relationships
        
        Args:
            record_types: List of record types
            
        Returns:
            NetworkX directed graph
        """
        
        G = nx.DiGraph()
        
        # Add nodes for each record
        for rec_type in record_types:
            G.add_node(rec_type)
        
        # Define "can lead to" relationships
        transitions = {
            # From Access Control issues
            'Bad Forecast': ['Government Action', 'CEO or Exec Leaves', 'Board Member Quits', 'Bonus Payment'],
            'Board Member Quits': ['Financial Audit', 'Bad Forecast', 'Investor Dispute'],
            
            # From Authentication issues
            'New CEO': ['Investor Dispute', 'New Leadership', 'Financial Audit'],
            'Stock Split': ['New CEO', 'Investor Dispute', 'Bad Forecast'],
            'New Leadership': ['Investor Dispute', 'Analyst Says Buy'],
            
            # From Type A patterns
            'Stock Goes Down': ['Analyst Says Buy', 'Government Action', 'More Shares Created', 'Investor Dispute'],
            'Stock Goes Up': ['Government Action', 'Pays More Dividends', 'Number Correction'],
            'Spending Too Much': ['Government Action', 'Pays More Dividends', 'Shrinking Profits'],
            'Shrinking Profits': ['Pays More Dividends'],
            
            # From Type C
            'Good Forecast': ['Government Action', 'Pays More Dividends', 'Gaining Customers'],
            'Gaining Customers': ['New Product', 'Government Action', 'Pays More Dividends'],
            
            # From API issues
            'Outside Investor Pushes Changes': ['CEO or Exec Leaves', 'Bonus Payment', 'Bad Forecast'],
            'Credit Problem': ['Bonus Payment', 'Bad Forecast', 'CEO or Exec Leaves'],
            'Money Moves to Other Sectors': ['CEO or Exec Leaves', 'Running Low on Cash'],
            'Bonus Payment': ['Government Action', 'More Shares Created'],
            'Running Low on Cash': ['New CEO', 'CEO or Exec Leaves', 'Investor Dispute'],
            
            # From Corporate Governance
            'CEO or Exec Leaves': ['Bad Forecast', 'Board Member Quits', 'Financial Audit'],
            'Executives Selling Stock': ['CEO or Exec Leaves', 'Financial Audit'],
            
            # From Accounting Events
            'Number Correction': ['Government Action', 'Pays More Dividends'],
            'Government Action': ['Pays More Dividends', 'Government Action'],
            
            # From Revenue Events
            'Sales Drop': ['Pays More Dividends', 'Shrinking Profits'],
            
            # From Analyst Events
            'Analyst Says Buy': ['Investor Dispute', 'CEO or Exec Leaves', 'Board Member Quits'],
            'Government Paperwork': ['Investor Dispute', 'Worse Credit Rating'],
            'Worse Credit Rating': ['Stock Goes Down', 'Government Action'],
            
            # From Compliance Events
            'Broke Loan Rules': ['Government Action', 'More Shares Created'],
            'Correcting Past Numbers': ['New CEO', 'Financial Audit'],
            
            # From Market Signals
            'Executives Buying Stock': ['Good Forecast', 'Government Action'],
        }
        
        # Add edges
        for source, targets in transitions.items():
            if source in record_types:
                for target in targets:
                    if target in record_types:
                        # Weight based on likelihood of transition
                        G.add_edge(source, target, weight=1.0)
        
        self.record_graph = G
        
        return G
    
    def find_pattern_paths(self, record_types: List[str], 
                          max_length: int = 5) -> List[List[str]]:
        """
        Find all possible pattern paths in record graph
        
        Args:
            record_types: List of record types
            max_length: Maximum path length
            
        Returns:
            List of pattern paths (each path is a list of record types)
        """
        
        if self.record_graph is None:
            self.build_record_graph(record_types)
        
        paths = []
        
        # Find all simple paths between all pairs of nodes
        for source in self.record_graph.nodes():
            for target in self.record_graph.nodes():
                if source != target:
                    try:
                        all_paths = nx.all_simple_paths(
                            self.record_graph,
                            source,
                            target,
                            cutoff=max_length
                        )
                        
                        for path in all_paths:
                            if len(path) >= 2:  # At least 2 types
                                paths.append(path)
                    except nx.NetworkXNoPath:
                        continue
        
        # Remove duplicate paths
        unique_paths = []
        seen = set()
        
        for path in paths:
            path_tuple = tuple(path)
            if path_tuple not in seen:
                seen.add(path_tuple)
                unique_paths.append(path)
        
        # Sort by path length and score
        unique_paths.sort(key=lambda p: (len(p), -self._score_path(p)), reverse=True)
        
        return unique_paths
    
    def _score_path(self, path: List[str]) -> float:
        """Score a pattern path based on record types involved"""
        
        high_impact_types = {
            'Pays More Dividends': 10,
            'Investor Dispute': 9,
            'Financial Audit': 9,
            'Stock Goes Up': 8,
            'Gaining Customers': 8,
        }
        
        score = sum(high_impact_types.get(t, 5) for t in path)
        return score / len(path)  # Average score
    
    def rank_chains(self, chains: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Rank detected chains by relevance
        
        Args:
            chains: Optional list of chains to rank (uses self.discovered_chains if None)
            
        Returns:
            Ranked list of chains
        """
        
        if chains is None:
            chains = self.discovered_chains
        
        if not chains:
            return []
        
        # Sort by relevance score
        ranked = sorted(
            chains,
            key=lambda c: (c['relevance_score'], -len(c.get('missing_prerequisites', []))),
            reverse=True
        )
        
        # Add rank
        for i, chain in enumerate(ranked, 1):
            chain['rank'] = i
        
        return ranked
    
    def generate_pattern_scenario(self, chain: Dict) -> str:
        """
        Generate human-readable pattern scenario from chain
        
        Args:
            chain: Chain dictionary
            
        Returns:
            Formatted pattern scenario description
        """
        
        is_partial = chain.get('partial', False)
        
        scenario = f"""
{'[PARTIAL CHAIN] ' if is_partial else ''}ATTACK CHAIN: {chain['name']}
{'='*70}

Severity: {chain['severity'].upper()}
Relevance Score: {chain['relevance_score']}/10
Likelihood: {chain.get('likelihood', 0) * 100:.0f}%
Attack Complexity: {chain.get('chain_complexity', 'medium').upper()}

Description:
{chain['description']}

Attack Steps:
"""
        
        for i, step in enumerate(chain['steps'], 1):
            scenario += f"{i}. {step}\n"
        
        scenario += f"""
Impact:
{chain['impact']}

Required Vulnerabilities:
✓ Present: {', '.join(chain['present_types'])}
"""
        
        if chain.get('missing_prerequisites'):
            scenario += f"✗ Missing: {', '.join(chain['missing_prerequisites'])}\n"
        
        return scenario
    
    def get_chain_statistics(self) -> Dict:
        """Get statistics about detected chains"""
        
        if not self.discovered_chains:
            return {
                'total_chains': 0,
                'complete_chains': 0,
                'partial_chains': 0,
                'critical_chains': 0,
                'high_chains': 0,
                'avg_score': 0.0,
                'max_score': 0.0
            }
        
        complete_chains = [c for c in self.discovered_chains if not c.get('partial', False)]
        partial_chains = [c for c in self.discovered_chains if c.get('partial', False)]
        
        stats = {
            'total_chains': len(self.discovered_chains),
            'complete_chains': len(complete_chains),
            'partial_chains': len(partial_chains),
            'critical_chains': sum(1 for c in self.discovered_chains if c['severity'] == 'critical'),
            'high_chains': sum(1 for c in self.discovered_chains if c['severity'] == 'high'),
            'medium_chains': sum(1 for c in self.discovered_chains if c['severity'] == 'medium'),
            'avg_score': np.mean([c['relevance_score'] for c in self.discovered_chains]),
            'max_score': max(c['relevance_score'] for c in self.discovered_chains),
            'unique_types_in_chains': len(set(
                t for chain in self.discovered_chains 
                for t in chain['present_types']
            ))
        }
        
        return stats
    
    def save(self, filepath: str):
        """Save chain detector state"""
        
        save_path = Path(filepath)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'chain_patterns': self.chain_patterns,
            'discovered_chains': self.discovered_chains,
            'chain_scores': self.chain_scores
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Saved PatternDetector to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load chain detector state"""
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        detector = cls()
        detector.chain_patterns = state['chain_patterns']
        detector.discovered_chains = state['discovered_chains']
        detector.chain_scores = state['chain_scores']
        
        print(f"Loaded PatternDetector from {filepath}")
        
        return detector
