# PARROT LLM Intelligence Service

This is the LLM Intelligence Layer for the PARROT medical consultation monitoring application. It runs as a lightweight, independent FastAPI microservice on port **8001** and communicates with the Groq API (using the free `llama-3.3-70b-versatile` model).

## Features
1. **Live Clinical Advice (`/advice`)**: Processes real-time patient telemetry + live transcription and returns 15-second micro-assessments with clinical suggestions for the doctor.
2. **Session Clinical Summary (`/summary`)**: Generates structured, evidence-based post-session clinical notes, key findings, and recommendations.
3. **Medical Guardrails**: Strict instructions constrain the LLM to clinical topics only, refusing off-topic queries.

## Requirements
- Python 3.8+
- Groq API Key (Sign up free at [console.groq.com](https://console.groq.com))

## Installation

1. Navigate to the project directory:
   ```bash
   cd Parrot-LLM
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example and fill in your Groq API Key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add:
   ```env
   GROQ_API_KEY=gsk_...
   ```

## Running the Service

Start the FastAPI application:
```bash
python app.py
```
The server will start at `http://localhost:8001`.

## Endpoints
- **GET `/health`**: Returns service and LLM connection status.
- **POST `/advice`**: Generates real-time patient guidance.
- **POST `/summary`**: Generates post-consultation documentation.
