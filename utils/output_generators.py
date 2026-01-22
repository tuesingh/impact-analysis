import pandas as pd
from datetime import datetime
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)

class OutputGenerators:
    @staticmethod
    def generate_impact_digest(items: List, limit: int = 10) -> Dict:
        relevant_items = [item for item in items if item.is_relevant]
        high_impact = sorted(relevant_items, key=lambda x: {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}.get(x.impact_overall or 'Low', 0), reverse=True)[:limit]
        
        digest = {'generated_at': datetime.utcnow().isoformat(), 'total_items': len(items), 'relevant_items': len(relevant_items), 'items': []}
        for item in high_impact:
            digest['items'].append({
                'id': item.id,
                'title': item.title,
                'source': item.source,
                'impact': item.impact_overall,
                'area': item.business_area,
                'url': item.url,
            })
        return digest
    
    @staticmethod
    def generate_task_backlog(items: List) -> Dict:
        task_dedup = {}
        for item in items:
            if not item.is_relevant or not item.tasks:
                continue
            tasks = json.loads(item.tasks) if isinstance(item.tasks, str) else item.tasks or []
            for task in tasks:
                task_key = f"{task.get('task', '')}-{task.get('owner_role', '')}".lower()
                if task_key not in task_dedup:
                    task_dedup[task_key] = task
        return {'generated_at': datetime.utcnow().isoformat(), 'total_tasks': len(task_dedup), 'tasks': list(task_dedup.values())}
    
    @staticmethod
    def generate_changelog(items_now: List, last_run_timestamp: datetime) -> Dict:
        new_items = [item for item in items_now if item.ingested_at > last_run_timestamp]
        escalated = [i for i in new_items if i.impact_overall in ['High', 'Critical']]
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'new_count': len(new_items),
            'escalated_count': len(escalated),
            'new_items': [{'id': i.id, 'title': i.title, 'impact': i.impact_overall} for i in new_items],
        }
    
    @staticmethod
    def export_to_csv(items: List, filename: str = 'impact_analysis.csv'):
        data = [{'ID': item.id, 'Title': item.title, 'Source': item.source, 'Impact': item.impact_overall, 'Area': item.business_area, 'URL': item.url} for item in items if item.is_relevant]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def export_to_json(digest: Dict, backlog: Dict, changelog: Dict, filename: str = 'impact_report.json'):
        report = {'generated_at': datetime.utcnow().isoformat(), 'digest': digest, 'backlog': backlog, 'changelog': changelog}
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        return filename
