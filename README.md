# ATS Resume Scorer

ATS Resume Scorer is an AI-powered resume analysis app that scores a resume against ATS-friendly criteria and a target job description. It combines a FastAPI backend with a Streamlit frontend to extract resume content, compare skills, generate feedback, and show clear improvement suggestions.

## Demo Video

<video src="./media/ATS%20Resume%20Scorer.mp4" controls width="100%">
  Your browser does not support the video tag.
</video>

## Features

- Resume upload and parsing.
- ATS score generation.
- Job description matching.
- Skill validation and gap analysis.
- Strengths, issues, and detailed improvement feedback.
- Actionable recommendations for resume optimization.
- Analysis history with Supabase-backed authentication.
- PDF report generation.

## Tech Stack

- Python
- FastAPI
- Streamlit
- Supabase
- spaCy
- Sentence Transformers
- Groq API
- Jupyter Notebook

## Project Structure

```text
backend/
  api/              API routes and authentication helpers
  core/             App configuration
  database/         Supabase database integration
  models/           Request and response schemas
  services/         Resume scoring, parsing, feedback, reports, and matching logic
  templates/        HTML templates for report sections
  utils/            File and matching utilities

frontend/
  assets/           Styling assets
  components/       Streamlit UI components
  services/         Frontend API and Supabase clients
  views/            App pages
  streamlit_app.py  Streamlit entry point

jupyter notebooks/  Data preparation, embeddings, and BERT fine-tuning notebooks
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/anshu-raj29/ats-resume-scorer.git
cd ats-resume-scorer
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add the required API keys and Supabase configuration.

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Run Locally

Start the backend API:

```bash
uvicorn backend.main:app --reload
```

Start the Streamlit frontend in another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

The backend runs at `http://localhost:8000`, and the frontend opens in Streamlit.

## API Endpoints

- `POST /api/v1/analyze-resume` - Analyze a resume.
- `GET /api/v1/history` - Get user analysis history.
- `DELETE /api/v1/history/:id` - Delete a history entry.
- `GET /api/v1/health` - Check API health.
- `POST /api/v1/generate-pdf` - Generate a PDF report.

## Notes

- Keep `.env` and `frontend/.streamlit/secrets.toml` private.
- The backend loads NLP and embedding models on startup, so the first run can take a little longer.
- The notebooks are included for data exploration, embeddings, and model fine-tuning work.
