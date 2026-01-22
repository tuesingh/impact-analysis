from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class RegulatoryItem(Base):
    __tablename__ = 'regulatory_items'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    type = Column(String(50))
    published_at = Column(DateTime)
    title = Column(String(500))
    summary_raw = Column(Text)
    full_text = Column(Text, nullable=True)
    url = Column(String(500), unique=True)
    tags = Column(Text)
    entities = Column(Text)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    
    is_relevant = Column(Integer, nullable=True)
    relevance_reason = Column(Text, nullable=True)
    business_area = Column(String(100), nullable=True)
    
    impact_severity = Column(Integer, nullable=True)
    impact_time_sensitivity = Column(Integer, nullable=True)
    impact_operational_effort = Column(Integer, nullable=True)
    impact_customer = Column(Integer, nullable=True)
    impact_enforcement_risk = Column(Integer, nullable=True)
    impact_overall = Column(String(20), nullable=True)
    
    executive_summary = Column(Text, nullable=True)
    tasks = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'source': self.source,
            'type': self.type,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'title': self.title,
            'summary_raw': self.summary_raw,
            'url': self.url,
            'tags': json.loads(self.tags) if self.tags else [],
            'entities': json.loads(self.entities) if self.entities else [],
        }

class DataStore:
    def __init__(self, db_url: str = 'sqlite:///./regulatory_items.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_items(self, items: List[Dict]) -> List[int]:
        added_ids = []
        for item_dict in items:
            try:
                existing = self.session.query(RegulatoryItem).filter_by(url=item_dict['url']).first()
                if existing:
                    continue
                
                item = RegulatoryItem(
                    source=item_dict['source'],
                    type=item_dict['type'],
                    published_at=datetime.fromisoformat(item_dict['published_at']) if isinstance(item_dict['published_at'], str) else item_dict['published_at'],
                    title=item_dict['title'],
                    summary_raw=item_dict['summary_raw'],
                    url=item_dict['url'],
                    tags=json.dumps(item_dict.get('tags', [])),
                    entities=json.dumps(item_dict.get('entities', [])),
                )
                self.session.add(item)
                self.session.flush()
                added_ids.append(item.id)
            except Exception as e:
                logger.error(f"Error adding item: {e}")
        
        self.session.commit()
        return added_ids
    
    def get_unanalyzed_items(self, limit: int = 50) -> List[RegulatoryItem]:
        return self.session.query(RegulatoryItem).filter(RegulatoryItem.is_relevant == None).order_by(RegulatoryItem.published_at.desc()).limit(limit).all()
    
    def update_analysis(self, item_id: int, analysis: Dict):
        item = self.session.query(RegulatoryItem).filter_by(id=item_id).first()
        if not item:
            return
        
        item.is_relevant = 1 if analysis.get('relevant') else 0
        item.relevance_reason = analysis.get('relevance_reason')
        item.business_area = analysis.get('business_area')
        item.impact_severity = analysis.get('impact_severity')
        item.impact_time_sensitivity = analysis.get('impact_time_sensitivity')
        item.impact_operational_effort = analysis.get('impact_operational_effort')
        item.impact_customer = analysis.get('impact_customer')
        item.impact_enforcement_risk = analysis.get('impact_enforcement_risk')
        item.impact_overall = analysis.get('impact_overall')
        item.executive_summary = analysis.get('executive_summary')
        item.tasks = json.dumps(analysis.get('tasks', []))
        
        self.session.commit()
    
    def get_recent_items(self, days: int = 7) -> List[RegulatoryItem]:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.session.query(RegulatoryItem).filter(RegulatoryItem.published_at >= cutoff).all()
    
    def get_high_impact_items(self) -> List[RegulatoryItem]:
        return self.session.query(RegulatoryItem).filter(RegulatoryItem.impact_overall.in_(['High', 'Critical'])).all()
