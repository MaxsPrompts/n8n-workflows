import pytest
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Assuming n8n_workflow_generator.py is in the parent directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from n8n_workflow_generator import N8NWorkflowSystem, get_n8n_json_from_llm

# Minimal valid n8n workflow structure for mocking
MINIMAL_N8N_WORKFLOW = {
    "name": "Test Workflow",
    "nodes": [
        {
            "parameters": {},
            "id": str(uuid.uuid4()),
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [250, 300]
        }
    ],
    "connections": {},
    "active": False,
    "settings": {},
    "versionId": str(uuid.uuid4()),
    "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "updatedAt": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "meta": None, # Added as per issue #1
    "pinData": None # Added as per issue #1
}

@pytest.fixture
def workflow_system():
    return N8NWorkflowSystem(openai_api_key="fake_key_for_testing")

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def is_iso_8601_utc(date_string):
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.tzinfo == timezone.utc
    except (ValueError, TypeError):
        return False

@patch('n8n_workflow_generator.openai.OpenAI')
def test_generate_valid_n8n_json_structure(mock_openai_class, workflow_system):
    # Mock the OpenAI client and its response
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message = MagicMock()
    # Ensure the content is a string that can be json.loads'd
    mock_completion.choices[0].message.content = json.dumps(MINIMAL_N8N_WORKFLOW)
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_client

    prompt = "Create a simple workflow"
    # Call the function that uses the LLM
    generated_json = get_n8n_json_from_llm(prompt, api_key="fake_key_for_testing")

    # Basic validation
    assert isinstance(generated_json, dict), "Generated output should be a dictionary"
    assert "name" in generated_json, "JSON must have a 'name' key"
    assert isinstance(generated_json["name"], str), "'name' must be a string"

    # Nodes validation
    assert "nodes" in generated_json, "JSON must have a 'nodes' key"
    assert isinstance(generated_json["nodes"], list), "'nodes' must be a list"
    assert len(generated_json["nodes"]) > 0, "'nodes' list should not be empty for a minimal valid workflow"
    for node in generated_json["nodes"]:
        assert isinstance(node, dict), "Each node must be a dictionary"
        assert "parameters" in node, "Node must have 'parameters' key"
        assert isinstance(node["parameters"], dict), "Node 'parameters' must be a dictionary"
        assert "id" in node, "Node must have 'id' key"
        assert is_valid_uuid(node["id"]), f"Node 'id' {node['id']} must be a valid UUID"
        assert "name" in node, "Node must have 'name' key"
        assert isinstance(node["name"], str), "Node 'name' must be a string"
        assert "type" in node, "Node must have 'type' key"
        assert isinstance(node["type"], str), "Node 'type' must be a string"
        assert "typeVersion" in node, "Node must have 'typeVersion' key"
        assert isinstance(node["typeVersion"], int), "Node 'typeVersion' must be an integer"
        assert "position" in node, "Node must have 'position' key"
        assert isinstance(node["position"], list), "Node 'position' must be a list"
        assert len(node["position"]) == 2, "Node 'position' must have two coordinates"
        assert all(isinstance(p, (int, float)) for p in node["position"]), "Node 'position' coordinates must be numbers"

    # Connections validation
    assert "connections" in generated_json, "JSON must have a 'connections' key"
    assert isinstance(generated_json["connections"], dict), "'connections' must be a dictionary"
    # Further connection validation can be added if complex workflows are tested

    # Metadata validation
    assert "active" in generated_json, "JSON must have an 'active' key"
    assert isinstance(generated_json["active"], bool), "'active' must be a boolean"
    assert "settings" in generated_json, "JSON must have a 'settings' key"
    assert isinstance(generated_json["settings"], dict), "'settings' must be a dictionary" # Can be {}
    assert "versionId" in generated_json, "JSON must have a 'versionId' key"
    assert is_valid_uuid(generated_json["versionId"]), f"'versionId' {generated_json['versionId']} must be a valid UUID"
    assert "createdAt" in generated_json, "JSON must have a 'createdAt' key"
    assert is_iso_8601_utc(generated_json["createdAt"]), f"'createdAt' {generated_json['createdAt']} is not a valid ISO 8601 UTC timestamp"
    assert "updatedAt" in generated_json, "JSON must have an 'updatedAt' key"
    assert is_iso_8601_utc(generated_json["updatedAt"]), f"'updatedAt' {generated_json['updatedAt']} is not a valid ISO 8601 UTC timestamp"
    
    # Check for new fields from issue #1 if they should be there by default
    # Based on the provided n8n_workflow_generator.py, these are NOT added by default by the LLM call.
    # The LLM prompt would need to be updated, or they'd need to be added in the enrichment phase.
    # For now, let's assume they are optional or added if the LLM includes them.
    # If MINIMAL_N8N_WORKFLOW is the direct output of the mock, then they will be present.
    assert "meta" in generated_json, "JSON should have 'meta' key" # As per MINIMAL_N8N_WORKFLOW
    assert generated_json["meta"] is None or isinstance(generated_json["meta"], dict), "'meta' should be None or a dict"
    assert "pinData" in generated_json, "JSON should have 'pinData' key" # As per MINIMAL_N8N_WORKFLOW
    assert generated_json["pinData"] is None or isinstance(generated_json["pinData"], dict), "'pinData' should be None or a dict"


