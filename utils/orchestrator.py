import sys
from pathlib import Path

# Add parent directory to path for direct execution
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.connectors import SecRSSConnector, FinraConnector, FedRegConnector
from utils.data_store import DataStore, RegulatoryItem
from utils.ai_analysis import AIAnalysisPipeline
from utils.output_generators import OutputGenerators
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RegulatoryIntelligenceOrchestrator:
    def __init__(self, db_url: str = 'sqlite:///./regulatory_items.db', api_key: str = None):
        self.data_store = DataStore(db_url)
        self.ai_pipeline = AIAnalysisPipeline(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        
        self.sec_connector = SecRSSConnector()
        self.finra_connector = FinraConnector()
        self.fed_reg_connector = FedRegConnector()
    
    def ingest_all_sources(self) -> int:
        logger.info("=== Starting ingest ===")
        all_items = []
        
        sec_items = self.sec_connector.fetch_press_releases()
        logger.info(f"SEC: {len(sec_items)} items")
        all_items.extend(sec_items)
        
        finra_items = self.finra_connector.fetch_notices()
        logger.info(f"FINRA: {len(finra_items)} items")
        all_items.extend(finra_items)
        
        fed_reg_items = self.fed_reg_connector.fetch_regulations()
        logger.info(f"FedReg: {len(fed_reg_items)} items")
        all_items.extend(fed_reg_items)
        
        added_ids = self.data_store.add_items(all_items)
        logger.info(f"Stored {len(added_ids)} items")
        return len(added_ids)
    
    def analyze_unanalyzed_items(self, limit: int = 50) -> int:
        logger.info(f"Analyzing up to {limit} items")
        items = self.data_store.get_unanalyzed_items(limit=limit)
        
        analyzed_count = 0
        for item in items:
            try:
                item_dict = item.to_dict()
                analysis = self.ai_pipeline.analyze_item(item_dict)
                self.data_store.update_analysis(item.id, analysis)
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error analyzing item {item.id}: {e}")
        
        logger.info(f"Analyzed {analyzed_count} items")
        return analyzed_count
    
    def generate_deliverables(self) -> Dict:
        logger.info("Generating deliverables")
        all_items = self.data_store.session.query(RegulatoryItem).all()
        
        digest = OutputGenerators.generate_impact_digest(all_items, limit=10)
        backlog = OutputGenerators.generate_task_backlog(all_items)
        
        last_24h = datetime.utcnow() - timedelta(hours=24)
        changelog = OutputGenerators.generate_changelog(all_items, last_24h)
        
        return {'digest': digest, 'backlog': backlog, 'changelog': changelog}
    
    def export_results(self, deliverables: Dict, output_dir: str = './reports'):
        os.makedirs(output_dir, exist_ok=True)
        
        json_file = os.path.join(output_dir, f"impact_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
        OutputGenerators.export_to_json(deliverables['digest'], deliverables['backlog'], deliverables['changelog'], filename=json_file)
        
        all_items = self.data_store.session.query(RegulatoryItem).all()
        csv_file = os.path.join(output_dir, f"impact_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
        OutputGenerators.export_to_csv(all_items, filename=csv_file)
        
        return {'json': json_file, 'csv': csv_file}
    
    def run_full_pipeline(self, limit_analysis: int = 50) -> Dict:
        logger.info("STARTING FULL PIPELINE")
        ingested = self.ingest_all_sources()
        analyzed = self.analyze_unanalyzed_items(limit=limit_analysis)
        deliverables = self.generate_deliverables()
        exports = self.export_results(deliverables)
        logger.info("PIPELINE COMPLETE")
        return {'ingested': ingested, 'analyzed': analyzed, 'deliverables': deliverables, 'exports': exports}

if __name__ == '__main__':
    orchestrator = RegulatoryIntelligenceOrchestrator()
    results = orchestrator.run_full_pipeline(limit_analysis=50)
    print(f"✓ Complete! Ingested: {results['ingested']}, Analyzed: {results['analyzed']}")
