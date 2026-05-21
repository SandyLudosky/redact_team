Créer une équipe de rédaction avec mémoire et RAG intégré

> Quickstart example to build a single-agent LLM-powered application using AutoChat.
> Powered by OpenAI's language model for real-time weather insights.
---

```sh

User → Writer → Researcher → Editor → Critic → (APPROVE)
                          ↓
                    Image Generator


```

[1]- Python Installation
[2]- Create and Activate a Virtual Environment
[3]- Install Packages
[4]- Set an environment variable called `OPENAI_API_KEY`

### [1]-Python Installation

#### macOS
1. **Check if Python is already installed**
   ```sh
   python3 --version
   ```
   If Python is not installed, proceed with the steps below.

2. **Install Homebrew (if not installed)**
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install Python**
   ```sh
   brew install python3
   ```

4. **Check Python Version**
   ```sh
   python3 --version
   ```

#### Windows
1. **Download Python** from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Run the installer** and check the box **"Add Python to PATH"** before proceeding with the installation.

3. **Check Python Version**
   ```sh
   python --version
   ```

---

### [2]-Create and Activate a Virtual Environment

#### macOS
1. **Navigate to your project directory**
   ```sh
   cd /path/to/your/project
   ```

2. **Create a virtual environment**
   ```sh
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**
   ```sh
   source .venv/bin/activate
   ```

4. **Verify that the virtual environment is active** (you should see `(venv)` in the terminal prompt).

#### Windows
1. **Navigate to your project directory**
   ```sh
   cd C:\path\to\your\project
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   ```sh
   .venv\Scripts\activate
   ```

4. **Verify that the virtual environment is active** (Command Prompt should show `(venv)` before the directory path).

---

## Deactivating the Virtual Environment
For both macOS and Windows, deactivate the virtual environment by running:
```sh
 deactivate
```

---

### [3]-Package Installation
(Mac)
```sh
pip3 install -r requirements.txt
pip3 install mem0ai
pip install fastapi uvicorn 

export PYTHONPATH=$PYTHONPATH:/path/to/autogen_agentchat
```

(Windows)
```sh
pip install -r requirements.txt
pip install mem0ai
pip install fastapi uvicorn 
```

---

## Exiting the Virtual Environment
Simply run:
```sh
deactivate
```

### [4]-OpenAI API Key


#### 1. Setting Up OpenAI Secret Key  
1. Create an OpenAI Account[OpenAI's API Keys page](https://platform.openai.com/signup/)
2. Go to [OpenAI's API Keys page](https://platform.openai.com/settings/organization/api-keys).
3. Click **Create new secret key** and copy it.  

####  2. Set Up the API Key Locally  

##### macOS & Linux  
You can store the key in your shell configuration file:  

```sh
echo 'export OPENAI_API_KEY="your-secret-key"' >> ~/.bashrc
source ~/.bashrc
````

or add to `.env` file

```sh
OPENAI_API_KEY="YOUR_API_KEY"

```

### -Start the app
(Mac)
```sh
python3 main.py
```

(Windows)
```sh
python main.py
```

Questions Examples : 
1. What kind of things did Paul Graham build or create as a child?

2. How did his interest in art and computers evolve over time?

3. What was Paul’s experience like at RISD (Rhode Island School of Design)?

4. How did the acquisition of Viaweb by Yahoo impact his path?

5. Why did Paul Graham start Y Combinator?

### Start the server

```bash
# Development (hot-reload)
python main.py

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production (no reload, multiple workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Interactive docs

| UI | URL |
|---|---|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |

---

## 📡 Endpoints

### `GET /health`
Returns service status.

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok" }
```

---

### `POST /run`
Runs the full multi-agent pipeline on a given task.

**Request body:**
```json
{
  "input": "Write an article about the impact of AI on education"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Write an article about the impact of AI on education"}'
```

**HTTPie:**
```bash
http POST localhost:8000/run input="Write an article about the impact of AI on education"
```

**Python (requests):**
```bash
curl -X POST http://localhost:8000/run \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "Write an article about the impact of AI on education"}'
```

**Response:**
```json
{
  "summary": "## AI in Education\n\n...",
  "image_path": "output/image_20240101.png",
  "error": null
}
```