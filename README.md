# **Smart Resume Screener**



A full-stack resume screening application that helps evaluate candidate resumes against job descriptions, extract structured candidate information, calculate explainable match scores, rank candidates, and manage shortlists.



#### **Overview:**



* Smart Resume Screener provides a simple workflow for a recruiter or hiring team:
* 
* Create a job posting with required and preferred skills.
* 
* Upload one or multiple candidate resumes in PDF or TXT format.
* 
* Extract candidate information such as name, email, skills, education, and experience.
* 
* Screen candidates against a selected job.
* 
* View match scores, fit levels, matched/missing skills, strengths, weaknesses, and justification.
* 
* Compare candidates through a ranked leaderboard.
* 
* Shortlist or remove candidates from the shortlist.
* 
* The application consists of a React/Vite frontend and a FastAPI backend backed by SQLite.









#### Key Features





* Job posting creation, listing, updating, and deletion
* 
* Single and batch resume upload
* 
* PDF and TXT resume parsing
* 
* Candidate information and skill extraction
* 
* Explainable resume-to-job evaluation
* 
* Candidate match score and fit level
* 
* Matched and missing skill analysis
* 
* Candidate strengths and weaknesses
* 
* Ranked candidate leaderboard
* 
* Minimum-score and shortlisted-only filtering
* 
* Candidate detail report
* 
* Shortlist management
* 
* Backend health and database connectivity check
* 
* REST API documentation through FastAPI Swagger UI and ReDoc
* 
* Backend tests covering parsing, CRUD workflows, screening, ranking, and shortlisting
* 
* Technology Stack
* 
* Frontend
* 
* React
* 
* Vite
* 
* JavaScript
* 
* Lucide React
* 
* Oxlint
* 
* Backend
* 
* Python
* 
* FastAPI
* 
* Uvicorn
* 
* SQLAlchemy
* 
* Pydantic / Pydantic Settings
* 
* pypdf
* 
* python-multipart
* 
* Database
* 
* SQLite





#### Project Structure





smart-resume-screener/

├── backend/

│   ├── app/

│   │   ├── api/

│   │   ├── core/

│   │   ├── models/

│   │   ├── schemas/

│   │   ├── services/

│   │   └── main.py

│   ├── tests/

│   ├── .env.example

│   └── requirements.txt

│

├── frontend/

│   ├── public/

│   ├── src/

│   │   ├── assets/

│   │   ├── components/

│   │   ├── services/

│   │   ├── App.jsx

│   │   ├── App.css

│   │   ├── index.css

│   │   └── main.jsx

│   ├── package.json

│   ├── package-lock.json

│   └── vite.config.js

│

└── .gitignore



#### Prerequisites





#### Make sure the following are installed:





Python 3.10+



Node.js and npm



Git



Backend Setup



Open a terminal in the project directory.



#### 1\. Create and activate a virtual environment



Windows PowerShell:



cd backend

python -m venv venv

.
env\\Scripts\\Activate.ps1



macOS/Linux:



cd backend

python3 -m venv venv

source venv/bin/activate



#### 2\. Install backend dependencies



pip install -r requirements.txt







#### 3\. Configure the backend port



The frontend Vite proxy is configured to forward /api requests to backend port 8001.



Create backend/.env if you need to override the backend defaults:



PORT=8001



The repository intentionally does not include a real .env file. Use backend/.env.example as the configuration placeholder and keep secrets out of Git.





#### 4\. Start the backend



From the backend directory:



uvicorn app.main:app --reload --port 8001



The backend will be available at:



http://127.0.0.1:8001



Useful endpoints:



http://127.0.0.1:8001/

http://127.0.0.1:8001/api/health

http://127.0.0.1:8001/docs

http://127.0.0.1:8001/redoc



Frontend Setup



Open a second terminal in the project root.



#### 1\. Install dependencies



cd frontend

npm install







#### 2\. Start the frontend



npm run dev



Vite will normally serve the application at:



http://localhost:5173



The frontend uses the /api path and the Vite proxy in frontend/vite.config.js to communicate with the backend on port 8001.



Running the Application



Start both services:



Terminal 1 — Backend



cd backend

uvicorn app.main:app --reload --port 8001



Terminal 2 — Frontend



cd frontend

npm run dev



Then open the frontend URL shown by Vite, normally:



http://localhost:5173



Resume Screening Workflow







#### 1\. Create a Job



Create a job posting with:



Job title



Department



Job description



Required skills



Preferred skills



Minimum experience







#### 2\. Upload Resumes



Upload candidate resumes in:



PDF



TXT



Single and batch upload are supported.





#### 3\. Screen Candidates



Select a job and screen one candidate or run batch screening.



The evaluation provides:



Match score



Fit level



Matched skills



Missing skills



Strengths



Weaknesses



Explanation/justification





#### 4\. Review Rankings



Candidates are ranked by match score so the strongest matches appear first.



The leaderboard also supports:



Minimum score filtering



Shortlisted-only filtering



Candidate detail viewing



Shortlist status updates



API Overview



The FastAPI backend exposes the following main API groups:



Area



Base Path



Purpose



Health



/api/health



Application and database health



Jobs



/api/jobs



Create and manage job postings



Resumes



/api/resumes



Upload and manage resumes



Screening



/api/screen



Screen, rank, and shortlist candidates



Full interactive API documentation is available through:



/docs — Swagger UI



/redoc — ReDoc







#### Testing



The repository includes backend tests covering:



Resume parsing and file validation



Skill, education, and experience extraction



Rule-based evaluation



Health/database connectivity



Job CRUD operations



Resume upload and candidate linking



End-to-end screening



Candidate ranking



Shortlisting



The test files are located in:



backend/tests/



Important Project Configuration



The frontend proxy is configured in:



frontend/vite.config.js



and points API requests to:



http://127.0.0.1:8001



Keep the backend running on port 8001 when using the current frontend configuration.



Security and Repository Hygiene



The repository intentionally excludes local/generated files such as:



venv/



node\_modules/



.env



SQLite database files



dist/



.vscode/



.idea/



Do not commit API keys, passwords, tokens, or other secrets.







#### Future Improvements



Potential future enhancements include:



Authentication and role-based access



Persistent user accounts



More advanced semantic matching



Additional resume formats



Recruiter analytics and reporting



Exportable screening reports



Production database support







#### License



No license is currently specified for this project.