@patch('n8n_workflow_generator.openai.OpenAI')
def test_n8n_workflow_system_returns_llm_output(mock_openai_class, workflow_system):
    # Mock the OpenAI client and its response for get_n8n_json_from_llm
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message = MagicMock()
    mock_completion.choices[0].message.content = json.dumps(MINIMAL_N8N_WORKFLOW)
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_client

    prompt = "Test prompt"
    result = workflow_system.create_workflow_from_text(prompt, export_filename=None)

    assert "n8n_workflow" in result
    assert result["n8n_workflow"]["name"] == "Test Workflow" # Check against mocked data
    assert result["status"] == "success"

@patch('n8n_workflow_generator.openai.OpenAI')
def test_llm_error_handling_returns_error_structure(mock_openai_class):
    # Simulate an API error from OpenAI
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("OpenAI API Down")
    mock_openai_class.return_value = mock_client

    prompt = "This will cause an error"
    error_json = get_n8n_json_from_llm(prompt, "fake_key_for_testing")

    assert "name" in error_json
    assert "Error" in error_json["name"]
    assert "nodes" in error_json
    assert len(error_json["nodes"]) == 1
    assert error_json["nodes"][0]["type"] == "n8n-nodes-base.stickyNote"
    assert "message" in error_json["nodes"][0]["parameters"]
    assert "OpenAI API Down" in error_json["nodes"][0]["parameters"]["message"]

# It might be useful to add a test for the N8NWorkflowSystem.create_workflow_from_text
# that checks file export, but that requires mocking `open` and `os.path.exists`.
# For now, focusing on the JSON generation validity.

# Add a test to ensure that the enrichment logic in get_n8n_json_from_llm works
# e.g. if LLM returns a slightly malformed/incomplete JSON
@patch('n8n_workflow_generator.openai.OpenAI')
def test_llm_response_enrichment(mock_openai_class):
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message = MagicMock()
    
    # Simulate LLM response missing some fields
    slightly_incomplete_workflow = {
        "name": "Needs Enrichment",
        "nodes": [
            {
                # Missing id, typeVersion, position, parameters
                "name": "Node 1", 
                "type": "n8n-nodes-base.set"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "", # Empty name
                "type": "n8n-nodes-base.wait",
                "typeVersion": 1,
                "position": [100,100],
                "parameters": {}
            }
        ]
        # Missing connections, active, settings, versionId, createdAt, updatedAt
    }
    mock_completion.choices[0].message.content = json.dumps(slightly_incomplete_workflow)
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_client

    enriched_json = get_n8n_json_from_llm("test enrichment", "fake_key")

    assert enriched_json["name"] == "Needs Enrichment"
    assert isinstance(enriched_json["active"], bool)
    assert isinstance(enriched_json["settings"], dict)
    assert is_valid_uuid(enriched_json["versionId"])
    assert is_iso_8601_utc(enriched_json["createdAt"])
    assert is_iso_8601_utc(enriched_json["updatedAt"])
    assert isinstance(enriched_json["connections"], dict)

    assert len(enriched_json["nodes"]) == 2
    node1 = enriched_json["nodes"][0]
    assert node1["name"] == "Node 1" # Name was present
    assert is_valid_uuid(node1["id"]) # Should be added
    assert isinstance(node1["typeVersion"], int) # Should be added
    assert isinstance(node1["position"], list) # Should be added
    assert isinstance(node1["parameters"], dict) # Should be added
    
    node2 = enriched_json["nodes"][1]
    assert node2["name"] == "Unnamed Node 2" # Should be renamed due to empty name
