---
description: Intelligent startup guide for the Algo Trading App, handling environment detection and remote connectivity.
---

# Smart Environment Startup

This workflow guides the AI Agent on how to start the application based on the host operating system.

## 1. Detect Environment
Run `uname -a` or check the OS.

---

## 2. Strategy Application

### ➤ If Host is MacOS (Local Mission Control)
**Objective**: Run the Dashboard (Frontend) and a local API proxy connected to the Remote Database.

**Step 1: Check Prerequisites**
*   **Node.js**: Must be v18 or newer. Run `node -v`.
*   **Python**: Ensure virtual environment is active.

**Step 2: Establish Remote Database Link (SSH Tunnel)**
*   The local backend needs access to the remote MySQL database.
*   **Action**: Create an SSH Tunnel forwarding local port `3306` to remote `3306`.
*   **Command**: 
    ```bash
    ssh -N -L 3306:127.0.0.1:3306 devuser@192.168.4.42
    ```
*   **Credential**: `Hjbljy88$$` (if prompted, though keys are preferred).
*   **Verification**: Check if port 3306 is listening locally.

**Step 3: Start Local API Service**
*   With the tunnel active, the local API can connect to "localhost".
*   **Command**: `uvicorn api.main:app --port 8001`
*   *Why?* The frontend (Vite) connects to `localhost:8001`.

**Step 4: Start Frontend Dashboard**
*   **Location**: `dashboard/` directory.
*   **Command**: `npm run dev`

---

### ➤ If Host is Windows/Remote (Execution Engine)
**Objective**: Run the full trading stack.

**Step 1: Database Check**
*   Ensure Docker/MySQL service is running.

**Step 2: Start API Service**
*   **Command**: `uvicorn api.main:app --host 0.0.0.0 --port 8001`
*   *Note*: Binds to `0.0.0.0` to allow external access if needed.
