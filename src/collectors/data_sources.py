"""Base data source definitions - Enhanced with all record types"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecordType(Enum):
    """Financial event categories — what happened to the stock?"""
    STOCK_GOES_UP = "Stock Goes Up"
    STOCK_GOES_DOWN = "Stock Goes Down"
    GOOD_FORECAST = "Good Forecast"
    BAD_FORECAST = "Bad Forecast"
    ANALYST_SAYS_BUY = "Analyst Says Buy"
    ANALYST_SAYS_SELL = "Analyst Says Sell"
    PAYS_MORE_DIVIDENDS = "Pays More Dividends"
    BUYING_BACK_STOCK = "Buying Back Stock"
    COMPANY_MERGER = "Company Merger"
    GOVERNMENT_ACTION = "Government Action"
    OTHER = "Other"


class Severity(Enum):
    """Record severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class DataRecord:
    """Standardized data record structure"""
    
    # Identifiers
    report_id: str
    platform: str  # source platform identifier
    
    # Target Information
    target_domain: str
    target_company: str
    target_program: str
    
    # Record Details
    record_type: str
    severity: str
    priority_score: float
    
    # Technical Details
    technology_stack: List[str] = field(default_factory=list)
    endpoint: str = ""
    http_method: str = "GET"
    category: str = "web"  # web, api, mobile, cloud, other
    
    # Context
    description: str = ""
    details: List[str] = field(default_factory=list)
    impact: str = ""
    remediation: str = ""
    
    # Metadata
    created_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    reward_amount: float = 0.0
    source_quality: int = 0
    
    # Additional Features
    authentication_required: bool = False
    privileges_required: str = "none"  # none, low, high
    user_interaction: bool = False
    complexity: str = "medium"  # low, medium, high
    
    # Tags
    tags: List[str] = field(default_factory=list)
    domain_category: str = ""
    category_id: int = 0
    
    # Raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'platform': self.platform,
            'target_domain': self.target_domain,
            'target_company': self.target_company,
            'target_program': self.target_program,
            'record_type': self.record_type,
            'severity': self.severity,
            'priority_score': self.priority_score,
            'technology_stack': self.technology_stack,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'category': self.category,
            'description': self.description,
            'details': self.details,
            'impact': self.impact,
            'remediation': self.remediation,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'reward_amount': self.reward_amount,
            'source_quality': self.source_quality,
            'authentication_required': self.authentication_required,
            'privileges_required': self.privileges_required,
            'user_interaction': self.user_interaction,
            'complexity': self.complexity,
            'tags': self.tags,
            'domain_category': self.domain_category,
            'category_id': self.category_id
        }


