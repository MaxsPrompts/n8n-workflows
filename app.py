#!/usr/bin/env python3
"""
Flask API for n8n Workflow Generator
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from n8n_workflow_generator import N8NWorkflowSystem # Assuming your main class is N8NWorkflowSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load OpenAI API Key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# It's good practice to also allow this to be configurable for the n8n instance if needed
N8N_URL = os.environ.get("N8N_URL")
N8N_API_KEY = os.environ.get("N8N_API_KEY")


@app.route('/')
def home():
    """Serves a simple welcome message or a basic HTML page."""
    return jsonify({
        "message": "n8n Workflow Generator API is running.",
        "endpoints": {
            "/generate-workflow": "POST a prompt to generate an n8n workflow.",
            "/health": "GET to check API health."
        },
        "version": "0.2.0" # Simple versioning
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Provides a simple health check endpoint."""
    # Check if critical services like OpenAI API key are available
    api_key_status = "configured" if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY" else "missing_or_placeholder"
    
    # Check n8n connectivity if configured for import
    n8n_import_configured = bool(N8N_URL and N8N_API_KEY and N8N_API_KEY != "YOUR_N8N_API_KEY_HERE")
    
    return jsonify({
        "status": "healthy", 
        "timestamp": os.path.getmtime(__file__), # Example: last modified time of this file
        "dependencies": {
            "openai_api_key": api_key_status,
            "n8n_auto_import_configured": n8n_import_configured
        }
    }), 200

@app.route('/generate-workflow', methods=['POST'])
def generate_workflow_route():
    """
    Endpoint to generate an n8n workflow from a text prompt.
    Expects a JSON body with a 'prompt' field.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        app.logger.error("OpenAI API key is not configured on the server.")
        return jsonify({"error": "OpenAI API key is not configured. Cannot process requests."}), 503 # Service Unavailable

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body."}), 400

    prompt = data.get('prompt')
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "'prompt' must be a non-empty string."}), 400

    # Optional: Get export_filename from request, default to None
    export_filename_req = data.get('export_filename') # e.g., "my_workflow" or True

    try:
        # Initialize the workflow system. The API key is passed to the constructor if needed.
        # The N8NWorkflowSystem constructor will use the environment variable if no key is passed.
        workflow_system = N8NWorkflowSystem(openai_api_key=OPENAI_API_KEY)
        
        # Call the method to convert text to workflow
        # Pass export_filename=None as we don't want the API to write files to its own filesystem by default.
        # File export could be a separate, more controlled endpoint if needed, or configured via env var.
        # For now, the primary output is the JSON response.
        result = workflow_system.create_workflow_from_text(prompt, export_filename=None) # Changed from export_filename_req

        response_payload = {
            "generated_workflow": result.get('n8n_workflow', {}),
            "generation_status": result.get('status', 'error'),
            "n8n_import_status": result.get('n8n_import_status', 'not_attempted'),
            "n8n_workflow_id": result.get('n8n_workflow_id')
        }
        
        if result.get('status') == 'success':
            app.logger.info(f"Successfully generated workflow for prompt: '{prompt[:50]}...'")
            return jsonify(response_payload), 200
        else:
            # If generation itself failed (e.g., LLM error, validation error in get_n8n_json_from_llm)
            error_message = "Failed to generate workflow."
            # The 'n8n_workflow' part of the result might contain a sticky note with error details
            details = result.get('n8n_workflow') 
            if details and isinstance(details, dict) and "nodes" in details and details["nodes"]:
                first_node = details["nodes"][0]
                if "Error" in first_node.get("name", "") and "message" in first_node.get("parameters", {}):
                    error_message = first_node["parameters"]["message"]

            app.logger.error(f"Failed to generate workflow for prompt: '{prompt[:50]}...'. Details: {error_message}")
            return jsonify({"error": error_message, "details": details}), 500

    except Exception as e:
        app.logger.error(f"Unexpected server error during workflow generation for prompt '{prompt[:50]}...': {e}", exc_info=True)
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Bind to 0.0.0.0 to be accessible externally (e.g., in Docker)
    # Port 5000 is common for Flask apps
    # Debug mode should be OFF in production
    is_debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=5000, debug=is_debug_mode)
