import anthropic
import json
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class AIAnalysisPipeline:
    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = 'claude-3-5-sonnet-20241022'
    
    def analyze_item(self, item_dict: Dict) -> Dict:
        logger.info(f"Analyzing: {item_dict['title'][:50]}")
        
        relevance = self.check_relevance(item_dict)
        if not relevance['relevant']:
            return {'relevant': False, 'relevance_reason': relevance['reason']}
        
        impact = self.score_impact(item_dict, relevance['business_area'])
        summary = self.generate_executive_summary(item_dict, relevance, impact)
        tasks = self.generate_tasks(item_dict, relevance, impact)
        
        return {
            'relevant': True,
            'relevance_reason': relevance['reason'],
            'business_area': relevance['business_area'],
            'impact_severity': impact['severity'],
            'impact_time_sensitivity': impact['time_sensitivity'],
            'impact_operational_effort': impact['operational_effort'],
            'impact_customer': impact['customer_impact'],
            'impact_enforcement_risk': impact['enforcement_risk'],
            'impact_overall': impact['overall'],
            'executive_summary': summary['summary'],
            'tasks': tasks['tasks'],
        }
    
    def check_relevance(self, item_dict: Dict) -> Dict:
        prompt = f"""Is this regulatory item relevant to wealth management (RIA, Broker-Dealer, Retirement)?
Title: {item_dict['title']}
Summary: {item_dict['summary_raw'][:500]}
Return JSON: {{"relevant": bool, "business_area": "RIA/Broker-Dealer/Retirement/AML/Other", "reason": "short reason"}}"""
        try:
            response = self.client.messages.create(model=self.model, max_tokens=300, messages=[{'role': 'user', 'content': prompt}])
            text = response.content[0].text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            result = json.loads(text[json_start:json_end])
            return {'relevant': result.get('relevant', False), 'business_area': result.get('business_area'), 'reason': result.get('reason', '')}
        except:
            return {'relevant': False, 'business_area': None, 'reason': 'Analysis error'}
    
    def score_impact(self, item_dict: Dict, business_area: str) -> Dict:
        prompt = f"""Score impact 1-5 for: {item_dict['title'][:100]}
Dimensions: severity, time_sensitivity, operational_effort, customer_impact, enforcement_risk
Return JSON: {{"severity": 1-5, "time_sensitivity": 1-5, "operational_effort": 1-5, "customer_impact": 1-5, "enforcement_risk": 1-5, "overall": "Low/Medium/High/Critical"}}"""
        try:
            response = self.client.messages.create(model=self.model, max_tokens=300, messages=[{'role': 'user', 'content': prompt}])
            text = response.content[0].text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            result = json.loads(text[json_start:json_end])
            return {
                'severity': min(5, max(1, result.get('severity', 3))),
                'time_sensitivity': min(5, max(1, result.get('time_sensitivity', 3))),
                'operational_effort': min(5, max(1, result.get('operational_effort', 3))),
                'customer_impact': min(5, max(1, result.get('customer_impact', 2))),
                'enforcement_risk': min(5, max(1, result.get('enforcement_risk', 3))),
                'overall': result.get('overall', 'Medium'),
            }
        except:
            return {'severity': 3, 'time_sensitivity': 3, 'operational_effort': 3, 'customer_impact': 2, 'enforcement_risk': 3, 'overall': 'Medium'}
    
    def generate_executive_summary(self, item_dict: Dict, relevance: Dict, impact: Dict) -> Dict:
        prompt = f"""Generate 5 bullets for: {item_dict['title'][:100]}
Format: What happened, Who affected, What changes, Timing, Evidence needed.
Return JSON: {{"summary": ["bullet1", "bullet2", "bullet3", "bullet4", "bullet5"]}}"""
        try:
            response = self.client.messages.create(model=self.model, max_tokens=400, messages=[{'role': 'user', 'content': prompt}])
            text = response.content[0].text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            result = json.loads(text[json_start:json_end])
            return {'summary': '\n'.join(result.get('summary', [])[:5])}
        except:
            return {'summary': 'See source for details'}
    
    def generate_tasks(self, item_dict: Dict, relevance: Dict, impact: Dict) -> Dict:
        prompt = f"""Generate 3-5 actionable tasks for: {item_dict['title'][:100]}
Return JSON: {{"tasks": [{{"task": "action", "owner_role": "Compliance/Legal/Ops/Tech", "due_window": "Now/30/60/90", "evidence_artifact": "policy/training/comms", "dependency": "none"}}]}}"""
        try:
            response = self.client.messages.create(model=self.model, max_tokens=500, messages=[{'role': 'user', 'content': prompt}])
            text = response.content[0].text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            result = json.loads(text[json_start:json_end])
            return {'tasks': result.get('tasks', [])}
        except:
            return {'tasks': [{'task': f'Review {item_dict["title"][:50]}', 'owner_role': 'Compliance', 'due_window': '30', 'evidence_artifact': 'memo', 'dependency': 'none'}]}
