# Trixie Wellness - Deployment Guide

This document outlines how to deploy the Trixie Wellness application to various cloud providers.

## General Cloud Deployment Readiness
The application has been containerized using Docker, making it highly portable.
- **Port Binding**: The app automatically binds to the port provided by the cloud provider via the `PORT` environment variable (defaults to `8000`).
- **Database**: The application currently uses SQLite (`trixie_wellness.db`). **Important**: In ephemeral container environments (like Render free tier, Railway without volumes, or Azure Container Apps), your database will reset every time the container restarts. It is highly recommended to attach a persistent volume to your cloud deployment or migrate to a managed database (e.g., PostgreSQL) for production.

---

## 1. Render (Recommended for Web Apps)
Render is an excellent choice for deploying this FastAPI backend due to its native Docker support and ease of use.

### Steps:
1. Push your code to a GitHub/GitLab repository.
2. Log in to [Render](https://render.com) and create a new **Web Service**.
3. Connect your repository.
4. Render will automatically detect the `Dockerfile`.
5. Under **Environment Variables**, you can add any necessary API keys (e.g., `OPENAI_API_KEY`).
6. **Persistent Storage (Optional but recommended)**: Go to the "Disks" section and add a disk mounted at `/app` to ensure your `trixie_wellness.db` is not lost between deployments.

---

## 2. Railway
Railway offers a very seamless developer experience and fast deployments.

### Steps:
1. Push your code to a GitHub repository.
2. Log in to [Railway](https://railway.app) and create a new Project.
3. Select **Deploy from GitHub repo** and choose your repository.
4. Railway will automatically build and deploy using the `Dockerfile`.
5. Go to the **Variables** tab to add your environment variables (`OPENAI_API_KEY`, etc.).
6. Go to the **Settings** tab and generate a public domain for your service.
7. **Persistent Storage**: To keep your SQLite DB data, you will need to add a Volume in Railway and mount it to `/app`.

---

## 3. Hugging Face Spaces (Recommended for AI Portfolios)
If you want to showcase this as an AI project, Hugging Face Spaces is a great platform.

### Steps:
1. Log in to [Hugging Face](https://huggingface.co/) and create a new **Space**.
2. Set the Space SDK to **Docker** and choose "Blank" template.
3. Clone the space repository locally and copy your project files into it, or upload them directly via the web UI.
4. By default, Hugging Face expects your app to run on port `7860`. Our application reads the `PORT` environment variable, which Hugging Face automatically provides.
5. In your Space's **Settings**, scroll down to **Variables and secrets** to add your API keys.
6. **Note**: Free spaces go to sleep after inactivity, resetting the SQLite DB unless you upgrade to persistent storage.

---

## 4. Azure
For enterprise-level deployment, Azure provides several options. The easiest is Azure App Service.

### Steps for Azure App Service:
1. Make sure you have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in.
2. Build and push your Docker image to a registry (like Azure Container Registry or Docker Hub).
   ```bash
   docker build -t your-dockerhub-username/trixie-wellness .
   docker push your-dockerhub-username/trixie-wellness
   ```
3. Create a Web App for Containers:
   - Go to the Azure Portal -> **App Services** -> **Create**.
   - Choose **Publish**: Docker Container.
   - Choose **Operating System**: Linux.
   - In the Docker tab, point it to your Docker image.
4. Under the Web App's **Configuration**, add your environment variables as **Application settings**.
5. Set the `WEBSITES_PORT` application setting to `8000` to tell Azure which port the container is listening on (or rely on the `PORT` environment variable).

## Environment Variables to Configure
No matter which platform you choose, remember to configure the following environment variables if your app depends on them:
- `OPENAI_API_KEY` (if used by your LLM logic)
- `GOOGLE_API_KEY` (if used)
- Any other keys present in your local `.env` file (do not commit your `.env` file to version control).
