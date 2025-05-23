#!/usr/bin/env python3
"""
Natural Language to n8n Workflow Generator
Converts text descriptions into uploadable n8n workflow JSON files
"""

import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TriggerType(Enum):
    MANUAL = "n8n-nodes-base.manualTrigger"
    WEBHOOK = "n8n-nodes-base.webhook"
    SCHEDULE = "n8n-nodes-base.scheduleTrigger"
    EMAIL = "n8n-nodes-base.emailReadImap"
    FILE = "n8n-nodes-base.localFileTrigger"

class NodeType(Enum):
    # Logic Nodes
    IF = "n8n-nodes-base.if"
    SWITCH = "n8n-nodes-base.switch"
    MERGE = "n8n-nodes-base.merge"
    SET = "n8n-nodes-base.set"
    FUNCTION = "n8n-nodes-base.function"
    
    # Action Nodes
    HTTP_REQUEST = "n8n-nodes-base.httpRequest"
    EMAIL_SEND = "n8n-nodes-base.emailSend"
    GMAIL = "n8n-nodes-base.gmail"
    SLACK = "n8n-nodes-base.slack"
    GOOGLE_SHEETS = "n8n-nodes-base.googleSheets"
    WEBHOOK_RESPONSE = "n8n-nodes-base.webhookResponse"

@dataclass
class SemanticWorkflow:
    """Semantic representation of a workflow before n8n conversion"""
    name: str
    description: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    variables: Dict[str, Any]