class DataCollector:
    """Base class for data collection with enhanced record detection"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.reports = []
        self.cache_dir = cache_dir
        self._setup_cache()
    
    def _setup_cache(self):
        """Setup caching directory"""
        from pathlib import Path
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def collect(self, limit: int = 1000) -> List[DataRecord]:
        """Collect data records"""
        raise NotImplementedError("Subclasses must implement collect()")
    
    def normalize(self, raw_data: Dict[str, Any]) -> Optional[DataRecord]:
        """Normalize raw data into standard format"""
        raise NotImplementedError("Subclasses must implement normalize()")
    
    def save_cache(self, reports: List[DataRecord], filename: str):
        """Save reports to cache"""
        import pickle
        from pathlib import Path
        
        cache_file = Path(self.cache_dir) / filename
        with open(cache_file, 'wb') as f:
            pickle.dump(reports, f)
        
        print(f"Cached {len(reports)} reports to {cache_file}")
    
    def load_cache(self, filename: str) -> Optional[List[DataRecord]]:
        """Load reports from cache"""
        import pickle
        from pathlib import Path
        
        cache_file = Path(self.cache_dir) / filename
        
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'rb') as f:
            reports = pickle.load(f)
        
        print(f"Loaded {len(reports)} reports from cache")
        return reports
    
    def extract_record_type(self, text: str, weakness_name: str = "", category_id: int = 0) -> str:
        """Extract record type from text"""
        
        text_lower = text.lower()
        
        type_keywords = {
            'Stock Goes Up': ['stock_up', 'good_earnings'],
            'Stock Goes Down': ['stock_down', 'bad_earnings'],
            'Good Forecast': ['good_forecast', 'outlook_raised'],
            'Bad Forecast': ['bad_forecast', 'outlook_lowered'],
            'Analyst Says Buy': ['analyst_buy', 'rating_upgrade'],
            'Analyst Says Sell': ['analyst_sell', 'rating_downgrade'],
            'Pays More Dividends': ['dividend_increase', 'more_dividends'],
            'Buying Back Stock': ['buyback', 'share_repurchase'],
            'Company Merger': ['merger', 'acquisition'],
            'Government Action': ['government', 'regulation'],
        }
        
        for rec_type, keywords in type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return rec_type
        
        return 'Other'
    
    def map_severity_to_score(self, severity: str) -> float:
        """Map severity to numeric score"""
        
        severity_mapping = {
            'critical': 9.5,
            'high': 7.5,
            'medium': 5.0,
            'low': 3.0,
            'none': 0.0
        }
        
        return severity_mapping.get(severity.lower(), 5.0)
    
    def extract_technologies(self, text: str) -> List[str]:
        """Extract technology stack from text - enhanced version"""
        
        tech_indicators = {
            # Frontend Frameworks
            'React': ['react', 'reactjs', 'react.js', 'react native'],
            'Angular': ['angular', 'angularjs', 'angular.js'],
            'Vue.js': ['vue', 'vuejs', 'vue.js', 'nuxt'],
            'Svelte': ['svelte', 'sveltekit'],
            'Next.js': ['next.js', 'nextjs', 'next js'],
            
            # Backend Frameworks
            'Node.js': ['node', 'nodejs', 'node.js', 'express', 'nestjs', 'koa'],
            'Python': ['python', 'django', 'flask', 'fastapi', 'tornado'],
            'Ruby': ['ruby', 'rails', 'ruby on rails', 'sinatra'],
            'PHP': ['php', 'laravel', 'symfony', 'wordpress', 'codeigniter'],
            'Java': ['java', 'spring', 'spring boot', 'struts', 'hibernate'],
            'Go': ['golang', 'go ', 'gin', 'echo'],
            '.NET': ['asp.net', '.net', 'dotnet', 'c#'],
            
            # APIs
            'GraphQL': ['graphql', 'graph ql', 'apollo'],
            'REST': ['rest api', 'restful', 'rest '],
            'gRPC': ['grpc', 'protocol buffers'],
            'WebSocket': ['websocket', 'ws://'],
            
            # Databases
            'MongoDB': ['mongodb', 'mongo'],
            'PostgreSQL': ['postgresql', 'postgres', 'psql'],
            'MySQL': ['mysql', 'mariadb'],
            'Redis': ['redis'],
            'Cassandra': ['cassandra'],
            'DynamoDB': ['dynamodb', 'dynamo'],
            'Elasticsearch': ['elasticsearch', 'elastic'],
            
            # Cloud
            'AWS': ['aws', 'amazon web services', 's3', 'ec2', 'lambda', 'cloudfront'],
            'Azure': ['azure', 'microsoft azure'],
            'Google Cloud': ['gcp', 'google cloud', 'firebase'],
            'Cloudflare': ['cloudflare', 'cf-'],
            
            # Containers & Orchestration
            'Docker': ['docker', 'container'],
            'Kubernetes': ['kubernetes', 'k8s', 'kubectl'],
            
            # Web Servers
            'Nginx': ['nginx'],
            'Apache': ['apache', 'httpd'],
            'IIS': ['iis', 'internet information services'],
            
            # Financial Data
            'Annual Report': ['10k', 'annual_report'],
            'Quarterly Report': ['10q', 'quarterly_report'],
            'SEC Filing': ['sec', 'edgar', 'filing'],
            
            # Message Queues
            'RabbitMQ': ['rabbitmq', 'rabbit mq'],
            'Kafka': ['kafka', 'apache kafka'],
            
            # Mobile
            'iOS': ['ios', 'swift', 'objective-c'],
            'Android': ['android', 'kotlin'],
            'React Native': ['react native'],
            'Flutter': ['flutter', 'dart'],
        }
        
        text_lower = text.lower()
        technologies = []
        
        for tech, indicators in tech_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                technologies.append(tech)
        
        return list(set(technologies))
