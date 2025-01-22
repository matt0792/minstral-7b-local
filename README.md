# Mistral 7B Chat Interface

A local chatbot interface optimized for Apple Silicon (M-series) MacBooks with Metal acceleration, powered by Mistral-7B-Instruct with a React frontend and FastAPI backend.

## Setup Guide

### Prerequisites
- **Apple Silicon Mac** (M1/M2/M3)
- Python 3.11+
- Node.js 18+
- 8GB+ RAM (16GB recommended)

---

## 1. Clone repo to local device

```bash
git clone https://github.com/matt0792/minstral-7b-local.git
```

---

## 2. Backend Setup

```bash
# Navigate to project root
cd minstral-7b-local

# Create virtual environment (if missing)
python -m venv llm-env

# Activate environment
source llm-env/bin/activate 

# Install requirements with Metal support
CMAKE_ARGS="-DLLAMA_METAL=on" pip install -r backend/requirements.txt
```

### Download Model
```bash
# Create model directory if missing
mkdir -p backend/model

# Download model
wget -P backend/model/ \
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

### Run Backend
```bash
cd backend
export LLAMA_METAL=1
uvicorn server:app --reload
```
Access API: `http://localhost:8000`

---

## 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access UI: `http://localhost:5173`

---

## Project Structure
```
minstral-7b-local/
├── llm-env/            # Virtual environment (ROOT)
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── model/          # Contains .gguf model
└── frontend/           # React app
```

---

**Created with ♥ by Matt Thompson**  