class WorkflowParser:
    """Parses natural language into semantic workflow representation"""
    
    def __init__(self):
        self.intent_patterns = {
            'automation': r'automate|automatically|auto',
            'notification': r'notify|alert|send notification|tell me',
            'integration': r'connect|integrate|sync|link',
            'processing': r'process|handle|manage|deal with',
            'monitoring': r'monitor|watch|track|check',
            'scheduling': r'every|daily|weekly|monthly|schedule'
        }
        
        self.trigger_patterns = {
            'webhook': r'when.*receive|webhook|api call|http request',
            'email': r'email.*receive|new email|email arrives',
            'schedule': r'every|daily|weekly|monthly|at \d+|cron',
            'manual': r'manually|on demand|when I trigger'
        }
        
        self.action_patterns = {
            'email': r'send email|email.*to|notify via email',
            'slack': r'slack|send to slack|slack message',
            'sheets': r'google sheets|spreadsheet|add to sheet',
            'http': r'api call|send request|post to|get from',
            'webhook_response': r'respond|return|send back'
        }

    def parse(self, text: str) -> SemanticWorkflow:
        """Parse natural language text into semantic workflow"""
        text = text.lower().strip()
        
        # Extract workflow name and description
        name = self._extract_name(text)
        description = text[:100] + "..." if len(text) > 100 else text
        
        # Identify trigger type and configuration
        trigger_type, trigger_config = self._identify_trigger(text)
        
        # Extract workflow steps
        steps = self._extract_steps(text)
        
        # Generate connections
        connections = self._generate_connections(steps)
        
        # Extract variables
        variables = self._extract_variables(text)
        
        return SemanticWorkflow(
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            steps=steps,
            connections=connections,
            variables=variables
        )

    def _extract_name(self, text: str) -> str:
        """Extract workflow name from text"""
        # Look for explicit naming
        name_match = re.search(r'(?:name|call|title).*?[\'\"](.*?)[\'\"]', text)
        if name_match:
            return name_match.group(1)
        
        # Generate name from first action
        words = text.split()[:5]
        return " ".join(words).title() + " Workflow"

    def _identify_trigger(self, text: str) -> tuple:
        """Identify trigger type and configuration"""
        for trigger_type, pattern in self.trigger_patterns.items():
            if re.search(pattern, text):
                return trigger_type, self._get_trigger_config(trigger_type, text)
        
        return 'manual', {}

    def _get_trigger_config(self, trigger_type: str, text: str) -> Dict[str, Any]:
        """Get configuration for specific trigger type"""
        configs = {
            'webhook': {
                'httpMethod': 'POST',
                'path': 'webhook',
                'responseMode': 'onReceived'
            },
            'email': {
                'pollTimes': {'item': [{'mode': 'everyMinute'}]},
                'format': 'simple'
            },
            'schedule': self._parse_schedule(text),
            'manual': {}
        }
        return configs.get(trigger_type, {})

    def _parse_schedule(self, text: str) -> Dict[str, Any]:
        """Parse schedule from text"""
        if 'daily' in text or 'every day' in text:
            return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * *'}]}}
        elif 'hourly' in text or 'every hour' in text:
            return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 * * * *'}]}}
        elif 'weekly' in text:
            return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * 1'}]}}
        else:
            return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * *'}]}}

    def _extract_steps(self, text: str) -> List[Dict[str, Any]]:
        """Extract workflow steps from text"""
        steps = []
        
        # Look for conditional logic
        if re.search(r'if|when.*then|condition', text):
            steps.append({
                'type': 'logic',
                'node_type': NodeType.IF.value,
                'name': 'Check Condition',
                'conditions': self._extract_conditions(text)
            })
        
        # Look for actions
        for action_type, pattern in self.action_patterns.items():
            if re.search(pattern, text):
                steps.append({
                    'type': 'action',
                    'node_type': self._get_node_type_for_action(action_type),
                    'name': f'Execute {action_type.title()}',
                    'config': self._get_action_config(action_type, text)
                })
        
        return steps

    def _extract_conditions(self, text: str) -> List[Dict[str, Any]]:
        """Extract conditional logic from text"""
        conditions = []
        
        # Simple condition extraction
        if_match = re.search(r'if\s+(.+?)\s+then', text)
        if if_match:
            condition_text = if_match.group(1)
            conditions.append({
                'field': 'data',
                'operation': 'contains',
                'value': condition_text
            })
        
        return conditions

    def _get_node_type_for_action(self, action_type: str) -> str:
        """Map action type to n8n node type"""
        mapping = {
            'email': NodeType.EMAIL_SEND.value,
            'slack': NodeType.SLACK.value,
            'sheets': NodeType.GOOGLE_SHEETS.value,
            'http': NodeType.HTTP_REQUEST.value,
            'webhook_response': NodeType.WEBHOOK_RESPONSE.value
        }
        return mapping.get(action_type, NodeType.HTTP_REQUEST.value)

    def _get_action_config(self, action_type: str, text: str) -> Dict[str, Any]:
        """Get configuration for specific action"""
        configs = {
            'email': {
                'resource': 'send',
                'operation': 'send',
                'subject': 'Automated Notification',
                'message': 'This is an automated message from your n8n workflow.'
            },
            'slack': {
                'resource': 'message',
                'operation': 'post',
                'channel': '#general',
                'text': 'Automated message from n8n workflow'
            },
            'sheets': {
                'resource': 'sheet',
                'operation': 'append',
                'range': 'A:Z'
            },
            'http': {
                'method': 'POST',
                'url': 'https://api.example.com/webhook'
            }
        }
        return configs.get(action_type, {})

    def _generate_connections(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate connections between workflow steps"""
        connections = []
        for i in range(len(steps) - 1):
            connections.append({
                'source': i,
                'target': i + 1,
                'source_output': 'main',
                'target_input': 'main'
            })
        return connections

    def _extract_variables(self, text: str) -> Dict[str, Any]:
        """Extract variables from text"""
        variables = {}
        
        # Look for email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            variables['email'] = emails[0]
        
        # Look for URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls:
            variables['url'] = urls[0]
        
        return variables

class N8NWorkflowGenerator:
    """Generates n8n-compatible workflow JSON from semantic representation"""
    
    def __init__(self):
        self.node_counter = 0

    def generate(self, semantic_workflow: SemanticWorkflow) -> Dict[str, Any]:
        """Generate n8n workflow JSON from semantic representation"""
        self.node_counter = 0
        
        # Create base workflow structure
        workflow = {
            "name": semantic_workflow.name,
            "nodes": [],
            "connections": {},
            "active": False,
            "settings": {},
            "versionId": str(uuid.uuid4()),
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }
        
        # Generate trigger node
        trigger_node = self._create_trigger_node(
            semantic_workflow.trigger_type,
            semantic_workflow.trigger_config
        )
        workflow["nodes"].append(trigger_node)
        
        # Generate step nodes
        step_nodes = []
        for step in semantic_workflow.steps:
            node = self._create_step_node(step)
            step_nodes.append(node)
            workflow["nodes"].append(node)
        
        # Generate connections
        workflow["connections"] = self._create_connections(
            trigger_node, step_nodes, semantic_workflow.connections
        )
        
        return workflow

    def _create_trigger_node(self, trigger_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create trigger node"""
        node_id = self._get_next_node_id()
        
        trigger_types = {
            'manual': TriggerType.MANUAL.value,
            'webhook': TriggerType.WEBHOOK.value,
            'schedule': TriggerType.SCHEDULE.value,
            'email': TriggerType.EMAIL.value
        }
        
        node_type = trigger_types.get(trigger_type, TriggerType.MANUAL.value)
        
        node = {
            "parameters": config,
            "id": node_id,
            "name": f"{trigger_type.title()} Trigger",
            "type": node_type,
            "typeVersion": 1,
            "position": [250, 300]
        }
        
        return node

    def _create_step_node(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create step node"""
        node_id = self._get_next_node_id()
        
        node = {
            "parameters": step.get('config', {}),
            "id": node_id,
            "name": step.get('name', 'Step'),
            "type": step.get('node_type', NodeType.SET.value),
            "typeVersion": 1,
            "position": [250 + (self.node_counter * 200), 300]
        }
        
        return node

    def _create_connections(self, trigger_node: Dict[str, Any], step_nodes: List[Dict[str, Any]], 
                          semantic_connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create node connections"""
        connections = {}
        
        if not step_nodes:
            return connections
        
        # Connect trigger to first step
        connections[trigger_node["name"]] = {
            "main": [[{
                "node": step_nodes[0]["name"],
                "type": "main",
                "index": 0
            }]]
        }
        
        # Connect subsequent steps
        for i in range(len(step_nodes) - 1):
            current_node = step_nodes[i]
            next_node = step_nodes[i + 1]
            
            connections[current_node["name"]] = {
                "main": [[{
                    "node": next_node["name"],
                    "type": "main",
                    "index": 0
                }]]
            }
        
        return connections

    def _get_next_node_id(self) -> str:
        """Generate next node ID"""
        node_id = str(uuid.uuid4())
        self.node_counter += 1
        return node_id

class WorkflowExporter:
    """Exports workflow to various formats"""
    
    @staticmethod
    def to_json_file(workflow: Dict[str, Any], filename: str) -> str:
        """Export workflow to JSON file"""
        with open(filename, 'w') as f:
            json.dump(workflow, f, indent=2)
        return filename
    
    @staticmethod
    def to_clipboard_format(workflow: Dict[str, Any]) -> str:
        """Export workflow to clipboard-friendly format"""
        return json.dumps(workflow, indent=2)

# Main Workflow Generator System
class N8NWorkflowSystem:
    """Complete system for converting text to n8n workflows"""
    
    def __init__(self):
        self.parser = WorkflowParser()
        self.generator = N8NWorkflowGenerator()
        self.exporter = WorkflowExporter()
    
    def create_workflow_from_text(self, text: str, export_format: str = 'json') -> Dict[str, Any]:
        """Main method: Convert text to n8n workflow"""
        try:
            # Step 1: Parse natural language to semantic representation
            semantic_workflow = self.parser.parse(text)
            print(f"✅ Parsed workflow: {semantic_workflow.name}")
            
            # Step 2: Generate n8n workflow JSON
            n8n_workflow = self.generator.generate(semantic_workflow)
            print(f"✅ Generated n8n workflow with {len(n8n_workflow['nodes'])} nodes")
            
            # Step 3: Export workflow
            if export_format == 'json':
                filename = f"{semantic_workflow.name.replace(' ', '_').lower()}.json"
                self.exporter.to_json_file(n8n_workflow, filename)
                print(f"✅ Exported to {filename}")
            
            return {
                'semantic': asdict(semantic_workflow),
                'n8n_workflow': n8n_workflow,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }

# Example Usage and Testing
def demo_workflow_generation():
    """Demonstrate the workflow generation system"""
    
    system = N8NWorkflowSystem()
    
    # Example 1: Simple notification workflow
    text1 = """
    I want to create a workflow that sends me a Slack notification 
    whenever I receive a webhook with high priority data. 
    If the priority is 'urgent', send to #alerts channel, 
    otherwise send to #general channel.
    """
    
    print("🚀 Generating Workflow 1...")
    result1 = system.create_workflow_from_text(text1)
    
    # Example 2: Scheduled data processing
    text2 = """
    Create a workflow that runs daily at 9 AM, 
    fetches data from an API endpoint,
    processes the data, and saves it to a Google Sheet.
    Send me an email summary when complete.
    """
    
    print("\n🚀 Generating Workflow 2...")
    result2 = system.create_workflow_from_text(text2)
    
    # Example 3: Email automation
    text3 = """
    When I receive an email with 'urgent' in the subject,
    automatically forward it to support@company.com
    and create a ticket in our system via API call.
    """
    
    print("\n🚀 Generating Workflow 3...")
    result3 = system.create_workflow_from_text(text3)
    
    return [result1, result2, result3]

if __name__ == "__main__":
    # Run demonstration
    results = demo_workflow_generation()
    
    # Print summary
    print("\n" + "="*50)
    print("WORKFLOW GENERATION SUMMARY")
    print("="*50)
    
    for i, result in enumerate(results, 1):
        if result['status'] == 'success':
            workflow = result['n8n_workflow']
            print(f"\nWorkflow {i}: {workflow['name']}")
            print(f"  - Nodes: {len(workflow['nodes'])}")
            print(f"  - Connections: {len(workflow.get('connections', {}))}")
            print(f"  - Status: ✅ Ready for upload to n8n")
        else:
            print(f"\nWorkflow {i}: ❌ Error - {result['error']}")
    
    print(f"\n📁 Generated JSON files are ready for upload to your n8n dashboard!")
    print("   Simply import the .json files in n8n: Settings > Import/Export > Import from File")
