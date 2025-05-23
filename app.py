import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from n8n_workflow_generator import N8NWorkflowSystem

app = Flask(__name__)
CORS(app) # Enable CORS for the entire application

# Retrieve OpenAI API key from environment variable
# The N8NWorkflowSystem will also try to retrieve this,
# but we can check it here for an early error if needed.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def home():
    return "N8N Workflow Generator server is running!"

@app.route('/generate-workflow', methods=['POST'])
def generate_workflow_route():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        return jsonify({"error": "OpenAI API key is not configured on the server."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to parse JSON payload: {str(e)}"}), 400

    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body."}), 400

    try:
        # Instantiate N8NWorkflowSystem.
        # The constructor of N8NWorkflowSystem is designed to pick up the API key
        # from os.environ if not provided, or use the one passed.
        # Passing it explicitly if available, otherwise it will use its internal logic.
        workflow_system = N8NWorkflowSystem(openai_api_key=OPENAI_API_KEY)
        
        # The create_workflow_from_text now directly returns a dictionary which includes
        # 'n8n_workflow' and 'status'. It handles file export internally if a filename is passed.
        # For the API, we don't need to export to a file here, just get the JSON.
        result = workflow_system.create_workflow_from_text(prompt, export_filename=None) # No server-side file export by default

        if result.get('status') == 'success':
            return jsonify(result.get('n8n_workflow', {})), 200
        else:
            # If status is 'error' or workflow is an error structure from get_n8n_json_from_llm
            error_message = "Failed to generate workflow."
            if 'n8n_workflow' in result and isinstance(result['n8n_workflow'], dict):
                # Try to get more specific error from the workflow structure itself (e.g., from sticky note)
                nodes = result['n8n_workflow'].get('nodes', [])
                if nodes and isinstance(nodes, list) and len(nodes) > 0:
                    first_node_params = nodes[0].get('parameters', {})
                    if 'message' in first_node_params and "Error" in result['n8n_workflow'].get('name', ""):
                        error_message = first_node_params['message']
            
            # Determine appropriate status code
            status_code = 500 # Default to internal server error
            if "API Key Missing" in error_message or "API Error" in error_message:
                status_code = 500
            elif "JSON Parsing Error" in error_message or "LLM Response/Validation Error" in error_message:
                status_code = 422 # Unprocessable Entity - prompt might be bad or LLM response malformed
            
            return jsonify({"error": error_message, "details": result.get('n8n_workflow')}), status_code

    except Exception as e:
        app.logger.error(f"Error during workflow generation: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Make sure to set the OPENAI_API_KEY environment variable before running
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        print("🔴 WARNING: OPENAI_API_KEY environment variable is not set or is using a placeholder.")
        print("   The /generate-workflow endpoint will return an error.")
        print("   Please set it for the API to function correctly, e.g.:")
        print("   export OPENAI_API_KEY='your_actual_api_key_here'")
    
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
