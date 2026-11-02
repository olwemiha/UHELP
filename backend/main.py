import hashlib
import hmac
import logging
import os
import re
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

# Security Imports
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend import database, models
from backend.seed import seed_all
from openai import OpenAI

FRONTEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(FRONTEND_DIR / ".env")

SESSION_COOKIE = "eduaccess_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14
SESSION_SECRET = os.environ.get("EDUACCESS_SECRET_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_urlsafe(32)
    logging.warning(
        "EDUACCESS_SECRET_KEY is unset; sessions will expire when this process restarts."
    )

# --- PYDANTIC MODELS ---

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise ValueError("Enter your full name.")
        return name

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Enter a valid email address.")
        return email

class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Enter a valid email address.")
        return email

class GoogleAuthRequest(BaseModel):
    token: str = Field(min_length=10)

class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    message: str = Field(min_length=10, max_length=5000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise ValueError("Enter your name.")
        return name

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Enter a valid email address.")
        return email

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if len(message) < 10:
            raise ValueError("Please enter a message with at least 10 characters.")
        return message

class SubjectMark(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    mark: int = Field(ge=0, le=100)

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, value: str) -> str:
        return value.strip()

class APSRequest(BaseModel):
    subjects: list[SubjectMark] = Field(min_length=6, max_length=7)

class EligibilityRequest(BaseModel):
    programme_id: int = Field(gt=0)
    score: int = Field(ge=0, le=1000)
    score_type: Literal["APS", "FPS"]

# --- APP SETUP & LIFESPAN ---

@asynccontextmanager
async def lifespan(_: FastAPI):
    database.initialize_schema()
    with database.SessionLocal() as db:
        seed_all(db)
    yield

app = FastAPI(title="UHELP API", lifespan=lifespan)

# --- SECURITY MIDDLEWARE ---

cors_origins = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "https://uni-helpsa.netlify.app,"
        "http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:8001,http://localhost:8001",
    ).split(",")
    if origin.strip()
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."}))

# --- DATABASE DEPENDENCY ---

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]

# --- AUTH HELPERS ---

def _user_payload(user: models.User) -> dict[str, int | str]:
    return {"id": user.id, "name": user.name, "email": user.email}

def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{password_hash.hex()}"

def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, expected_hex = stored_hash.split(":", maxsplit=1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
    except ValueError:
        return False
    actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(actual, expected)

def _create_session_token(user_id: int) -> str:
    expires_at = int(time.time()) + SESSION_MAX_AGE
    payload = f"{user_id}.{expires_at}"
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}.{signature}"

def _get_session_user_id(token: str | None) -> int | None:
    if not token:
        return None
    try:
        user_id_text, expires_text, signature = token.split(".", maxsplit=2)
        user_id = int(user_id_text)
        expires_at = int(expires_text)
    except (ValueError, TypeError):
        return None

    payload = f"{user_id}.{expires_at}"
    expected_signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    if expires_at < int(time.time()) or not hmac.compare_digest(signature, expected_signature):
        return None
    return user_id

def _session_cookie_options(request: Request) -> tuple[bool, str]:
    origin = request.headers.get("origin", "").rstrip("/")
    is_cross_origin = origin in cors_origins and origin != str(request.base_url).rstrip("/")
    secure = is_cross_origin or os.environ.get("EDUACCESS_COOKIE_SECURE", "").lower() == "true"
    return secure, "none" if is_cross_origin else "lax"


def _set_session_cookie(response: Response, user: models.User, request: Request) -> None:
    secure, samesite = _session_cookie_options(request)
    response.set_cookie(
        SESSION_COOKIE,
        _create_session_token(user.id),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )

def get_current_user(request: Request, db: DbSession) -> models.User:
    user_id = _get_session_user_id(request.cookies.get(SESSION_COOKIE))
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
    user = db.query(models.User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]

# --- PROGRAMME HELPER ---

def _programme_payload(programme: models.Programme) -> dict[str, int | str | None]:
    return {
        "id": programme.id,
        "institution": programme.institution,
        "faculty": programme.faculty,
        "department": programme.department,
        "programme": programme.programme,
        "score_type": programme.score_type,
        "aps_score": programme.aps_score,
        "max_score": programme.max_score,
        "entry_requirement": programme.entry_requirement,
        "notes": programme.notes,
        "source": programme.source,
    }

