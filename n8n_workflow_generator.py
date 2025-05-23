#!/usr/bin/env python3
"""
Natural Language to n8n Workflow Generator
Converts text descriptions into uploadable n8n workflow JSON files
"""

import json
import openai # Added for LLM integration
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict # asdict might be removed if SemanticWorkflow is fully removed
from enum import Enum

# Enum classes can remain as they might be useful for the LLM prompt or validation,
# or if some parts of the old structure are kept for other purposes.
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

# SemanticWorkflow might be deprecated if the LLM generates full n8n JSON directly.
# For now, it's kept, but its usage will change.
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

# class WorkflowParser:
#     """Parses natural language into semantic workflow representation"""
    
#     def __init__(self):
#         self.intent_patterns = {
#             'automation': r'automate|automatically|auto',
#             'notification': r'notify|alert|send notification|tell me',
#             'integration': r'connect|integrate|sync|link',
#             'processing': r'process|handle|manage|deal with',
#             'monitoring': r'monitor|watch|track|check',
#             'scheduling': r'every|daily|weekly|monthly|schedule'
#         }
        
#         self.trigger_patterns = {
#             'webhook': r'when.*receive|webhook|api call|http request',
#             'email': r'email.*receive|new email|email arrives',
#             'schedule': r'every|daily|weekly|monthly|at \d+|cron',
#             'manual': r'manually|on demand|when I trigger'
#         }
        
#         self.action_patterns = {
#             'email': r'send email|email.*to|notify via email',
#             'slack': r'slack|send to slack|slack message',
#             'sheets': r'google sheets|spreadsheet|add to sheet',
#             'http': r'api call|send request|post to|get from',
#             'webhook_response': r'respond|return|send back'
#         }

#     def parse(self, text: str) -> SemanticWorkflow:
#         """Parse natural language text into semantic workflow"""
#         text = text.lower().strip()
        
#         # Extract workflow name and description
#         name = self._extract_name(text)
#         description = text[:100] + "..." if len(text) > 100 else text
        
#         # Identify trigger type and configuration
#         trigger_type, trigger_config = self._identify_trigger(text)
        
#         # Extract workflow steps
#         steps = self._extract_steps(text)
        
#         # Generate connections
#         connections = self._generate_connections(steps)
        
#         # Extract variables
#         variables = self._extract_variables(text)
        
#         return SemanticWorkflow(
#             name=name,
#             description=description,
#             trigger_type=trigger_type,
#             trigger_config=trigger_config,
#             steps=steps,
#             connections=connections,
#             variables=variables
#         )

#     def _extract_name(self, text: str) -> str:
#         """Extract workflow name from text"""
#         # Look for explicit naming
#         name_match = re.search(r'(?:name|call|title).*?[\'\"](.*?)[\'\"]', text)
#         if name_match:
#             return name_match.group(1)
        
#         # Generate name from first action
#         words = text.split()[:5]
#         return " ".join(words).title() + " Workflow"

#     def _identify_trigger(self, text: str) -> tuple:
#         """Identify trigger type and configuration"""
#         for trigger_type, pattern in self.trigger_patterns.items():
#             if re.search(pattern, text):
#                 return trigger_type, self._get_trigger_config(trigger_type, text)
        
#         return 'manual', {}

#     def _get_trigger_config(self, trigger_type: str, text: str) -> Dict[str, Any]:
#         """Get configuration for specific trigger type"""
#         configs = {
#             'webhook': {
#                 'httpMethod': 'POST',
#                 'path': 'webhook',
#                 'responseMode': 'onReceived'
#             },
#             'email': {
#                 'pollTimes': {'item': [{'mode': 'everyMinute'}]},
#                 'format': 'simple'
#             },
#             'schedule': self._parse_schedule(text),
#             'manual': {}
#         }
#         return configs.get(trigger_type, {})

#     def _parse_schedule(self, text: str) -> Dict[str, Any]:
#         """Parse schedule from text"""
#         if 'daily' in text or 'every day' in text:
#             return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * *'}]}}
#         elif 'hourly' in text or 'every hour' in text:
#             return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 * * * *'}]}}
#         elif 'weekly' in text:
#             return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * 1'}]}}
#         else:
#             return {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 9 * * *'}]}}

