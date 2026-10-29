# AI Academic Advisor (connected frontend + backend)

## Tech stack
- Frontend: HTML, CSS, JavaScript
- Frontend hosting: GitHub Pages
- Backend: Python, FastAPI, Pydantic, Uvicorn
- Algorithm: transparent rule-based academic risk score and study-plan generator
- Browser-side persistence: localStorage
- Version control: GitHub
- Optional backend deployment: Render

## Important architecture note
GitHub Pages only hosts static frontend files. It does not run a Python API server. Store the frontend and backend in the same GitHub repository, publish the frontend with GitHub Pages, and deploy `backend/` as a web service (for example Render) so the frontend can call it.

## Files
- `index.html`: frontend
- `backend/main.py`: FastAPI backend and algorithm
- `backend/requirements.txt`: Python dependencies
- `render.yaml`: optional Render deployment blueprint

## Setup
1. Create a GitHub repository and upload `index.html`, `render.yaml`, and the `backend` folder.
2. In GitHub repository Settings > Pages, deploy the `main` branch from the root folder.
3. Deploy the repository as a Render Web Service using the included `render.yaml` blueprint, or configure a Python web service with root directory `backend`, build command `pip install -r requirements.txt`, and start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Copy the backend service URL (for example `https://your-service.onrender.com`).
5. Open `index.html` in GitHub and edit `API_BASE_URL` near the bottom. Replace `https://YOUR-BACKEND-NAME.onrender.com` with your real backend URL. Commit the change.
6. Wait for GitHub Pages to redeploy and refresh the site. Test `/health` on your backend URL and `/docs` for interactive API documentation.

## Local test (optional)
From the `backend` folder:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Then open `http://127.0.0.1:8000/docs`. To connect the frontend locally, set `API_BASE_URL` to `http://127.0.0.1:8000`.

## Algorithm note
The risk score is rule-based for a student project demonstration. It is not a trained machine-learning model and should not be treated as a validated prediction.