# --- PUBLIC ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/institutions")
def get_institutions(
    db: DbSession,
    q: Annotated[str, Query(max_length=100)] = "",
):
    query = db.query(models.Institution)
    if q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (models.Institution.name.ilike(search))
            | (models.Institution.short_name.ilike(search))
            | (models.Institution.type.ilike(search))
            | (models.Institution.province.ilike(search))
        )

    institutions = query.order_by(models.Institution.name).all()
    return [
        {
            "id": institution.id,
            "name": institution.name,
            "short_name": institution.short_name,
            "type": institution.type,
            "province": institution.province,
        }
        for institution in institutions
    ]

@app.get("/api/bursaries")
def get_bursaries(
    db: DbSession,
    q: Annotated[str, Query(max_length=100)] = "",
):
    query = db.query(models.Bursary).filter(models.Bursary.is_active.is_(True))
    if q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (models.Bursary.name.ilike(search))
            | (models.Bursary.provider.ilike(search))
            | (models.Bursary.field_of_study.ilike(search))
            | (models.Bursary.description.ilike(search))
        )
    bursaries = (
        query
        .order_by(models.Bursary.closing_date, models.Bursary.name)
        .all()
    )
    return [
        {
            "id": bursary.id,
            "name": bursary.name,
            "provider": bursary.provider,
            "field_of_study": bursary.field_of_study,
            "opening_date": bursary.opening_date,
            "closing_date": bursary.closing_date,
            "description": bursary.description,
            "website": bursary.website,
            "is_active": bursary.is_active,
        }
        for bursary in bursaries
    ]

@app.get("/api/programmes")
def get_programmes(
    db: DbSession,
    q: Annotated[str, Query(max_length=100)] = "",
):
    query = db.query(models.Programme)
    if q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (models.Programme.programme.ilike(search))
            | (models.Programme.institution.ilike(search))
            | (models.Programme.entry_requirement.ilike(search))
            | (models.Programme.faculty.ilike(search))
            | (models.Programme.department.ilike(search))
            | (models.Programme.notes.ilike(search))
        )

    programmes = query.order_by(
        models.Programme.institution,
        models.Programme.programme,
    ).all()
    return [_programme_payload(programme) for programme in programmes]

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: DbSession,
):
    if db.query(models.User).filter_by(email=payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=_hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, user, request)
    return {"user": _user_payload(user)}

@app.post("/api/auth/login")
@limiter.limit("5/minute")
def login_user(request: Request, payload: LoginRequest, response: Response, db: DbSession):
    user = db.query(models.User).filter_by(email=payload.email).first()
    if user is None or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")
    _set_session_cookie(response, user, request)
    return {"user": _user_payload(user)}

