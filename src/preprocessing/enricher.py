"""Data enricher for data records"""

from typing import List
from ..collectors.data_sources import DataRecord


class Enricher:
    """Enrich data records with additional computed fields"""
    
    def __init__(self):
        """Initialize the enricher"""
        pass
    
    def enrich_reports(self, reports: List[DataRecord]) -> List[DataRecord]:
        """
        Enrich a list of data records
        
        Args:
            reports: List of DataRecord objects
            
        Returns:
            List of enriched reports
        """
        enriched = []
        
        for report in reports:
            enriched_report = self.enrich_report(report)
            enriched.append(enriched_report)
        
        return enriched
    
    def enrich(self, reports: List[DataRecord]) -> List[DataRecord]:
        """
        Alias for enrich_reports for compatibility
        
        Args:
            reports: List of DataRecord objects
            
        Returns:
            List of enriched reports
        """
        return self.enrich_reports(reports)
    
    def enrich_report(self, report: DataRecord) -> DataRecord:
        """
        Enrich a single data record with computed fields
        
        Args:
            report: DataRecord object
            
        Returns:
            Enriched DataRecord
        """
        # Calculate risk score
        report.risk_score = self.calculate_risk_score(report)
        
        # Calculate complexity score
        report.complexity_score = self.calculate_complexity(report)
        
        # Calculate impact score
        report.impact_score = self.calculate_impact(report)
        
        # Calculate quality score
        report.quality_score = self.calculate_quality_score(report)
        
        # Add domain category if not present
        if not hasattr(report, 'domain_category') or not report.domain_category:
            report.domain_category = self._infer_domain_category(report)
        
        # Add category ID if not present
        if not hasattr(report, 'category_id') or not report.category_id:
            report.category_id = self._infer_category_id(report)
        
        return report
    
    def calculate_risk_score(self, report: DataRecord) -> float:
        """
        Calculate overall risk score (0-10)
        
        Args:
            report: DataRecord object
            
        Returns:
            Risk score from 0 to 10
        """
        # Base score from severity
        severity_scores = {
            'critical': 9.0,
            'high': 7.0,
            'medium': 5.0,
            'low': 3.0,
            'none': 1.0
        }
        
        severity = getattr(report, 'severity', 'medium').lower()
        base_score = severity_scores.get(severity, 5.0)
        
        # Adjust based on reward amount
        reward = getattr(report, 'reward_amount', 0)
        if reward > 10000:
            base_score += 1.0
        elif reward > 5000:
            base_score += 0.5
        
        # Cap at 10
        return min(base_score, 10.0)
    
    def calculate_complexity(self, report: DataRecord) -> float:
        """
        Calculate complexity score (0-10)
        
        Args:
            report: DataRecord object
            
        Returns:
            Complexity score from 0 to 10
        """
        score = 5.0  # Base score
        
        # Authentication required reduces complexity
        if getattr(report, 'authentication_required', False):
            score -= 2.0
        
        # User interaction required reduces complexity
        if getattr(report, 'user_interaction', False):
            score -= 1.5
        
        # Complexity affects complexity
        complexity = getattr(report, 'complexity', 'medium')
        if complexity == 'low':
            score += 2.0
        elif complexity == 'high':
            score -= 2.0
        
        # Privileges required reduces complexity
        privileges = getattr(report, 'privileges_required', 'none')
        if privileges == 'admin':
            score -= 3.0
        elif privileges == 'user':
            score -= 1.0
        
        # Ensure score is within bounds
        return max(0.0, min(score, 10.0))
    
    def calculate_impact(self, report: DataRecord) -> float:
        """
        Calculate impact score (0-10)
        
        Args:
            report: DataRecord object
            
        Returns:
            Impact score from 0 to 10
        """
        # Use priority score if available
        priority = getattr(report, 'priority_score', None)
        if priority:
            return min(priority, 10.0)
        
        # Otherwise estimate from severity
        severity_impacts = {
            'critical': 9.5,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5,
            'none': 0.5
        }
        
        severity = getattr(report, 'severity', 'medium').lower()
        return severity_impacts.get(severity, 5.0)
    
    def calculate_quality_score(self, report: DataRecord) -> float:
        """
        Calculate report quality score (0-1)
        
        Args:
            report: DataRecord object
            
        Returns:
            Quality score from 0 to 1
        """
        score = 0.0
        
        # Title exists and is substantial
        title = getattr(report, 'title', '')
        if title and len(title) > 10:
            score += 0.2
        
        # Description exists and is substantial
        description = getattr(report, 'description', '')
        if description and len(description) > 50:
            score += 0.3
        elif description and len(description) > 20:
            score += 0.15
        
        # Record type is specified
        rec_type = getattr(report, 'record_type', '')
        if rec_type and rec_type != 'Unknown':
            score += 0.2
        
        # Severity is specified
        severity = getattr(report, 'severity', '')
        if severity and severity != 'none':
            score += 0.15
        
        # Has reward information
        reward = getattr(report, 'reward_amount', 0)
        if reward > 0:
            score += 0.15
        
        return min(score, 1.0)
    
    def _infer_domain_category(self, report: DataRecord) -> str:
        """
        Infer domain category from record type
        
        Args:
            report: DataRecord object
            
        Returns:
            domain category string
        """
        rec_type = getattr(report, 'record_type', '').lower()
        
        category_mapping = {
            'stock goes up': 'Good News',
            'stock goes down': 'Bad News',
            'good forecast': 'Good News',
            'bad forecast': 'Bad News',
            'analyst says buy': 'Good News',
            'analyst says sell': 'Bad News',
            'pays more dividends': 'Money Back to Investors',
            'buying back stock': 'Money Back to Investors',
            'company merger': 'Big Company Change',
            'government action': 'Government News',
        }
        
        for key, category in category_mapping.items():
            if key in rec_type:
                return category
        
        return 'Other'
    
    def _infer_category_id(self, report: DataRecord) -> str:
        """
        Infer category ID from record type
        
        Args:
            report: DataRecord object
            
        Returns:
            category ID string
        """
        rec_type = getattr(report, 'record_type', '').lower()
        
        id_mapping = {
            'stock goes up': 'CAT-001',
            'stock goes down': 'CAT-002',
            'good forecast': 'CAT-003',
            'bad forecast': 'CAT-004',
            'analyst says buy': 'CAT-005',
            'analyst says sell': 'CAT-006',
            'pays more dividends': 'CAT-007',
            'buying back stock': 'CAT-008',
            'company merger': 'CAT-009',
            'government action': 'CAT-010',
        }
        
        for key, cwe in id_mapping.items():
            if key in rec_type:
                return cwe
        
        return 'CAT-000'


# Alias for backward compatibility
class DataEnricher(Enricher):
    """Alias for Enricher class for backward compatibility"""
    pass
