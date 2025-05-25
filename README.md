# N8N AI Workflow Generator

[![Open in Visual Studio Code](https://img.shields.io/static/v1?label=Open%20in&message=VS%20Code&logo=visualstudiocode&color=007ACC)](https://vscode.dev/github/YOUR_USERNAME/YOUR_REPONAME) <!-- Replace YOUR_USERNAME/YOUR_REPONAME -->
[![Open in Gitpod](https://img.shields.io/badge/Open%20in-Gitpod-blue?logo=gitpod)](https://gitpod.io/#https://github.com/YOUR_USERNAME/YOUR_REPONAME) <!-- Replace YOUR_USERNAME/YOUR_REPONAME -->
[![Build Status](https://github.com/YOUR_USERNAME/YOUR_REPONAME/actions/workflows/main.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPONAME/actions/workflows/main.yml) <!-- Replace YOUR_USERNAME/YOUR_REPONAME -->

Generate n8n workflows from natural language prompts using AI! This service takes your plain text description and converts it into n8n workflow JSON, ready for import.

Optionally, configure it to automatically import the generated workflow into your n8n instance.

<!-- Placeholder for GIF Screencast -->
<!--
**Demo Video/GIF:**
[Link to GIF/Video showing the app in action]
-->

## Core Features

*   **AI-Powered Generation:** Leverages Large Language Models (OpenAI) to understand your prompts.
*   **Flask Web Service:** Provides an API endpoint (`/generate-workflow`) to receive prompts and return n8n JSON.
*   **Direct n8n Import:** Generated JSON is compatible for direct import into n8n.
*   **Optional Auto-Import:** Connect to your n8n instance to have new workflows appear automatically.
*   **Containerized:** Dockerfile and docker-compose setup for easy local development and deployment.
*   **Multiple Deploy Targets:** Configuration provided for Heroku, Render, Railway, and Azure.
*   **CI/CD:** GitHub Actions for linting, testing, building, and publishing Docker images, with optional redeployment triggers.

## Quick Start (Local Development with Docker)

1.  **Prerequisites:**
    *   Docker and Docker Compose installed.
    *   Git installed.
    *   An OpenAI API Key.

2.  **Clone & Configure:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPONAME.git # Replace YOUR_USERNAME/YOUR_REPONAME
    cd YOUR_REPONAME # Replace YOUR_REPONAME
    cp .env.example .env
    ```
    Edit `.env` and add your `OPENAI_API_KEY`. For auto-import, also set `N8N_URL` and `N8N_API_KEY` (referring to your n8n instance).

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    *   The generator app will be available at `http://localhost:5000`.
    *   The n8n instance (if you keep it in `docker-compose.yml`) will be at `http://localhost:5678`.

    You can then send POST requests to `http://localhost:5000/generate-workflow` with a JSON body like `{"prompt": "your workflow description"}`.

## Deployment

This application is designed to be deployed to various platforms. Click the buttons below to deploy, or use the provided configuration files.

**Deployment Options:**

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/YOUR_REPONAME) <!-- Replace YOUR_USERNAME/YOUR_REPONAME -->

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/YOUR_REPONAME) <!-- Replace YOUR_USERNAME/YOUR_REPONAME -->

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/YOUR_REPONAME&envs=OPENAI_API_KEY,N8N_URL,N8N_API_KEY&OPENAI_API_KEY_DESCRIPTION=Your%20OpenAI%20API%20Key&N8N_URL_DESCRIPTION=(Optional)%20URL%20of%20your%20n8n%20instance&N8N_API_KEY_DESCRIPTION=(Optional)%20Your%20n8n%20API%20Key) <!-- Replace YOUR_USERNAME/YOUR_REPONAME. Railway button can prefill env vars. -->

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2FYOUR_REPONAME%2Fmain%2Fmain.bicep/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2FYOUR_REPONAME%2Fmain%2Fportaluidashboard.json) <!-- Replace YOUR_USERNAME/YOUR_REPONAME. Requires main.bicep and a portal UI definition for one-click. For now, this links to template deployment. -->

**Configuration Files:**

*   **Heroku:** Uses `app.json` (for the Deploy button) and `Procfile`.
*   **Render:** Uses `render.yaml` to define services for the generator and n8n.
*   **Railway:** A `railway.json` is provided to help scaffold services. Railway's Nixpacks or Dockerfile build will be used.
*   **Azure:** Uses `main.bicep` and `azuredeploy.parameters.json` for deployment via Azure CLI or Portal. The Docker image for the generator app should be available on Docker Hub (automated by GitHub Actions).
*   **Docker Hub:** The CI pipeline automatically builds and pushes Docker images to Docker Hub (configure `yourusername/n8n-workflow-generator` in `.github/workflows/main.yml` and set `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets in GitHub).

## Developer Environments

Quickly get started with development using pre-configured cloud environments:

*   **GitHub Codespaces:** Click the "Open in VS Code" badge above or open manually.
*   **Gitpod:** Click the "Open in Gitpod" badge above.

Configuration is in `.devcontainer/devcontainer.json` for Codespaces/Dev Containers and `.gitpod.yml` for Gitpod.

## Project Structure

*   `app.py`: Flask application providing the API.
*   `n8n_workflow_generator.py`: Core logic for LLM interaction and n8n JSON generation.
*   `n8n_web_interface.html`: A basic HTML interface (primarily for local testing/demo if run without Docker). <!-- This file's utility is reduced with API focus -->
*   `tests/`: Pytest unit and integration tests.
*   `Dockerfile`: For building the generator app's Docker image.
*   `docker-compose.yml`: For local development, running the generator and an n8n instance.
*   `.github/workflows/`: GitHub Actions for CI/CD.
*   Deployment configs: `app.json`, `render.yaml`, `railway.json`, `main.bicep`.
*   Developer configs: `.devcontainer/`, `.gitpod.yml`.

<!-- Environment Variables and FAQ sections will be added below -->

## Environment Variables

The following environment variables are used by the application and services. Some are required for core functionality, while others are optional or specific to certain deployment environments.

| Variable                 | Required | Default                                  | Scope                      | Description                                                                                                                               |
|--------------------------|----------|------------------------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `OPENAI_API_KEY`         | Yes      | None                                     | Generator App (Runtime)    | Your OpenAI API key. Essential for generating workflows.                                                                                  |
| `FLASK_DEBUG`            | No       | `0` (production), `1` (development)      | Generator App (Runtime)    | Set to `1` for Flask debug mode (local dev only). Should be `0` in production.                                                            |
| `PYTHONUNBUFFERED`       | No       | `1`                                      | Generator App (Runtime)    | Recommended to `1` to ensure Python output (logs) is sent straight to stdout/stderr without buffering, crucial for containerized logging. |
| `N8N_URL`                | No       | None                                     | Generator App (Runtime)    | Full URL of your n8n instance (e.g., `http://localhost:5678` or `https://your-n8n.onrender.com`) for the auto-import feature.        |
| `N8N_API_KEY`            | No       | None                                     | Generator App (Runtime)    | Your n8n API key (from n8n Admin settings > API) for the auto-import feature.                                                             |
| `DOCKER_IMAGE_NAME`      | N/A      | `yourusername/n8n-workflow-generator`    | GitHub Actions (Buildtime) | Docker Hub repository name used in CI/CD workflow (`.github/workflows/main.yml`). **User must update.**                               |
| `DOCKERHUB_USERNAME`     | N/A      | None                                     | GitHub Actions (CI Secret) | Your Docker Hub username. Required as a GitHub secret for publishing the Docker image.                                                    |
| `DOCKERHUB_TOKEN`        | N/A      | None                                     | GitHub Actions (CI Secret) | Your Docker Hub access token. Required as a GitHub secret for publishing the Docker image.                                                  |
| `RENDER_DEPLOY_HOOK_URL_GENERATOR` | N/A    | None                                     | GitHub Actions (CD Secret) | Deploy hook URL from Render for the generator service, used by `redeploy.yml` workflow.                                                   |
| `RENDER_DEPLOY_HOOK_URL_N8N` | N/A    | None                                     | GitHub Actions (CD Secret) | (Optional) Deploy hook URL from Render for the n8n service, used by `redeploy.yml` workflow.                                            |
| `N8N_ENCRYPTION_KEY`     | Yes (n8n)| `CHANGEME_VERY_IMPORTANT_SECURE_KEY`     | n8n Service (Runtime)      | **Critical for n8n.** A secure, random string for encrypting credentials in n8n. Set this when deploying n8n.                             |
| `GENERIC_TIMEZONE`       | No (n8n)| `Europe/Berlin` (example)                | n8n Service (Runtime)      | Timezone for the n8n instance.                                                                                                            |
| `N8N_HOST`               | No (n8n)| `0.0.0.0` (for Docker)                   | n8n Service (Runtime)      | Hostname n8n listens on. `0.0.0.0` makes it accessible within Docker networks.                                                            |
| `WEBHOOK_TUNNEL_URL`     | No (n8n)| None                                     | n8n Service (Runtime)      | If n8n needs a tunnel for webhooks during local dev or specific setups (e.g. `https://[subdomain].ngrok-free.app` if using ngrok with n8n). Generally not needed for production cloud deploys. |

**Note on `YOUR_USERNAME/YOUR_REPONAME`:** Throughout the documentation and configuration files, `YOUR_USERNAME/YOUR_REPONAME` is a placeholder. Please replace it with your actual GitHub username and repository name when customizing this project.

## FAQ (Frequently Asked Questions)

**Q1: I'm getting an error related to the OpenAI API Key when trying to generate a workflow.**

*   **A1:** This usually means your `OPENAI_API_KEY` is missing, incorrect, or your OpenAI account has an issue (e.g., exceeded quota, billing problem).
    *   **Check if Set:** Ensure the `OPENAI_API_KEY` environment variable is correctly set where your generator application is running (e.g., in your `.env` file for local Docker, in the environment variable settings of your deployment platform like Heroku, Render, Azure).
    *   **Verify Key:** Double-check that the key itself is valid and has no typos.
    *   **OpenAI Dashboard:** Log in to your OpenAI account dashboard to check your API usage, quota, and billing status.
    *   **Rate Limits:** You might be hitting rate limits. Check OpenAI's rate limit documentation.

**Q2: The workflow was generated, but it failed to auto-import into n8n.**

*   **A2:** This could be due to several reasons:
    *   **`N8N_URL` or `N8N_API_KEY` not set:** Ensure these environment variables are correctly set for the generator application, pointing to your active n8n instance and a valid n8n API key.
    *   **Incorrect `N8N_URL`:** Verify the URL is correct and the n8n instance is accessible from where the generator app is running (e.g., network connectivity, public URL if deployed separately).
    *   **Invalid `N8N_API_KEY`:** Regenerate or check your n8n API key in n8n's Admin settings. Ensure it has the necessary permissions (usually core API keys have workflow create permissions).
    *   **n8n Instance Down/Error:** Your n8n instance might be down or experiencing issues. Check its logs.
    *   **Network Issues:** Firewalls or network policies might be preventing the generator app from reaching the n8n API.
    *   **API Endpoint:** The generator uses `/api/v1/workflows` to import. While standard, very old or custom n8n setups might differ.

**Q3: My n8n instance isn't saving credentials or workflows correctly after deploying it (e.g., via Render, Railway, or Azure Bicep with ACI).**

*   **A3:** This is almost always due to **missing or misconfigured persistent storage** for n8n and/or a **missing `N8N_ENCRYPTION_KEY`**.
    *   **Persistent Storage:** n8n needs a volume mounted at `/home/node/.n8n` inside its container to persist its SQLite database (which stores workflows, credentials, etc.) and user files. Ensure your deployment configuration (`render.yaml`, `railway.json`, Azure template) correctly defines and mounts a persistent disk/volume for n8n.
    *   **`N8N_ENCRYPTION_KEY`:** This environment variable is **critical**. If not set, n8n might run but will not be able to save encrypted data like credentials properly. If you set it *after* n8n has already started and tried to save data, you might encounter issues. It's best to set it from the very first deployment of n8n and keep it consistent. It should be a long, random, and secure string.

**Q4: Where do I find the "Deploy to Azure" button or how do I use the Bicep template?**

*   **A4:** The README includes an Azure deployment badge. Clicking it will take you to the Azure portal to deploy the `main.bicep` template. You'll need to have your Docker image for the generator app already published to a container registry like Docker Hub, and you'll provide its name as a parameter during the Azure deployment setup (e.g., `yourdockerhubusername/your-repo-name:latest`). You will also need to provide your OpenAI API key and other parameters as prompted.

**Q5: How does the Railway deployment work?**

*   **A5:** The `railway.json` file provides a basic configuration that can help Railway understand your project structure, especially if you have a Dockerfile. When you create a new project on Railway from your Git repository, Railway will detect the Dockerfile and use it to build and deploy the `n8n-workflow-generator` service. You can then add the `n8n` service manually in the Railway dashboard by specifying the `n8nio/n8n:latest` Docker image. The `railway.json` also hints at necessary environment variables which you'll need to configure in Railway's variable management system (referencing secrets where appropriate).

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
