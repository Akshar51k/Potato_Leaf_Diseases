# 🥔 Potato Disease Classification

A full-stack deep learning application that classifies potato leaf diseases using a trained CNN model. Upload an image of a potato leaf and get instant disease predictions with confidence scores.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange?logo=tensorflow)
![React](https://img.shields.io/badge/React-17-blue?logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

---

## 🏗️ Architecture

```
┌──────────────┐       HTTP        ┌──────────────────┐       Keras       ┌──────────────┐
│   React UI   │ ───────────────►  │   FastAPI Server  │ ───────────────►  │  CNN Model   │
│  (Port 3000) │ ◄─────────────── │   (Port 8000)     │ ◄─────────────── │  (.h5 file)  │
└──────────────┘    JSON Response  └──────────────────┘    Predictions    └──────────────┘
```

## 🎯 Supported Classifications

| Class          | Description                        |
|----------------|------------------------------------|
| **Early Blight** | Alternaria solani fungal infection |
| **Late Blight**  | Phytophthora infestans infection   |
| **Healthy**      | No disease detected               |

---

## 📁 Project Structure

```
PlantVillage/
├── api/
│   ├── main.py              # FastAPI application (prediction endpoint)
│   ├── requirements.txt     # Python dependencies (pinned)
│   ├── Dockerfile           # Container config with health checks
│   ├── .env                 # Local environment config (gitignored)
│   ├── .env.example         # Template for environment variables
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── home.js          # Main UI component (drag-and-drop upload)
│   │   ├── App.js           # React app entry
│   │   └── index.js         # React DOM mount
│   ├── .env                 # Frontend environment config (gitignored)
│   ├── .env.example         # Template for frontend env vars
│   └── package.json
├── models/                  # Trained model files (gitignored — see setup)
│   └── potato_1.h5
├── docker-compose.yml       # Multi-service orchestration
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 16+** with npm
- **Git**

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd PlantVillage
```

### 2. Download Model Files

> ⚠️ Model files are not included in Git due to their size. Place them in the `models/` directory:

```
models/
└── potato_1.h5    # ~782 KB trained Keras model
```

### 3. Backend Setup

```bash
# Create and activate virtual environment
python -m venv myenv
myenv\Scripts\activate       # Windows
# source myenv/bin/activate  # macOS/Linux

# Install dependencies
cd api
pip install -r requirements.txt

# Configure environment
cp .env.example .env         # Edit .env if needed

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/ping`

### 4. Frontend Setup

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env         # Edit .env if needed

# Start development server
npm start
```

The UI will be available at `http://localhost:3000`

---

## 🐳 Docker (Alternative)

Run both services with Docker Compose:

```bash
docker-compose up --build
```

---

## 📡 API Reference

### `GET /ping`
Health check — returns `"Hello, I am alive"`.

### `GET /health`
Extended health check with model status.

```json
{ "status": "ok", "model_loaded": true }
```

### `POST /predict`
Upload a JPG/JPEG image for classification.

**Request**: `multipart/form-data` with field `file`

**Response**:
```json
{
  "class": "Early Blight",
  "confidence": 0.9987
}
```

---

## ⚙️ Environment Variables

### Backend (`api/.env`)

| Variable           | Default                                    | Description                  |
|--------------------|--------------------------------------------|------------------------------|
| `MODEL_PATH`       | `../models/potato_1.h5`                    | Path to Keras model file     |
| `ALLOWED_ORIGINS`  | `http://localhost,http://localhost:3000`    | CORS allowed origins (CSV)   |
| `PORT`             | `8000`                                     | Server port                  |
| `MAX_FILE_SIZE_MB` | `10`                                       | Max upload size in MB        |

### Frontend (`frontend/.env`)

| Variable             | Default                            | Description          |
|----------------------|------------------------------------|----------------------|
| `REACT_APP_API_URL`  | `http://localhost:8000/predict`    | Backend predict URL  |

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, TensorFlow/Keras, Pillow, Uvicorn
- **Frontend**: React 17, Material-UI, Axios, material-ui-dropzone
- **Infra**: Docker, Docker Compose
- **Model**: CNN trained on PlantVillage dataset

---

## 📄 License

This project is for educational purposes.