@app.post("/api/auth/google")
def google_auth(request: Request, payload: GoogleAuthRequest, response: Response, db: DbSession):
    try:
        # Verify the token with Google
        id_info = id_token.verify_oauth2_token(
            payload.token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token.")

    email = id_info["email"].lower()
    name = id_info.get("name", email.split("@")[0])

    user = db.query(models.User).filter_by(email=email).first()
    if user is None:
        # Create user with a random secure password since they use Google
        user = models.User(
            name=name,
            email=email,
            password_hash=_hash_password(secrets.token_urlsafe(32)),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    _set_session_cookie(response, user, request)
    return {"user": _user_payload(user)}

@app.get("/api/auth/me")
def current_user_profile(user: CurrentUser):
    return {"user": _user_payload(user)}

@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(request: Request, response: Response):
    secure, samesite = _session_cookie_options(request)
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=secure,
        samesite=samesite,
    )

# --- TOOLS & CONTACT ---

@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
def submit_contact_message(payload: ContactRequest, db: DbSession):
    message = models.ContactMessage(
        name=payload.name,
        email=payload.email,
        message=payload.message,
    )
    db.add(message)
    db.commit()
    return {"message": "Your message has been received. We will be in touch."}

@app.post("/api/tools/aps")
def calculate_aps(payload: APSRequest):
    included_subjects = [
        subject for subject in payload.subjects
        if subject.subject.casefold() not in {"life orientation", "lo"}
    ]
    if len(included_subjects) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enter marks for at least six subjects excluding Life Orientation.",
        )

    def points(mark: int) -> int:
        return min(7, max(1, mark // 10 - 1))

    best_six = sorted(included_subjects, key=lambda subject: points(subject.mark), reverse=True)[:6]
    return {
        "aps_score": sum(points(subject.mark) for subject in best_six),
        "subjects_counted": [
            {"subject": subject.subject, "mark": subject.mark, "points": points(subject.mark)}
            for subject in best_six
        ],
        "notice": "Indicative estimate only. Institutions may calculate APS differently and may require specific subjects.",
    }

@app.post("/api/tools/eligibility")
def check_eligibility(payload: EligibilityRequest, db: DbSession):
    programme = db.query(models.Programme).filter_by(id=payload.programme_id).first()
    if programme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found.")
    if (
        programme.score_type not in {"APS", "FPS"}
        or programme.aps_score is None
        or payload.score_type != programme.score_type
    ):
        return {
            "comparable": False,
            "programme": programme.programme,
            "institution": programme.institution,
            "message": "The entered score type cannot be compared with this programme. Review its listed requirements with the institution.",
            "entry_requirement": programme.entry_requirement,
        }

    meets_score = payload.score >= programme.aps_score
    return {
        "comparable": True,
        "eligible_by_score": meets_score,
        "required_score_type": programme.score_type,
        "required_score": programme.aps_score,
        "your_score": payload.score,
        "score_type": programme.score_type,
        "programme": programme.programme,
        "institution": programme.institution,
        "entry_requirement": programme.entry_requirement,
        "message": "Your score meets the listed minimum; this does not guarantee admission."
        if meets_score else "Your score is below the listed minimum. Check alternate pathways with the institution.",
    }

# --- SAVED PROGRAMMES (PROTECTED) ---

@app.get("/api/saved-programmes")
def get_saved_programmes(user: CurrentUser, db: DbSession):
    saved = (
        db.query(models.SavedProgramme)
        .filter_by(user_id=user.id)
        .order_by(models.SavedProgramme.saved_at.desc())
        .all()
    )
    programmes = {
        programme.id: programme
        for programme in db.query(models.Programme).filter(
            models.Programme.id.in_([item.programme_id for item in saved])
        ).all()
    } if saved else {}
    return [_programme_payload(programmes[item.programme_id]) for item in saved if item.programme_id in programmes]

@app.post("/api/saved-programmes/{programme_id}", status_code=status.HTTP_201_CREATED)
def save_programme(programme_id: int, user: CurrentUser, db: DbSession):
    programme = db.query(models.Programme).filter_by(id=programme_id).first()
    if programme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found.")
    saved = db.query(models.SavedProgramme).filter_by(
        user_id=user.id,
        programme_id=programme_id,
    ).first()
    if saved is None:
        db.add(models.SavedProgramme(user_id=user.id, programme_id=programme_id))
        db.commit()
    return {"message": "Programme saved.", "programme": _programme_payload(programme)}

@app.delete("/api/saved-programmes/{programme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_programme(programme_id: int, user: CurrentUser, db: DbSession):
    saved = db.query(models.SavedProgramme).filter_by(
        user_id=user.id,
        programme_id=programme_id,
    ).first()
    if saved is not None:
        db.delete(saved)
        db.commit()

# --- FUNDING SEARCH ---

@app.get("/api/funding")
def find_funding(
    db: DbSession,
    q: Annotated[str, Query(min_length=1, max_length=100)],
):
    search = f"%{q.strip()}%"
    bursaries = (
        db.query(models.Bursary)
        .filter(models.Bursary.is_active.is_(True))
        .filter(
            (models.Bursary.name.ilike(search))
            | (models.Bursary.provider.ilike(search))
            | (models.Bursary.field_of_study.ilike(search))
            | (models.Bursary.description.ilike(search))
        )
        .order_by(models.Bursary.closing_date, models.Bursary.name)
        .all()
    )
    return [
        {
            "id": bursary.id,
            "name": bursary.name,
            "provider": bursary.provider,
            "field_of_study": bursary.field_of_study,
            "opening_date": bursary.opening_date,
            "closing_date": bursary.closing_date,
            "description": bursary.description,
            "website": bursary.website,
        }
        for bursary in bursaries
    ]
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_ai(payload: ChatRequest):
    if openai_client is None:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured.")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", # Fast and cost-effective
            messages=[
                {
                    "role": "system",
                    "content": "You are UHELP, a helpful assistant for South African matriculants. "
                               "You help students understand APS scores, university requirements, TVET colleges, and NSFAS funding. "
                               "Keep your answers brief, encouraging, and focused on education. "
                               "If a user asks something unrelated to education, politely redirect them."
                },
                {"role": "user", "content": payload.message}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return ChatResponse(reply=response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI Error: {e}")
        raise HTTPException(status_code=500, detail="The AI assistant is currently unavailable.")
# --- STATIC FILES (FRONTEND) ---

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")