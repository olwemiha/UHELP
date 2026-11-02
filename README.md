# UHELP
Your future starts with the right opportunity.
UHelp is an AI-powered educational guide for South African matriculants. It simplifies the journey from school to higher education by bringing universities, TVET colleges, APS calculators, eligibility checks, and funding opportunities into one accessible platform.

It is not just a database — it is a guide that turns a setback into a redirect with its unique Plan B Engine.

 Features
 For Students
Search & Discover: Browse 150+ institutions and 700+ programmes across all 9 provinces.

APS Calculator: Instantly calculate your Admission Point Score based on your Grade 12 marks.

Eligibility Checker: Find out exactly which university programmes you qualify for.

Plan B Engine: Don't meet the APS requirement? UHelp suggests alternative pathways (Extended programmes, TVET, Higher Certificates, or upgrading marks) with time and cost.

Funding Finder: Live search of NSFAS and corporate bursaries, with closing dates and application links.

AI Chatbot: Ask questions in English or isiZulu about APS scores, funding, or study options.

Secure Authentication: Log in securely with Google or email/password.

 For Admins
Secure Login: Role-based access control (Student vs. Admin).

Verified Data: All programme data is sourced from official prospectuses and DHET guidelines.

 Tech Stack
Frontend (The Client)
HTML5 & CSS3: Fully responsive, mobile-first design with a professional, non-template aesthetic.

Vanilla JavaScript (ES6+): No heavy frameworks. Fast, lightweight, and works on low-end devices.

Progressive Web App (PWA) Ready: Can be installed on any phone via the browser.

Security: Uses HttpOnly, SameSite=Lax cookies for session management. Zero sensitive data stored in localStorage.

Backend (The API)
Python 3.10+ & FastAPI: High-performance, asynchronous API framework.

SQLAlchemy & SQLite: Robust Object-Relational Mapping (ORM) and lightweight database.

Pydantic: Strict data validation for all incoming requests.

Security:

Hashing: scrypt with salt for password storage (industry standard).

Session Tokens: HMAC-SHA256 signed tokens to prevent tampering.

Rate Limiting: slowapi prevents brute-force attacks on the login endpoint.

CORS: Locked down to only allow requests from the authorized frontend.

AI Integration: OpenAI API (gpt-4o-mini) for the intelligent chatbot.
UHELP/
│
├── index.html                  # Homepage
├── about.html                  # About UHelp
├── programmes.html             # Programme Directory
├── institutions.html           # Institution Directory
├── bursaries.html              # Funding Opportunities
├── contact.html                # Contact Form
├── dashboard.html              # User Dashboard (Protected)
│
├── css/
│   └── styles.css              # Global styles
│
├── js/
│   └── main.js                 # Global scripts (menu, language toggle)
│
├── auth/
│   ├── login.html              # Login Page (Google + Email)
│   └── signup.html             # Signup Page
│
├── services/
│   ├── aps-calculator.html     # APS Calculator Tool
│   ├── eligibility.html        # Eligibility Checker Tool
│   └── funding-finder.html     # Bursary Search Tool
│
├── backend/
│   ├── main.py                 # FastAPI application & routes
│   ├── models.py               # Database models
│   ├── database.py             # DB connection setup
│   ├── seed.py                 # Database seeding script
│   └── seed_data/
│       ├── university_data.py  # University programme data
│       └── tvet_data.py        # TVET & Private college data
│
├── .env                        # Environment variables (Ignored by Git)
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
└── README.md                   


 Getting Started (Local Development)
Prerequisites
Python 3.10+

VS Code with the Live Server extension.

An OpenAI API Key (for the chatbot).

1. Clone the Repository
bash
git clone https://github.com/your-username/uhelp.git
cd uhelp
2. Set Up the Backend
Create a virtual environment and install the required packages:

bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Configure Environment Variables
Create a file called .env in the root folder and add your keys:


4. Seed the Database
Run the seeding script to populate the SQLite database with all 700+ programmes and institutions:

bash
python backend/seed.py
5. Start the Backend Server
bash
uvicorn backend.main:app --reload
The API will be running at http://127.0.0.1:8000. You can view the interactive API docs at http://127.0.0.1:8000/docs.

6. Start the Frontend
Open the UHELP folder in VS Code.

Right-click on index.html and select "Open with Live Server".

The website will open at http://127.0.0.1:5500.

 Security Notes
Passwords are never stored in plain text. We use scrypt with a unique salt for every user.

Session cookies are HttpOnly and SameSite=Lax, meaning JavaScript cannot access them, and they are protected against CSRF attacks.

The .env file is in .gitignore, so API keys are never pushed to version control.

Rate limiting is applied to the login endpoint to stop brute-force attacks.

The Plan B Engine
Most platforms stop at "You are not eligible." UHelp is different.

If a learner doesn't meet the APS requirement for their dream course, our engine:

Identifies the gap (e.g., "You are 3 APS points short").

Searches a pathway graph of alternative qualifications (Extended degrees, TVET N4-N6, Higher Certificates).

Ranks these alternatives by time and cost.

Recommends the best route forward.

This turns a rejection into a redirection — the core promise of UHelp.

📄License
This project was built for the  Hackathon 2026. It is free for learners, always.

 Acknowledgements
Data sourced from DHET, university prospectuses, and official bursary providers.

Built with for South African matriculants.

