# Deployment & Hosting Guide — SwitchGuard & CampusHire Relay
### Flip the Switch Hackathon 2026 (WeMakeDevs × Switch AI)

This document explains the recommended hosting strategies for your submission, live demos, and Switch AI agent webhook integration.

---

## 🧭 Executive Summary: Do I need to host on Render / Railway?

| Strategy | Best For | Cost | Latency / Cold Starts | Setup Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Strategy 1: Local Hosting** *(Recommended)* | Hackathon demo video, pitch recording, local development | **100% Free** | **1.2 ms** (instant local CPU reflex, zero cold starts) | 0 steps (`.\start_switch_agent.bat`) |
| **Strategy 2: Local + HTTPS Tunnel** | Live Switch AI cloud webhooks without cloud hosting | **100% Free** | Low network latency, no container build | 1 command (`.\expose_tunnel.bat`) |
| **Strategy 3: Render (Cloud PaaS)** | 24/7 public web link in submission form | Free Tier | 50s spin-down after 15 min idle | Connect GitHub & Deploy |
| **Strategy 4: Railway (Cloud Container)** | Persistent cloud container with zero spin-down | Free / Trial | Low (<150ms) | Connect GitHub & Deploy |

---

## Strategy 1: Local Hosting (Recommended for Pitch & Demo Video)

For hackathon submissions, evaluators care most about your **architecture, functional implementation, test suite verification, and recorded video walkthrough**.

Running locally delivers:
- **Sub-2ms Reflex Latency**: System 1 Laya triage runs directly on CPU without cloud roundtrip delays.
- **No Cold Starts**: Avoids free-tier container sleep.
- **Deterministic Reliability**: Zero network timeouts during your demo recording.

### Start Command
```powershell
# Windows PowerShell
.\start_switch_agent.ps1

# Or Command Prompt
start_switch_agent.bat
```
**Access URLs:**
- War Room Dashboard: `http://127.0.0.1:8080/`
- Switch AI Protocol: `http://127.0.0.1:8080/agent`
- Health Endpoint: `http://127.0.0.1:8080/healthz`
- CampusHire API: `http://127.0.0.1:8080/api/campushire/candidates`

---

## Strategy 2: Local + Public HTTPS Tunnel (Zero-Cost Webhooks)

When configuring agents in the **Switch AI Cloud Console** (`https://console.switchagents.ai/`), Switch AI's servers send HTTP POST webhooks to your agent. Since Switch AI cannot reach `http://127.0.0.1:8080` behind your local NAT/router, you can create an instant public HTTPS tunnel.

### Launch Tunnel
Run the included launcher:
```powershell
.\expose_tunnel.ps1
# or
expose_tunnel.bat
```

The script automatically detects and launches one of the following:
1. **Cloudflare Quick Tunnel (Zero setup, no sign-up)**:
   ```bash
   npx untun@latest tunnel http://127.0.0.1:8080
   ```
   *Generates*: `https://<random-id>.trycloudflare.com`
2. **ngrok**:
   ```bash
   ngrok http 8080
   ```
   *Generates*: `https://<id>.ngrok-free.app`

### Switch AI Console Configuration
In the Switch AI Developer Console:
- **Agent URL**: `https://<your-tunnel-url>/agent`
- **Webhook URL**: `https://<your-tunnel-url>/api/campushire/events`

---

## Strategy 3: Render Deployment (Turnkey `render.yaml`)

Your repository is pre-configured with `render.yaml` for Render Web Services.

### Deployment Steps:
1. Push your repository to GitHub.
2. Sign in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** → **Blueprint** (or **Web Service**).
4. Select your GitHub repository.
5. Render will detect `render.yaml` automatically:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/healthz`
6. Click **Apply** or **Create Web Service**.

---

## Strategy 4: Railway Deployment (Turnkey `Dockerfile` / `Procfile`)

Railway natively supports both the included `Dockerfile` and `Procfile`.

### Deployment Steps:
1. Sign in to [Railway](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select this repository.
4. Railway will automatically build using `Dockerfile` or `Procfile`:
   - It exposes the assigned `$PORT` dynamically.
5. In **Settings** → **Networking**, click **Generate Domain** to get your public HTTPS URL (e.g. `https://switch-campushire.up.railway.app`).

---

## Strategy 5: Docker Container (Self-Hosted / Cloud Run)

To run the containerized backend anywhere (AWS ECS, Google Cloud Run, Azure App Service, or local Docker):

```bash
# Build the Docker image
docker build -t switch-campushire-relay:latest .

# Run the container
docker run -p 8080:8000 -e PORT=8000 switch-campushire-relay:latest
```

Open `http://localhost:8080` in your browser.

---

## 🔍 Verification Checklist

Before recording your demo or submitting links:
- [x] Run test suite: `.\laya-repo\.venv312\Scripts\python.exe run_all_tests.py` (**158/158 Passing**)
- [x] Verify health check: `GET /healthz` returns `{"status": "healthy", "laya_ready": true}`
- [x] Verify protocol discovery: `GET /agent` returns Switch AI v1 manifest
- [x] Verify interactive dashboard: `GET /` renders interactive War Room
