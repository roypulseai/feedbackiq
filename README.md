# FeedbackIQ

> Multilingual sentiment analysis and topic modeling for user feedback.

FeedbackIQ is a fully containerized, offline-capable Streamlit application that ingests feedback data (CSV or PostgreSQL), runs multilingual sentiment analysis using Hugging Face Transformers, and discovers themes with BERTopic topic modeling. Designed to run on low-spec machines (Intel i3, 8GB RAM).

## Features

- **CSV Upload** — Drop in any feedback CSV file and analyze text columns.
- **PostgreSQL Integration** — Connect directly to a database and run custom queries.
- **Multilingual Sentiment** — Powered by `lxyuan/distilbert-base-multilingual-cased-sentiments-student` (supports 6+ languages).
- **Topic Discovery** — Automatic theme extraction via BERTopic with multilingual sentence embeddings.
- **Interactive Dashboard** — Sentiment distribution bar chart, top topics, and a sortable data table.
- **One-Click Export** — Download analyzed results as CSV.
- **Offline Ready** — All ML models are baked into the Docker image — no internet needed at runtime.
- **Portable Delivery** — Single `.tar` image + launcher script for Windows or macOS.

## Quick Start (End User)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Windows

1. Double-click `Start_App.bat`.
2. Docker loads the image and opens `http://localhost:8501` in your browser.

### macOS

1. Open Terminal in the folder and run:
   ```bash
   chmod +x Start_App.command && ./Start_App.command
   ```
2. Docker loads the image and opens `http://localhost:8501` in your browser.

### Usage

1. Choose a data source in the sidebar (**CSV Upload** or **PostgreSQL Connection**).
2. Select the text column to analyze.
3. Click **Run NLP Analysis**.
4. View sentiment distribution, discovered topics, and the detailed results table.
5. Download results as CSV.

## Build from Source (Developer)

### Requirements

- Python 3.10+
- Docker Desktop
- 8GB+ RAM (for model downloads)

### Step 1: Clone & Setup

```bash
git clone https://github.com/roypulseai/feedbackiq.git
cd feedbackiq
```

### Step 2: Obfuscate (protect source code)

```bash
pip install pyarmor
pyarmor gen app.py
```

This creates a `dist/` folder with the encrypted `app.py`.

### Step 3: Build the Docker Image

```bash
docker build -t feedbackiq .
```

The build will download and cache the ML models inside the image.

### Step 4: Export for Distribution

```bash
docker save -o feedbackiq.tar feedbackiq
```

### Step 5: Test Locally

```bash
docker run -p 8501:8501 feedbackiq
```

Open http://localhost:8501

## Project Structure

```
feedbackiq/
├── app.py                 # Main Streamlit application
├── download_models.py     # Model pre-caching script (used during Docker build)
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── Start_App.bat          # Windows launcher
├── Start_App.command      # macOS launcher
├── .gitignore
└── README.md
```

## Technical Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| Data Processing | Pandas, SQLAlchemy, psycopg2 |
| Sentiment Analysis | Hugging Face Transformers (`distilbert-base-multilingual-cased-sentiments-student`) |
| Topic Modeling | BERTopic (multilingual sentence embeddings) |
| Code Protection | PyArmor (obfuscation) |
| Deployment | Docker (offline container) |
| Hardware Target | Intel i3 / 8GB RAM (`batch_size=8`) |

## Limitations

- **HF_TOKEN required for reliable builds** — Hugging Face throttles unauthenticated downloads. Without setting `HF_TOKEN`, model downloads during `docker build` may be slow or fail under heavy traffic. Set it via:
  ```bash
  docker build --build-arg HF_TOKEN=hf_your_token -t feedbackiq .
  ```
  Get your free token at https://huggingface.co/settings/tokens

- **Large image size (4-6 GB)** — ML models are baked into the Docker image. Distribution via `docker save` produces a multi-gigabyte tar file. Ensure sufficient disk and bandwidth.

- **BERTopic needs ~100+ documents** — For smaller datasets, topic modeling may classify most entries as outliers (-1) instead of forming meaningful clusters.

- **Single-word & sarcasm blind spots** — The sentiment model can misclassify very short inputs (e.g., `"Bad"` scored as Positive with low confidence) and struggles with sarcasm, irony, or heavy code-switching.

- **Memory floor** — `batch_size=8` is tuned for 8GB RAM machines, but running both sentiment and topic models simultaneously still pushes that limit. Expect higher RAM usage during analysis.

- **Stateless UI** — Streamlit runs in-memory; results vanish on page refresh. Download the CSV to persist analyzed data.

- **Single-user** — Streamlit serves one process. Not designed for concurrent multi-user access without additional infrastructure.

- **One-time internet needed** — The initial Docker build downloads models from Hugging Face. After the image is built, the application runs fully offline.

## Privacy & Data Protection

FeedbackIQ is designed with a **privacy-first, offline architecture**:

- **Data never leaves your machine** — All processing happens inside the local Docker container. No data is sent to external APIs, cloud services, or third parties.
- **No telemetry or tracking** — The application contains no analytics, telemetry, or phone-home functionality.
- **CSV data stays on disk** — Uploaded CSV files are read into memory and processed locally. They are not persisted, cached, or transmitted anywhere.
- **PostgreSQL credentials** — Database URIs are entered via a password-masked input field and used only for the duration of the session. Credentials are never logged or stored.
- **Optional internet for model download** — The only network activity is during `docker build` when ML models are downloaded from Hugging Face. See `HF_TOKEN` note above. Once the image is built, no network access is required.
- **No user accounts** — The application has no authentication, no user database, and no persistent storage of personal data.
- **Suitable for GDPR/DPA compliance** — Because all data processing is local and no personal data is transmitted or stored by the application, it aligns with data protection requirements where processing must remain under the data controller's control.

> **Note**: Users are responsible for ensuring that any data loaded into FeedbackIQ (via CSV or PostgreSQL) complies with their own data protection obligations, including obtaining necessary consent and anonymizing personal data where appropriate.

## License

MIT