#     def _extract_steps(self, text: str) -> List[Dict[str, Any]]:
#         """Extract workflow steps from text"""
#         steps = []
        
#         # Look for conditional logic
#         if re.search(r'if|when.*then|condition', text):
#             steps.append({
#                 'type': 'logic',
#                 'node_type': NodeType.IF.value,
#                 'name': 'Check Condition',
#                 'conditions': self._extract_conditions(text)
#             })
        
#         # Look for actions
#         for action_type, pattern in self.action_patterns.items():
#             if re.search(pattern, text):
#                 steps.append({
#                     'type': 'action',
#                     'node_type': self._get_node_type_for_action(action_type),
#                     'name': f'Execute {action_type.title()}',
#                     'config': self._get_action_config(action_type, text)
#                 })
        
#         return steps

#     def _extract_conditions(self, text: str) -> List[Dict[str, Any]]:
#         """Extract conditional logic from text"""
#         conditions = []
        
#         # Simple condition extraction
#         if_match = re.search(r'if\s+(.+?)\s+then', text)
#         if if_match:
#             condition_text = if_match.group(1)
#             conditions.append({
#                 'field': 'data',
#                 'operation': 'contains',
#                 'value': condition_text
#             })
        
#         return conditions

#     def _get_node_type_for_action(self, action_type: str) -> str:
#         """Map action type to n8n node type"""
#         mapping = {
#             'email': NodeType.EMAIL_SEND.value,
#             'slack': NodeType.SLACK.value,
#             'sheets': NodeType.GOOGLE_SHEETS.value,
#             'http': NodeType.HTTP_REQUEST.value,
#             'webhook_response': NodeType.WEBHOOK_RESPONSE.value
#         }
#         return mapping.get(action_type, NodeType.HTTP_REQUEST.value)

#     def _get_action_config(self, action_type: str, text: str) -> Dict[str, Any]:
#         """Get configuration for specific action"""
#         configs = {
#             'email': {
#                 'resource': 'send',
#                 'operation': 'send',
#                 'subject': 'Automated Notification',
#                 'message': 'This is an automated message from your n8n workflow.'
#             },
#             'slack': {
#                 'resource': 'message',
#                 'operation': 'post',
#                 'channel': '#general',
#                 'text': 'Automated message from n8n workflow'
#             },
#             'sheets': {
#                 'resource': 'sheet',
#                 'operation': 'append',
#                 'range': 'A:Z'
#             },
#             'http': {
#                 'method': 'POST',
#                 'url': 'https://api.example.com/webhook'
#             }
#         }
#         return configs.get(action_type, {})

#     def _generate_connections(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Generate connections between workflow steps"""
#         connections = []
#         for i in range(len(steps) - 1):
#             connections.append({
#                 'source': i,
#                 'target': i + 1,
#                 'source_output': 'main',
#                 'target_input': 'main'
#             })
#         return connections

#     def _extract_variables(self, text: str) -> Dict[str, Any]:
#         """Extract variables from text"""
#         variables = {}
        
#         # Look for email addresses
#         emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
#         if emails:
#             variables['email'] = emails[0]
        
#         # Look for URLs
#         urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
#         if urls:
#             variables['url'] = urls[0]
        
#         return variables

