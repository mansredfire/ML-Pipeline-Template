"""Remove duplicate data records"""

from typing import List, Set
from ..collectors.data_sources import DataRecord


class Deduplicator:
    """Remove duplicate data records"""
    
    def __init__(self):
        self.duplicates_removed = 0
    
    def remove_duplicates(self, reports: List[DataRecord]) -> List[DataRecord]:
        """
        Remove duplicate reports based on report_id
        
        Args:
            reports: List of reports (may contain duplicates)
            
        Returns:
            List of unique reports
        """
        
        seen_ids: Set[str] = set()
        unique_reports = []
        
        for report in reports:
            report_id = getattr(report, 'report_id', None)
            
            if report_id and report_id not in seen_ids:
                seen_ids.add(report_id)
                unique_reports.append(report)
            elif not report_id:
                # If no report_id, keep it anyway (shouldn't happen with normalized data)
                unique_reports.append(report)
            else:
                self.duplicates_removed += 1
        
        if self.duplicates_removed > 0:
            print(f"Removed {self.duplicates_removed} duplicate reports")
        
        return unique_reports
    
    def deduplicate(self, reports: List[DataRecord]) -> List[DataRecord]:
        """Alias for remove_duplicates - for compatibility with TrainingPipeline"""
        return self.remove_duplicates(reports)
    
    def remove_similar_duplicates(self, reports: List[DataRecord], 
                                   threshold: float = 0.9) -> List[DataRecord]:
        """
        Remove reports that are very similar (fuzzy matching)
        
        Args:
            reports: List of reports
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of unique reports
        """
        
        # Simple implementation - can be enhanced with fuzzy matching
        # For now, just check title similarity
        
        unique_reports = []
        seen_titles: Set[str] = set()
        
        for report in reports:
            title = getattr(report, 'title', '')
            title_lower = title.lower() if title else ""
            
            if title_lower and title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_reports.append(report)
            elif not title_lower:
                # Keep reports without titles
                unique_reports.append(report)
            else:
                self.duplicates_removed += 1
        
        return unique_reports
