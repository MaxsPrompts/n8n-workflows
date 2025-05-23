# N8N AI Workflow Generator

## Overview

The N8N AI Workflow Generator is a web service that takes a plain language prompt and uses an AI (Large Language Model - LLM) to generate a downloadable n8n workflow JSON file. This allows users to quickly create n8n workflows by simply describing their desired automation in English.

## Features

*   Simple web interface for providing workflow prompts.
*   Utilizes OpenAI's LLM for intelligent workflow generation.
*   Generates `workflow.json` files suitable for direct import into n8n.
*   Includes server-side validation to improve the quality of the generated JSON.

## Files

*   **`n8n_web_interface.html`**: The client-side HTML web page for user interaction.
*   **`app.py`**: A Flask web server that handles user requests, interacts with the LLM, and serves the generated workflow.
*   **`n8n_workflow_generator.py`**: The Python module responsible for the core logic of calling the OpenAI LLM, processing the prompt, and generating/validating the n8n JSON structure.
*   **`LICENSE`**: Contains the licensing information for this project (MIT License).

## Setup Instructions

### Prerequisites

*   Python 3.7+
*   `pip` (Python package installer, usually comes with Python)

### Installation

1.  **Get the code:**
    *   If this is a Git repository, clone it:
        ```bash
        git clone <repository_url>
        cd <repository_directory>
        ```
    *   Otherwise, download all project files (`n8n_web_interface.html`, `app.py`, `n8n_workflow_generator.py`) into a single directory.

2.  **Install Python dependencies:**
    Open your terminal or command prompt and run:
    ```bash
    pip install Flask openai Flask-CORS
    ```

### Configuration

1.  **OpenAI API Key:**
    This service requires a valid OpenAI API key to function. You need to set this key as an environment variable named `OPENAI_API_KEY`.

    *   **For macOS/Linux:**
        ```bash
        export OPENAI_API_KEY="your_openai_api_key_here"
        ```
        To make this permanent, add the line to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`) and then source it (e.g., `source ~/.bashrc`).

    *   **For Windows (Command Prompt):**
        ```bash
        set OPENAI_API_KEY=your_openai_api_key_here
        ```
    *   **For Windows (PowerShell):**
        ```powershell
        $Env:OPENAI_API_KEY="your_openai_api_key_here"
        ```
        For permanent setting on Windows, search for "environment variables" in the system settings.

    **Important:** Replace `"your_openai_api_key_here"` with your actual OpenAI API key. Without a valid key, the workflow generation will fail.

## Running the Service

1.  **Start the Server:**
    Navigate to the directory containing the project files in your terminal and run:
    ```bash
    python app.py
    ```
    The server will typically start on `http://127.0.0.1:5000`. You should see output in the terminal indicating it's running.

2.  **Access the Web Interface:**
    *   Open the `n8n_web_interface.html` file directly in your web browser (e.g., by double-clicking it or using "File > Open" in your browser).
    *   **Important Note:** The development process for `n8n_web_interface.html` encountered tool limitations that may have prevented the file from being correctly updated by the AI agent. If the web interface does not function as expected (e.g., buttons don't work, no response from the server), you may need to manually replace its content with the final version provided during the development interaction logs.

## How to Use

1.  **Open `n8n_web_interface.html`** in your web browser.
2.  **Enter your prompt:** In the text area, describe the workflow you want to automate in plain English. For example: "When a new email arrives with the subject 'invoice', save any attachments to Google Drive in a folder named 'Invoices', and then send a Slack message to the #accounting channel with the filename."
3.  **Click "Generate Workflow".**
4.  **Wait for generation:** The interface will show a loading indicator.
5.  **Review and Download:**
    *   If successful, a preview of the generated n8n workflow JSON will appear in the "Workflow Output" section.
    *   A download button will also appear, allowing you to save the `workflow.json` file (the filename might be based on the workflow name).
    *   If there's an error (e.g., API key issue, problem with the prompt), an error message will be displayed.
6.  **Import to n8n:**
    *   In your n8n instance, go to "Workflows".
    *   Click the "Import from File" button.
    *   Select the downloaded `workflow.json` file.
    *   Review the imported workflow and make any necessary adjustments to credentials or specific node configurations.

---

This project aims to simplify n8n workflow creation through the power of AI. Enjoy automating!