# LLM-based n8n JSON generation
def get_n8n_json_from_llm(user_prompt: str, api_key: str) -> Dict[str, Any]:
    """
    Generates n8n workflow JSON from a user prompt using an LLM.
    """
    if not api_key or api_key == "YOUR_OPENAI_API_KEY":
        print("🛑 ERROR: OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable or pass it to the function.")
        # Return a basic valid n8n JSON structure indicating the error
        return {
            "name": "Error - API Key Missing",
            "nodes": [{
                "parameters": {"message": "OpenAI API Key is missing. Please configure it."},
                "id": str(uuid.uuid4()),
                "name": "API Key Error",
                "type": "n8n-nodes-base.stickyNote", # Using a sticky note to show the error in n8n UI
                "typeVersion": 1,
                "position": [250, 300]
            }],
            "connections": {},
            "active": False,
            "settings": {},
            "versionId": str(uuid.uuid4()),
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }

    client = openai.OpenAI(api_key=api_key)

    system_prompt = """
    You are an expert n8n workflow generation assistant.
    Your task is to convert the user's text prompt into a valid n8n workflow JSON object.
    The output MUST be ONLY the JSON object, with no other text, explanations, or markdown formatting.
    The JSON structure should be directly usable by n8n.

    Key elements of the n8n JSON structure:
    - "name": (string) The name of the workflow. Try to infer a suitable name from the user's prompt.
    - "nodes": (array) A list of node objects.
        - Each node object must have:
            - "parameters": (object) Configuration specific to the node type (e.g., for HTTP Request: method, url, options; for Slack: text, channel).
            - "id": (string) A unique UUID v4 (e.g., "a1b2c3d4-e5f6-7890-1234-567890abcdef"). Generate a new UUID for each node.
            - "name": (string) A descriptive name for the node (e.g., "Start", "Fetch Data", "Send Slack Alert").
            - "type": (string) The n8n node type (e.g., "n8n-nodes-base.start", "n8n-nodes-base.httpRequest", "n8n-nodes-base.if", "n8n-nodes-base.slack").
            - "typeVersion": (number) Usually 1 or 2, depending on the node. Default to 1 if unsure for common nodes.
            - "position": (array of numbers) [x, y] coordinates for the node's position in the n8n editor. Arrange nodes logically, e.g., [250, 300], [450, 300], [650, 300].
    - "connections": (object) Defines how nodes are connected.
        - Keys are the 'name' of the source node (must match a "name" in the "nodes" list).
        - Values are objects where keys are output port names (usually "main", but can be others like "true" or "false" for IF nodes).
        - The value for an output port is an array of arrays, each inner array containing an object:
            { "node": "TARGET_NODE_NAME", "type": "main", "index": 0 } 
            (Ensure TARGET_NODE_NAME matches the "name" of a node defined in the "nodes" list).
    - "active": (boolean) Whether the workflow is active (default to false for new workflows).
    - "settings": (object) Workflow settings (can be an empty object {} or specify timezone, error workflow, etc.).
    - "versionId": (string) A unique UUID v4 for this version of the workflow. Generate a new UUID.
    - "createdAt": (string) ISO 8601 timestamp (e.g., "2023-01-01T12:00:00.000Z"). Use the current UTC time.
    - "updatedAt": (string) ISO 8601 timestamp (e.g., "2023-01-01T12:00:00.000Z"). Use the current UTC time.

    Example of a minimal workflow for "a workflow that starts and then does nothing else":
    {
      "name": "My Simple Workflow",
      "nodes": [
        {
          "parameters": {},
          "id": "GENERATED_UUID_FOR_START_NODE",
          "name": "Start",
          "type": "n8n-nodes-base.start",
          "typeVersion": 1,
          "position": [250, 300]
        }
      ],
      "connections": {},
      "active": false,
      "settings": {},
      "versionId": "GENERATED_UUID_FOR_WORKFLOW",
      "createdAt": "CURRENT_ISO_TIMESTAMP_Z",
      "updatedAt": "CURRENT_ISO_TIMESTAMP_Z"
    }
    
    Ensure all UUIDs (for node "id" and "versionId") are unique and newly generated (use UUID v4 format).
    Ensure "createdAt" and "updatedAt" timestamps are current UTC in ISO 8601 format, ending with 'Z'.
    If the user asks for a trigger (e.g., "when a webhook is called", "every Monday at 9 AM"), use the appropriate trigger node (e.g., "n8n-nodes-base.webhook", "n8n-nodes-base.scheduleTrigger") as the first node. If no trigger is specified, you can start with "n8n-nodes-base.start".
    Pay close attention to the "connections" structure, ensuring node names used in connections accurately match the "name" fields of the nodes in the "nodes" list.
    If the user implies data from a previous node should be used (e.g., "send the webhook body to Slack"), you might need to use n8n expressions like "{{$json.body}}" or "{{$items('Previous Node Name').first().json.fieldName}}" in the parameters of the consuming node. Assume basic data passing if not specified.
    """

    llm_response_content = None # Initialize for error logging
    try:
        # Generate UUIDs and timestamps to be potentially used by the LLM, or to fill in if LLM omits them.
        # However, the LLM is instructed to generate these itself. This is more of a fallback.
        workflow_version_id = str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat() + "Z"

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125", # Using a specific version known for good JSON output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} # Request JSON output
        )
        
        llm_response_content = completion.choices[0].message.content
        
        if not llm_response_content:
            raise ValueError("LLM returned an empty response.")

        parsed_json = json.loads(llm_response_content)
        
        # --- Start Enhanced validation and enrichment of LLM response ---
        if not isinstance(parsed_json, dict):
             raise ValueError("LLM response is not a JSON object.")
        
        # Top-Level Property Validation & Enrichment
        if not isinstance(parsed_json.get("name"), str) or not parsed_json["name"].strip():
            parsed_json["name"] = "LLM Generated Workflow" # Default name if missing or empty
        if not isinstance(parsed_json.get("active"), bool):
            parsed_json["active"] = False # Default active state
        if not isinstance(parsed_json.get("settings"), dict):
            parsed_json["settings"] = {} # Default settings
        
        # UUIDs and Timestamps (enrich if missing, validate format if present)
        try:
            uuid.UUID(str(parsed_json.get("versionId")))
        except (ValueError, TypeError):
            parsed_json["versionId"] = str(uuid.uuid4())
        
        try:
            datetime.fromisoformat(str(parsed_json.get("createdAt")).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            parsed_json["createdAt"] = datetime.utcnow().isoformat() + "Z"
        
        try:
            datetime.fromisoformat(str(parsed_json.get("updatedAt")).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            parsed_json["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        # Node Validation & Enrichment
        if "nodes" not in parsed_json or not isinstance(parsed_json["nodes"], list) or not parsed_json["nodes"]:
            # If no nodes or empty list, create a default start node
            print("⚠️ Warning: LLM response missing 'nodes' or 'nodes' is empty. Creating a default Start node.")
            parsed_json["nodes"] = [{
                "parameters": {}, 
                "id": str(uuid.uuid4()), 
                "name": "Start",
                "type": "n8n-nodes-base.start", 
                "typeVersion": 1, 
                "position": [250, 300]
            }]
        else:
            processed_node_names = set()
            for i, node in enumerate(parsed_json["nodes"]):
                if not isinstance(node, dict):
                    raise ValueError(f"Node at index {i} is not a dictionary.")
                
                # ID validation/enrichment
                try:
                    uuid.UUID(str(node.get("id")))
                except (ValueError, TypeError):
                    node["id"] = str(uuid.uuid4()) # Ensure valid UUID if LLM provided one is faulty

                # Name validation/enrichment
                node_name = node.get("name")
                if not isinstance(node_name, str) or not node_name.strip():
                    node["name"] = f"Unnamed Node {i+1}"
                    print(f"⚠️ Warning: Node at index {i} has invalid or missing name. Defaulting to '{node['name']}'.")
                # Ensure unique node names as they are used for connections
                original_node_name = node["name"]
                counter = 1
                while node["name"] in processed_node_names:
                    node["name"] = f"{original_node_name}_{counter}"
                    counter +=1
                processed_node_names.add(node["name"])


                # Type validation/enrichment
                if not isinstance(node.get("type"), str) or not node["type"].strip():
                    node["type"] = "n8n-nodes-base.stickyNote" # Default to stickyNote if type is invalid/missing
                    node.setdefault("parameters", {"message": "Error: Node type was missing or invalid."})
                    print(f"⚠️ Warning: Node '{node['name']}' has invalid or missing type. Defaulting to 'stickyNote'.")
                
                # typeVersion validation/enrichment
                if not isinstance(node.get("typeVersion"), int):
                    node["typeVersion"] = 1 # Default typeVersion
                
                # Position validation/enrichment
                position = node.get("position")
                if not (isinstance(position, list) and len(position) == 2 and 
                        all(isinstance(p, (int, float)) for p in position)):
                    node["position"] = [250 + (i * 200), 300 + ((i % 2) * 100)] # Default position
                    print(f"⚠️ Warning: Node '{node['name']}' has invalid or missing position. Defaulting.")

                # Parameters validation/enrichment
                if not isinstance(node.get("parameters"), dict):
                    node["parameters"] = {}

        # Connections Validation & Enrichment
        if not isinstance(parsed_json.get("connections"), dict):
            parsed_json["connections"] = {} # Default to empty if missing or invalid type
        
        valid_node_names_for_connections = {n.get("name") for n in parsed_json["nodes"] if isinstance(n.get("name"), str)}
        
        connections_to_remove = []
        for source_node_name, output_ports in list(parsed_json["connections"].items()):
            if source_node_name not in valid_node_names_for_connections:
                print(f"⚠️ Warning: Connection source node '{source_node_name}' not found in defined nodes. Removing connection.")
                connections_to_remove.append(source_node_name)
                continue
            
            if not isinstance(output_ports, dict):
                print(f"⚠️ Warning: Output ports for '{source_node_name}' is not a dictionary. Removing connection.")
                connections_to_remove.append(source_node_name)
                continue

            ports_to_remove = []
            for port_name, targets in list(output_ports.items()):
                if not isinstance(targets, list):
                    print(f"⚠️ Warning: Targets for '{source_node_name}' -> '{port_name}' is not a list. Removing port targets.")
                    ports_to_remove.append(port_name)
                    continue
                
                valid_targets_for_port = []
                for target_group in targets:
                    if not isinstance(target_group, list):
                        print(f"⚠️ Warning: Target group in '{source_node_name}' -> '{port_name}' is not a list. Skipping group.")
                        continue
                    
                    valid_target_group_items = []
                    for target_obj in target_group:
                        if not isinstance(target_obj, dict):
                            print(f"⚠️ Warning: Target object in '{source_node_name}' -> '{port_name}' is not a dict. Skipping target.")
                            continue
                        
                        target_node_name = target_obj.get("node")
                        target_type = target_obj.get("type") # e.g. "main"
                        target_index = target_obj.get("index") # e.g. 0

                        if target_node_name not in valid_node_names_for_connections:
                            print(f"⚠️ Warning: Target node '{target_node_name}' in connection from '{source_node_name}' -> '{port_name}' not found. Skipping target.")
                            continue
                        if not (isinstance(target_type, str) and target_type.strip()):
                            print(f"⚠️ Warning: Target type for '{target_node_name}' in connection from '{source_node_name}' -> '{port_name}' is invalid. Skipping target.")
                            continue
                        if not isinstance(target_index, int):
                             print(f"⚠️ Warning: Target index for '{target_node_name}' in connection from '{source_node_name}' -> '{port_name}' is not an int. Skipping target.")
                             continue
                        
                        valid_target_group_items.append({
                            "node": target_node_name,
                            "type": target_type,
                            "index": target_index
                        })
                    
                    if valid_target_group_items: # Only add if there are valid items in this group
                        valid_targets_for_port.append(valid_target_group_items)

                if not valid_targets_for_port: # If no valid targets remain for this port
                    ports_to_remove.append(port_name)
                else:
                    output_ports[port_name] = valid_targets_for_port
            
            for port_name in ports_to_remove:
                del output_ports[port_name]
            
            if not output_ports: # If all ports were removed for this source_node_name
                connections_to_remove.append(source_node_name)

        for conn_name in connections_to_remove:
            del parsed_json["connections"][conn_name]
        # --- End Enhanced validation and enrichment ---

        return parsed_json

    except openai.APIError as e:
        print(f"❌ OpenAI API Error: {e}")
        error_message = f"OpenAI API Error: {str(e)}"
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: Failed to parse LLM response. Details: {e}")
        print(f"Raw LLM response was: {llm_response_content}")
        error_message = f"JSON Parsing Error: {str(e)}. Raw response: {llm_response_content[:500]}..."
    except ValueError as e:
        print(f"❌ Value Error (LLM response validation or empty response): {e}")
        error_message = f"LLM Response/Validation Error: {str(e)}"
    except Exception as e: # Catch any other unexpected errors
        print(f"❌ Unexpected Error: {e}")
        error_message = f"Unexpected Error: {str(e)}"

    # Fallback to a simple error workflow if any exception occurred
    return {
        "name": "Error Generating Workflow",
        "nodes": [{
            "parameters": {"message": error_message},
            "id": str(uuid.uuid4()),
            "name": "Error Node",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [250, 300]
        }],
        "connections": {}, "active": False, "settings": {}, 
        "versionId": str(uuid.uuid4()), 
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }

# The N8NWorkflowGenerator class is no longer needed as the LLM generates the full JSON.
# class N8NWorkflowGenerator:
# ... (rest of the commented out class)

class WorkflowExporter:
    """Exports workflow to various formats"""
    
    @staticmethod
    def to_json_file(workflow: Dict[str, Any], filename: str) -> str:
        """Export workflow to JSON file"""
        # Ensure filename is somewhat safe
        filename = "".join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in filename)
        if not filename.endswith(".json"):
            filename += ".json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(workflow, f, indent=2)
            print(f"✅ Successfully exported to {filename}")
        except IOError as e:
            print(f"❌ Error exporting to file {filename}: {e}")
            # Fallback filename if original is problematic (though sanitization should help)
            fallback_filename = f"workflow_export_{str(uuid.uuid4())}.json"
            try:
                with open(fallback_filename, 'w') as f:
                    json.dump(workflow, f, indent=2)
                print(f"✅ Successfully exported to fallback file {fallback_filename}")
                return fallback_filename
            except Exception as fe:
                 print(f"❌ Error exporting to fallback file {fallback_filename}: {fe}")
                 return "" # Return empty if all fails
        return filename
    
    @staticmethod
    def to_clipboard_format(workflow: Dict[str, Any]) -> str:
        """Export workflow to clipboard-friendly format"""
        return json.dumps(workflow, indent=2)

# Main Workflow Generator System
class N8NWorkflowSystem:
    """Complete system for converting text to n8n workflows using LLM"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.exporter = WorkflowExporter()
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"
        
        if self.openai_api_key == "YOUR_OPENAI_API_KEY":
            print("⚠️ WARNING: OpenAI API key is not configured. Using placeholder key.")
            print("   Please set the OPENAI_API_KEY environment variable or pass it to N8NWorkflowSystem constructor.")

    def create_workflow_from_text(self, text: str, export_filename: Optional[str] = None) -> Dict[str, Any]:
        """Main method: Convert text to n8n workflow using LLM"""
        print(f"💬 Sending prompt to LLM for: \"{text[:100]}...\"")
        
        n8n_workflow_json = get_n8n_json_from_llm(text, self.openai_api_key)
        
        if not n8n_workflow_json or not n8n_workflow_json.get("nodes") or "Error" in n8n_workflow_json.get("name", ""):
             print(f"❌ LLM did not return a valid or complete workflow structure. Workflow name: {n8n_workflow_json.get('name')}")
             # Even if it's an error structure from get_n8n_json_from_llm, we might still want to export it to see the error in n8n
        else:
            print(f"✅ LLM generated workflow: {n8n_workflow_json.get('name', 'Unnamed Workflow')}")
            print(f"   Nodes: {len(n8n_workflow_json.get('nodes', []))}, Connections: {len(n8n_workflow_json.get('connections', {}))}")

        if export_filename:
            # Use the workflow name for the filename if export_filename is just True or empty string
            actual_filename = export_filename
            if isinstance(export_filename, str) and not export_filename.strip(): # handles empty string
                 actual_filename = n8n_workflow_json.get('name', 'untitled_workflow')
            elif export_filename is True: # if True, use workflow name
                 actual_filename = n8n_workflow_json.get('name', 'untitled_workflow')
            
            self.exporter.to_json_file(n8n_workflow_json, actual_filename)
        
        return {
            'n8n_workflow': n8n_workflow_json,
            'status': 'error' if "Error" in n8n_workflow_json.get("name", "") else 'success'
        }

# Example Usage and Testing
def demo_workflow_generation(api_key_for_demo: str):
    """Demonstrate the LLM-based workflow generation system"""
    
    # Initialize system with the provided API key for the demo
    system = N8NWorkflowSystem(openai_api_key=api_key_for_demo)
    
    prompts = [
        ("Create a simple workflow named 'Webhook Listener' that is triggered by a webhook at path 'mywebhook', then uses a Set node to set a variable 'status' to 'received', and finally responds to the webhook with a 200 OK and the message 'Webhook processed'.", "webhook_listener_workflow"),
        ("Every Monday at 9 AM, fetch data from 'https://jsonplaceholder.typicode.com/todos/1'. If the 'completed' field in the response is true, send a Slack message to '#general' saying 'Task completed'. Otherwise, log 'Task not completed' using a Sticky Note. Name it 'Scheduled Task Check'.", "scheduled_task_check_workflow"),
        ("A workflow that starts, then uses an HTTP Request node to GET data from 'https://www.boredapi.com/api/activity'. Name it 'Bored API Fetcher'.", "bored_api_fetcher_workflow"),
        ("This prompt is intentionally bad to test error handling json output.", "bad_prompt_test_workflow")
    ]
    
    results = []
    for i, (prompt, filename_base) in enumerate(prompts):
        print(f"\n🚀 Generating Workflow {i+1} ({filename_base})...")
        # Pass filename for export, it will be sanitized and .json added by exporter
        result = system.create_workflow_from_text(prompt, export_filename=filename_base)
        results.append(result)
    
    return results

if __name__ == "__main__":
    import os
    # Attempt to get API key from environment variable first for the demo
    actual_api_key_for_demo = os.environ.get("OPENAI_API_KEY")

    if not actual_api_key_for_demo or actual_api_key_for_demo == "YOUR_OPENAI_API_KEY":
        print("🔴 ATTENTION: Using a placeholder or missing OpenAI API key for the demo.")
        print("   The script will likely generate placeholder/error workflows.")
        print("   To generate real workflows, please set your OPENAI_API_KEY environment variable.\n")
        actual_api_key_for_demo = "YOUR_OPENAI_API_KEY" # Ensure it's the placeholder if not set

    demo_results = demo_workflow_generation(api_key_for_demo=actual_api_key_for_demo)
    
    print("\n" + "="*50)
    print("LLM-BASED WORKFLOW GENERATION DEMO SUMMARY")
    print("="*50)
    
    for i, res_dict in enumerate(demo_results):
        workflow_data = res_dict.get('n8n_workflow', {})
        status = res_dict.get('status', 'unknown')
        
        workflow_name = workflow_data.get('name', 'Unnamed Workflow')
        nodes_count = len(workflow_data.get('nodes', []))
        connections_count = len(workflow_data.get('connections', {}))
            
        print(f"\nWorkflow {i+1}: {workflow_name}")
        print(f"  - Status from system: {status}")
        print(f"  - Nodes: {nodes_count}")
        print(f"  - Connections: {connections_count}")

        if "Error" in workflow_name or status == 'error':
            print(f"  - Outcome: ⚠️ Generated a placeholder/error workflow. Check logs and JSON file.")
            if nodes_count > 0 and workflow_data['nodes'][0].get('type') == "n8n-nodes-base.stickyNote":
                 print(f"    Error details (from Sticky Note): {workflow_data['nodes'][0].get('parameters', {}).get('message', 'N/A')}")
        else:
            print(f"  - Outcome: ✅ Workflow structure generated.")
        
        # Check if a file was likely created (exporter handles actual naming)
        # This is a simplified check based on the input filename_base
        # The actual filename might be different due to sanitization or if exporter failed.
        prompt_filename_base = prompts[i][1] 
        potential_filename = "".join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in prompt_filename_base) + ".json"
        if os.path.exists(potential_filename):
            print(f"  - Exported to: {potential_filename} (verify content)")
        elif status != 'error': # Don't claim export if it's an error workflow from LLM function directly
            print(f"  - Export: File '{potential_filename}' was expected but might not have been created if export failed or name differs.")

    if actual_api_key_for_demo == "YOUR_OPENAI_API_KEY":
         print("\n🔴 NOTE: The demo ran with a placeholder API key.")
         print("   Generated workflows are likely error placeholders. Set OPENAI_API_KEY for functional generation.")
    else:
        print(f"\n📁 Generated JSON files (if any) are in the current directory.")
        print("   These can be imported into n8n: Settings > Import/Export > Import from File.")

    print("\n✨ Demo finished.")
