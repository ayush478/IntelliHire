# 🎯 IntelliHire - Complete Technical Interview Preparation Guide

> **An AI-powered recruitment platform that automates resume screening by parsing job descriptions, analyzing resumes, and scoring candidates using multi-factor algorithms.**

---

## 📋 Table of Contents

1. [Project Overview](#-1-project-overview)
2. [High-Level Architecture](#-2-high-level-architecture)
3. [Tech Stack & Why It Was Chosen](#-3-tech-stack--why-it-was-chosen)
4. [Core Features](#-4-core-features)
5. [Backend Deep Dive](#-5-backend-deep-dive)
6. [Database Design](#-6-database-design)
7. [System Design Concepts](#-7-system-design-concepts)
8. [Edge Cases & Failures](#-8-edge-cases--failures)
9. [Performance Optimizations](#-9-performance-optimizations)
10. [Real Interview Q&A](#-10-real-interview-qa)
11. [One-Minute & Five-Minute Explanation](#-11-one-minute--five-minute-explanation)
12. [Core Concepts Deep Dive](#-12-core-concepts-deep-dive)
13. [Technology Fundamentals for Beginners](#-13-technology-fundamentals-for-beginners)

---

## 🔍 1. Project Overview

### What Problem Does This Project Solve?

**The Traditional Hiring Problem:**
Imagine you're an HR manager at a growing tech company. You post a job listing for a "Senior Machine Learning Engineer" and receive **500+ resumes** in a week. 

- 📧 Reading each resume: ~3 minutes
- ⏰ Total time: **25+ hours** just for initial screening
- 🎯 Human bias can affect decisions
- 😓 Fatigue leads to overlooking good candidates

**IntelliHire solves this by:**
1. **Automatically parsing** job descriptions from any URL (LinkedIn, Indeed, company sites)
2. **Extracting structured data** from resumes (PDF, DOCX) using AI
3. **Scoring candidates** based on multiple factors (experience, skills, career trajectory)
4. **Ranking candidates** so recruiters see the best matches first

### Who Are The Users?

| User Type | How They Use It | Key Benefit |
|-----------|----------------|-------------|
| **HR Recruiters** | Upload resumes, get ranked candidates | Saves 80%+ screening time |
| **Hiring Managers** | Review top candidates with score explanations | Better quality hires |
| **Staffing Agencies** | Process high-volume applications | Scale without hiring more staff |
| **Startups** | Small teams can handle enterprise-level hiring | Competitive advantage |

### Why Was This Project Needed?

```
Before IntelliHire:
┌──────────────────────────────────────────────────────┐
│  500 Resumes → Manual Review → 25+ hours → Decisions │
└──────────────────────────────────────────────────────┘

After IntelliHire:
┌──────────────────────────────────────────────────────────────┐
│  500 Resumes → AI Processing (5 min) → Ranked List → Focus  │
│                                         on Top 20 Candidates │
└──────────────────────────────────────────────────────────────┘
```

**Key Drivers:**
- ⏱️ **Time Efficiency**: Reduce screening from hours to minutes
- 🎯 **Consistency**: Same criteria applied to every candidate
- 📊 **Transparency**: Explainable scores (not just "good" or "bad")
- 🤖 **AI Detection**: Identify AI-generated resumes that lack authenticity

---

## 🏗️ 2. High-Level Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────────────────┐│
│  │  JD Input  │ │  Resume    │ │  Weight    │ │   Results Dashboard        ││
│  │   (URL)    │ │  Upload    │ │  Sliders   │ │ (Charts + Ranked Cards)    ││
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └────────────┬───────────────┘│
└────────┼──────────────┼──────────────┼─────────────────────┼────────────────┘
         │ HTTP POST    │ FormData     │ Weights JSON        │ Results JSON
         ▼              ▼              ▼                     ▲
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND (FastAPI)                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ /job-descriptions│  │ /resumes/upload  │  │    /scores/batch-score   │  │
│  │   - Fetch URL    │  │   - Parse Files  │  │    - Calculate Scores    │  │
│  │   - Parse with AI │  │   - Store DB    │  │    - AI Detection        │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬─────────────┘  │
│           │                     │                         │                 │
│           ▼                     ▼                         ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Google Vertex AI (Gemini)                        │  │
│  │   - JD Parsing Prompt    - Resume Parsing Prompt    - AI Detection   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MongoDB Database                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐    │
│  │ job_descriptions│  │    resumes     │  │         scores             │    │
│  │  - url          │  │  - file_hash   │  │  - resume_id, jd_id        │    │
│  │  - parsed_data  │  │  - parsed_data │  │  - overall_score           │    │
│  │  - content      │  │  - content     │  │  - weights_hash (caching)  │    │
│  └────────────────┘  └────────────────┘  └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: From UI → API → DB → Response

Let's trace what happens when a user clicks "Process Candidates":

```
Step 1: User Action
┌──────────────────────────────────────────────┐
│  User enters JD URL + uploads 5 resumes      │
│  Clicks "⚡ Process Candidates"              │
└──────────────────────────┬───────────────────┘
                           ▼
Step 2: Analyze Job Description
┌──────────────────────────────────────────────┐
│  POST /api/v1/job-descriptions               │
│  Body: { "url": "https://linkedin.com/..." } │
│                                              │
│  Backend:                                    │
│  1. Fetch HTML from URL (requests library)   │
│  2. Parse HTML → extract text (BeautifulSoup)│
│  3. Send to Gemini AI with JD_PROMPT         │
│  4. Get structured JSON (title, skills, etc.)│
│  5. Store in MongoDB → return jd._id         │
└──────────────────────────┬───────────────────┘
                           ▼
Step 3: Upload & Parse Resumes
┌──────────────────────────────────────────────┐
│  POST /api/v1/resumes/upload/batch           │
│  Body: FormData with 5 files                 │
│                                              │
│  Backend (for each file):                    │
│  1. Calculate SHA256 hash (deduplication)    │
│  2. Check if hash exists → return cached     │
│  3. Decode file content (UTF-8)              │
│  4. Send to Gemini AI with RESUME_PROMPT     │
│  5. Get structured JSON (name, skills, etc.) │
│  6. Store in MongoDB → return resume._id     │
└──────────────────────────┬───────────────────┘
                           ▼
Step 4: Score Candidates
┌──────────────────────────────────────────────┐
│  POST /api/v1/scores/batch-score             │
│  Body: {                                     │
│    "jd_id": "abc123",                        │
│    "resume_ids": ["r1", "r2", ...],          │
│    "weights": {                              │
│      "experience": 0.5,                      │
│      "skills": 0.35,                         │
│      "trajectory": 0.15                      │
│    }                                         │
│  }                                           │
│                                              │
│  Backend:                                    │
│  1. Create weights_hash for caching          │
│  2. For each resume:                         │
│     a. Check cache (same jd + weights)       │
│     b. If cached → return cached score       │
│     c. If new → calculate:                   │
│        - Experience similarity (fuzzy match) │
│        - Skills overlap (fuzzy matching)     │
│        - Trajectory alignment (seniority)    │
│        - AI detection (Gemini prompt)        │
│     d. Combine: weighted average × 100       │
│     e. Store in MongoDB for future cache     │
│  3. Sort by score DESC → return results      │
└──────────────────────────┬───────────────────┘
                           ▼
Step 5: Display Results
┌──────────────────────────────────────────────┐
│  Frontend receives JSON array:               │
│  [                                           │
│    { "score": 85, "parsed": {...}, ... },    │
│    { "score": 72, "parsed": {...}, ... }     │
│  ]                                           │
│                                              │
│  React:                                      │
│  1. setResults(data) → triggers re-render    │
│  2. AreaChart shows visual comparison        │
│  3. Candidate cards with progress bars       │
│  4. "Download Report" generates PDF          │
└──────────────────────────────────────────────┘
```

---

## 🛠️ 3. Tech Stack & Why It Was Chosen

### Backend Technologies

| Technology | What It Does | Why This Choice | Alternatives Considered |
|------------|--------------|-----------------|-------------------------|
| **Python** | Core programming language | AI/ML ecosystem, FastAPI compatibility | Node.js (less AI libraries), Go (less rapid prototyping) |
| **FastAPI** | Web framework for APIs | Async support, automatic OpenAPI docs, type hints | Flask (no async), Django (overkill for API-only) |
| **Uvicorn** | ASGI server | Async performance, works with FastAPI | Gunicorn (WSGI only), Hypercorn |
| **Motor** | Async MongoDB driver | Non-blocking DB operations | PyMongo (sync, blocks event loop) |
| **Pydantic** | Data validation | Automatic serialization, type safety | Marshmallow, dataclasses (less features) |

### Frontend Technologies

| Technology | What It Does | Why This Choice | Alternatives Considered |
|------------|--------------|-----------------|-------------------------|
| **React 19** | UI library | Component-based, large ecosystem | Vue (smaller ecosystem), Svelte (less tooling) |
| **Next.js 15** | React framework | SSR/SSG, file-based routing, Turbopack | Create React App (outdated), Vite (less features) |
| **TypeScript** | Type-safe JavaScript | Catch errors at compile time, better refactoring | JavaScript (no type safety) |
| **Tailwind CSS** | Utility-first styling | Rapid prototyping, consistent design | CSS Modules, styled-components |
| **Recharts** | Data visualization | React-native, easy to customize | Chart.js (more setup), D3 (steep learning curve) |
| **jsPDF + autoTable** | PDF generation | Client-side generation, no server load | Server-side PDF (adds complexity) |

### Database

| Technology | What It Does | Why This Choice | Alternatives Considered |
|------------|--------------|-----------------|-------------------------|
| **MongoDB** | Document database | Flexible schema for parsed data | PostgreSQL (rigid schema), DynamoDB (vendor lock-in) |

**Why MongoDB was perfect for this use case:**
```javascript
// Resume data can have varying structures:
{
  "name": "John Doe",
  "skills": ["python", "react", "aws"], // Array of varying length
  "experience_bullets": [...], // Dynamic list
  "parsed_data": { ... } // AI output varies
}

// In SQL, you'd need:
// - candidates table
// - skills table (many-to-many)
// - experience_bullets table
// - JOIN operations for every query

// In MongoDB: One document, one query!
```

### AI & ML

| Technology | What It Does | Why This Choice |
|------------|--------------|-----------------|
| **Google Vertex AI (Gemini 2.0 Flash)** | LLM for parsing | Fast, structured JSON output, reliable |
| **rapidfuzz** | Fuzzy string matching | Fast C implementation, handles typos |
| **scikit-learn** | Cosine similarity | Industry standard, vectorized operations |

---

## ⚡ 4. Core Features

### Feature 1: AI-Powered Job Description Parsing

**Input:** A URL like `https://linkedin.com/jobs/view/12345`

**Processing:**
```python
# 1. Fetch the webpage
response = requests.get(url, headers={'User-Agent': '...'})

# 2. Extract text from HTML
soup = BeautifulSoup(response.text, 'html.parser')
for script in soup(["script", "style"]):
    script.extract()  # Remove non-content elements
text = soup.get_text()

# 3. Send to Gemini with this prompt:
JD_PROMPT = """
You are an expert HR analyst. Return STRICT JSON:
{
  "title": "Senior ML Engineer",
  "seniority": "senior",
  "required_skills": ["python", "tensorflow", "kubernetes"],
  "responsibilities": ["Lead ML projects", "Mentor team"],
  ...
}
"""
```

**Output:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "title": "Senior Machine Learning Engineer",
  "seniority": "senior",
  "required_skills": ["python", "tensorflow", "pytorch", "kubernetes", "aws"],
  "nice_to_have_skills": ["spark", "mlflow"],
  "responsibilities": [
    "Design and implement ML pipelines",
    "Lead a team of 3-5 engineers"
  ]
}
```

**Real-World Example:**
> "I paste a LinkedIn job URL. The system automatically extracts that it's a Senior-level role requiring Python, TensorFlow, and 5+ years experience. No manual data entry needed!"

---

### Feature 2: Batch Resume Processing

**Input:** Multiple PDF/DOCX files uploaded via drag-and-drop

**Processing:**
```python
# For each resume file:
for file in uploaded_files:
    # 1. Calculate unique hash (for deduplication)
    file_hash = hashlib.sha256(content).hexdigest()
    
    # 2. Check if we've seen this resume before
    existing = await collection.find_one({"file_hash": file_hash})
    if existing:
        return existing  # Skip re-processing!
    
    # 3. Parse with Gemini
    parsed_data = parse_resume_with_gemini(resume_text)
```

**Output (per resume):**
```json
{
  "name": "Jane Smith",
  "titles": ["software engineer", "ml engineer"],
  "seniority": "senior",
  "skills": ["python", "react", "aws", "tensorflow", "sql"],
  "experience_bullets": [
    "Built recommendation system serving 10M users",
    "Led migration to Kubernetes, reducing costs 40%"
  ],
  "education": ["M.S. Computer Science, Stanford"]
}
```

---

### Feature 3: Multi-Factor Scoring Algorithm

This is the **brain** of IntelliHire. Let's break it down:

```
Final Score = (Experience × W_exp) + (Skills × W_skills) + (Trajectory × W_traj)
              ─────────────────────────────────────────────────────────────────
                                    Normalized to 0-100
```

#### Factor 1: Experience Similarity (Default: 50% weight)

**Analogy:** Like comparing two job descriptions side-by-side and highlighting overlapping keywords.

**How it works:**
```python
def exp_similarity(jd_text, resume_text):
    # Uses fuzzy matching (like spell-check)
    token_set_ratio = fuzz.token_set_ratio(jd_text, resume_text)  # 0-100
    partial_ratio = fuzz.partial_ratio(jd_text, resume_text)  # 0-100
    
    avg = (token_set_ratio + partial_ratio) / 2
    
    # Apply square root scaling (boosts mid-range scores)
    # 50% match → 70% score (more forgiving)
    scaled = (avg / 100.0) ** 0.5
    
    return max(0.15, scaled)  # Floor of 15% for any resume
```

**Example:**
```
JD: "Build microservices in Go on Kubernetes"
Resume: "Developed Go microservices deployed on K8s clusters"

token_set_ratio = 85 (recognizes "Kubernetes" ≈ "K8s")
partial_ratio = 78
Average = 81.5
Scaled = 0.90 (90% experience match!)
```

---

#### Factor 2: Skills Overlap (Default: 35% weight)

**Analogy:** Like a Venn diagram showing common skills.

```python
def skills_overlap_score(jd_skills, resume_skills):
    """
    For each JD skill, find the BEST match in resume skills.
    Handles variations like "Python" vs "Python3" gracefully.
    """
    total = 0.0
    for jd_skill in jd_skills:
        best_match = 0.0
        for resume_skill in resume_skills:
            # Compare with fuzzy matching
            ratio = fuzz.ratio(jd_skill, resume_skill) / 100.0
            partial = fuzz.partial_ratio(jd_skill, resume_skill) / 100.0
            best_match = max(best_match, ratio, partial)
        total += best_match
    
    return total / len(jd_skills)
```

**Example:**
```
JD requires: ["python", "tensorflow", "aws", "sql"]
Resume has: ["python3", "pytorch", "aws", "mysql", "docker"]

Matching:
- "python" ↔ "python3" = 85%
- "tensorflow" ↔ "pytorch" = 45% (different but related)
- "aws" ↔ "aws" = 100%
- "sql" ↔ "mysql" = 80%

Average = (85 + 45 + 100 + 80) / 4 = 77.5%
```

---

#### Factor 3: Trajectory Alignment (Default: 15% weight)

**Analogy:** Is your career level appropriate for this role?

```python
SENIORITY_MAP = {
    "intern": 0, "junior": 1, "mid": 2, "senior": 3,
    "lead": 4, "manager": 5, "director": 6, "executive": 7
}

def trajectory_alignment(jd_level, resume_level):
    jd_num = SENIORITY_MAP.get(jd_level, 2)
    resume_num = SENIORITY_MAP.get(resume_level, 2)
    diff = abs(jd_num - resume_num)
    
    if diff == 0: return 1.0    # Perfect match
    if diff == 1: return 0.8    # One level off (still good)
    if diff == 2: return 0.5    # Two levels off
    return 0.25                  # More than 2 levels off
```

**Example:**
```
JD requires: "senior" level
Candidate is: "mid" level

diff = |3 - 2| = 1
Score = 0.8 (80%) - still a strong candidate!
```

---

### Feature 4: AI Content Detection

**Why it matters:** Resumes heavily written by ChatGPT may lack genuine experience details.

```python
AI_DETECT_PROMPT = """
Estimate the likelihood that this text was generated by an LLM.
Return JSON:
{
  "ai_likelihood_percent": 35,
  "rationale": "Generic action verbs, templated structure",
  "flags": ["buzzword-heavy", "lack of specifics"]
}
"""

# Penalty calculation (forgiving for moderate AI use)
validity_pct = 100 - int((ai_pct ** 1.2) / (100 ** 0.2))

# Examples:
# 20% AI detected → ~15% penalty → 85% validity
# 50% AI detected → ~42% penalty → 58% validity
# 90% AI detected → ~85% penalty → 15% validity
```

---

### Feature 5: Dynamic Weight Adjustment

Users can **customize** how scores are calculated in real-time:

```typescript
// Frontend sliders (0 to 1)
const [wExp, setWExp] = useState(0.5);   // Experience: 50%
const [wSk, setWSk] = useState(0.35);    // Skills: 35%
const [wTr, setWTr] = useState(0.15);    // Trajectory: 15%

// Normalize so weights always sum to 100%
const weights = useMemo(() => {
    const s = Math.max(0.0001, wExp + wSk + wTr);
    return {
        experience: wExp / s,
        skills: wSk / s,
        trajectory: wTr / s,
    };
}, [wExp, wSk, wTr]);
```

**Use Case:**
> "For a junior role, I care more about skills (potential) than experience. I slide Skills to 60% and Experience to 25%."

---

## 🔧 5. Backend Deep Dive

### API Structure

```
backend/app/
├── main.py              # FastAPI app entry point
├── core/
│   └── config.py        # Settings (MongoDB URL, Google Cloud config)
├── models/
│   └── base.py          # Pydantic models (Resume, JobDescription, Score)
├── db/
│   └── mongodb.py       # Motor async driver, connection management
└── api/
    └── api_v1/
        ├── api.py       # Router aggregation
        └── endpoints/
            ├── job_descriptions.py  # JD parsing endpoint
            ├── resumes.py           # Resume upload endpoint
            └── scores.py            # Scoring algorithm
```

### Controllers, Services, Repositories Pattern

**Note:** This project uses a **simplified architecture** suitable for its size:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Traditional Pattern                         │
│  Controller → Service → Repository → Database                       │
│  (routing)    (logic)   (data access)                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         IntelliHire Pattern                         │
│  Router/Endpoint → Direct MongoDB Access                            │
│  (routing + logic combined for simplicity)                          │
└─────────────────────────────────────────────────────────────────────┘
```

**Why this choice:**
- Small team, rapid development
- Feature-focused files (each endpoint file handles one domain)
- Easy to understand and modify
- Can refactor to services layer if complexity grows

### Authentication & Authorization Flow

**Current State:** No authentication (development/demo mode)

**Production-Ready Pattern (if you were to add it):**
```python
# In config.py, there's already:
SECRET_KEY: str = os.getenv("SECRET_KEY", "...")
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

# You would add:
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode JWT, validate, return user
    pass

@router.post("/batch-score")
async def batch_score(
    ...,
    user = Depends(get_current_user)  # Require auth
):
    pass
```

### Business Logic Handling

**Example: Batch Score Endpoint**

```python
@router.post("/batch-score", response_model=List[dict])
async def batch_score_resumes(
    jd_id: str = Body(...),
    resume_ids: List[str] = Body(...),
    weights: Optional[Dict[str, float]] = Body(None),
    db: MongoDB = Depends(get_db)
):
    # 1. VALIDATION
    jd = await jd_collection.find_one({"_id": ObjectId(jd_id)})
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # 2. CACHING STRATEGY
    w_sig = weights_signature(weights)  # Hash of weights for cache key
    
    # 3. PROCESSING LOOP
    rows = []
    for resume_id in resume_ids:
        # Check cache first
        existing = await scores_collection.find_one({
            "resume_id": resume_id,
            "jd_id": jd_id,
            "weights_hash": w_sig,  # Same weights = same score
        })
        if existing:
            rows.append(existing)  # Cache hit!
            continue
        
        # Calculate fresh score
        exp_sim = exp_similarity(jd_text, resume_text)
        skill_overlap = skills_overlap_score(jd_skills, resume_skills)
        traj = trajectory_alignment(jd_level, resume_level)
        score = candidate_score(exp_sim, skill_overlap, traj, weights)
        
        # Store for future cache hits
        await scores_collection.insert_one(db_doc)
        rows.append(db_doc)
    
    # 4. SORT & RETURN
    rows.sort(key=lambda r: r.get("score", 0.0), reverse=True)
    return rows
```

### Validation and Error Handling

**Input Validation with Pydantic:**
```python
class Resume(BaseDocument):
    file_hash: str                          # Required
    file_name: str                          # Required
    file_size: int                          # Required, must be integer
    file_type: str                          # Required
    content: Dict[str, Any]                 # Required
    parsed_data: Optional[Dict[str, Any]]   # Optional
```

**Error Handling Examples:**
```python
# Invalid ID format
try:
    object_id = ObjectId(jd_id)
except Exception:
    raise HTTPException(
        status_code=400, 
        detail="Invalid job description ID format"
    )

# Resource not found
if not jd:
    raise HTTPException(
        status_code=404, 
        detail="Job description not found"
    )

# External API failure
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except Exception as e:
    raise HTTPException(
        status_code=400, 
        detail=f"Failed to fetch job description: {str(e)}"
    )
```

---

## 🗃️ 6. Database Design

### Collections Overview

```
MongoDB: talent_intel_db
│
├── job_descriptions
│   ├── _id: ObjectId
│   ├── url: String
│   ├── url_hash: String (SHA256 for deduplication)
│   ├── content: String (raw text)
│   ├── parsed_data: Object (AI-extracted structure)
│   ├── created_at: DateTime
│   └── updated_at: DateTime
│
├── resumes
│   ├── _id: ObjectId
│   ├── file_hash: String (SHA256 of file content)
│   ├── file_name: String
│   ├── file_size: Integer
│   ├── file_type: String
│   ├── content: Object { text: String }
│   ├── parsed_data: Object (AI-extracted structure)
│   ├── created_at: DateTime
│   └── updated_at: DateTime
│
└── scores
    ├── _id: ObjectId
    ├── resume_id: String (reference)
    ├── jd_id: String (reference)
    ├── overall_score: Float (0-100)
    ├── score_breakdown: Object
    ├── weights: Object { experience, skills, trajectory }
    ├── weights_hash: String (for caching)
    ├── ai: Object (AI detection results)
    ├── ai_pct: Integer (0-100)
    ├── validity_pct: Integer (0-100)
    ├── exp_sim: Float
    ├── skill_overlap: Float
    └── trajectory: Float
```

### Relationships

```
                    ┌─────────────────┐
                    │ job_descriptions │
                    │     (_id)        │
                    └────────┬────────┘
                             │
                 1:N         │         N:1
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────┐                          ┌──────────────┐
│   resumes    │◄──────────N:M───────────►│    scores    │
│    (_id)     │                          │ (resume_id,  │
│              │                          │   jd_id)     │
└──────────────┘                          └──────────────┘
```

**Note:** This is a **document-based** approach, not relational joins:
- `scores.resume_id` and `scores.jd_id` are string references
- No foreign key constraints (application-level integrity)
- Trade-off: Flexibility vs. strict consistency

### Indexing Strategy

**Recommended Indexes:**
```javascript
// job_descriptions
db.job_descriptions.createIndex({ "url_hash": 1 }, { unique: true })
db.job_descriptions.createIndex({ "created_at": -1 })

// resumes
db.resumes.createIndex({ "file_hash": 1 }, { unique: true })

// scores (compound index for cache lookups)
db.scores.createIndex({ 
    "resume_id": 1, 
    "jd_id": 1, 
    "weights_hash": 1 
}, { unique: true })
```

**Why these indexes?**
- `url_hash` and `file_hash`: Fast deduplication checks (O(1) lookup)
- `created_at`: Sort by recent for listing endpoints
- Compound index on scores: Cache lookup is a 3-field query

### Performance Considerations

| Query Pattern | Without Index | With Index |
|---------------|---------------|------------|
| Find by file_hash | O(N) scan | O(1) lookup |
| Score cache check | O(N) scan | O(1) lookup |
| Sort by score | O(N log N) | O(N log N) + faster retrieval |

---

## 🔐 7. System Design Concepts

### Scalability

**Current State:** Single instance, suitable for ~100 concurrent users

**Horizontal Scaling Path:**
```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Backend Pod 1  │ │  Backend Pod 2  │ │  Backend Pod 3  │
│   (FastAPI)     │ │   (FastAPI)     │ │   (FastAPI)     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ MongoDB Cluster │
                    │ (Replica Set)   │
                    └─────────────────┘
```

**Key Points:**
- FastAPI is stateless → easy to scale horizontally
- MongoDB supports replica sets for read scaling
- Gemini API calls are independent (parallel processing)

---

### Caching Strategy

**Level 1: Database-Level Caching**
```python
# Before calculating a score, check if it exists:
existing = await scores_collection.find_one({
    "resume_id": resume_id,
    "jd_id": jd_id,
    "weights_hash": w_sig,  # Same weights = same result
})
if existing:
    return existing  # Skip expensive AI calls!
```

**Level 2: Deduplication (Implicit Caching)**
```python
# Resumes are cached by file hash
file_hash = hashlib.sha256(content).hexdigest()
existing = await collection.find_one({"file_hash": file_hash})
if existing:
    return existing  # Don't re-parse the same resume!
```

**Level 3: Redis (Future Enhancement)**
```python
# For even faster lookups:
import redis
r = redis.Redis()

cache_key = f"score:{jd_id}:{resume_id}:{weights_hash}"
cached = r.get(cache_key)
if cached:
    return json.loads(cached)

# After calculation:
r.setex(cache_key, 3600, json.dumps(result))  # TTL: 1 hour
```

---

### Async Processing

**Current: Synchronous Batch Processing**
```python
# Process all resumes in order (blocking)
for resume_id in resume_ids:
    score = await calculate_score(resume_id, jd_id)
```

**Future: Background Job Queue**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  API receives   │────►│   Redis Queue   │────►│  Worker process │
│  batch request  │     │   (job queue)   │     │  (calculate)    │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         │  Return job_id immediately                    │
         ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│  Client polls   │◄────────────────────────────│  Store results  │
│  /jobs/{job_id} │                             │  in MongoDB     │
└─────────────────┘                             └─────────────────┘
```

**Why this would help:**
- Non-blocking API responses
- Can process 500+ resumes without timeout
- Worker can be scaled independently

---

### Rate Limiting / Security

**Current State:** CORS configured, basic error handling

**Recommended Additions:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/scores/batch-score")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def batch_score_resumes(...):
    pass
```

**Security Checklist:**
| Item | Status | Notes |
|------|--------|-------|
| CORS restrictions | ⚠️ Currently `allow_origins=["*"]` | Restrict in production |
| Rate limiting | ❌ Not implemented | Add SlowAPI or similar |
| Input validation | ✅ Pydantic models | All inputs validated |
| SQL Injection | ✅ N/A | MongoDB, parameterized queries |
| File upload limits | ⚠️ Basic checks | Add file size limits |

---

## ⚠️ 8. Edge Cases & Failures

### What Can Go Wrong?

| Scenario | Current Handling | Improvement |
|----------|------------------|-------------|
| **Invalid URL format** | HTTP 400 with message | ✅ Works well |
| **URL fetch fails (timeout, 404)** | HTTP 400 with error detail | ✅ Works well |
| **Gemini API rate limit** | Exception bubbles up | Add retry with exponential backoff |
| **Gemini returns malformed JSON** | Fallback JSON extraction | ✅ Handles gracefully |
| **Large file upload (100MB PDF)** | May time out | Add file size limit check |
| **Resume in non-UTF8 encoding** | `errors='ignore'` | May lose some characters |
| **MongoDB connection lost** | Exception on next query | Add connection retry logic |

### Error Handling Examples

**Gemini JSON Parsing (Defensive):**
```python
def gemini_json(gemini, system_prompt, text):
    resp = gemini.generate_content([...])
    raw = resp.candidates[0].content.parts[0].text
    raw = raw.strip().strip("` ")  # Remove markdown code blocks
    
    try:
        return json.loads(raw)
    except Exception:
        # Fallback: find JSON object in response
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end+1])
            except Exception:
                pass
    return {}  # Safe default
```

**ObjectId Validation:**
```python
try:
    object_id = ObjectId(jd_id)
except Exception:
    raise HTTPException(
        status_code=400, 
        detail="Invalid job description ID format"
    )
```

---

## 🚀 9. Performance Optimizations

### Query Optimizations

**1. Deduplication with Hash Indexes**
```python
# Instead of: "Have we seen this resume before?"
# Slow: Find all resumes, compare content
# Fast: Hash lookup on indexed field
existing = await collection.find_one({"file_hash": file_hash})
```

**2. Batch Score Caching**
```python
# Cache key includes weights hash
# Same resume + same JD + same weights = same score
weights_hash = hashlib.sha256(
    json.dumps(sorted_weights).encode()
).hexdigest()
```

**3. Early Exit Pattern**
```python
for resume_id in resume_ids:
    # Check cache FIRST (fast)
    if cached_score_exists:
        continue  # Skip expensive AI calls
    
    # Only then do heavy processing
    score = await calculate_with_ai(...)
```

### Caching Strategies Summary

| Layer | What's Cached | TTL | Invalidation |
|-------|---------------|-----|--------------|
| Score cache | Computed scores | Permanent | New processing replaces |
| Resume cache | Parsed resumes | Permanent | File hash based |
| JD cache | Parsed JDs | Permanent | URL hash based |

### API Response Improvements

**1. Minimal Response Payload**
```python
# Return only what frontend needs
return {
    "resume_id": id,
    "score": score,
    "parsed": parsed_data,  # Name, skills for display
    # Don't return: raw content, internal fields
}
```

**2. Sorted Results on Server**
```python
# Sort on server, not client
rows.sort(key=lambda r: r.get("score", 0.0), reverse=True)
return rows
```

---

## 💬 10. Real Interview Q&A

### "Why did you design it this way?"

**Q: Why MongoDB instead of PostgreSQL?**

> "Our data is highly variable. Each resume has different numbers of skills, experiences, and education entries. With MongoDB, I can store this as a single document without complex junction tables. The parsed_data field can have any structure the AI returns, giving us flexibility to improve prompts without schema migrations."

**Q: Why FastAPI instead of Flask or Django?**

> "Three reasons: 
> 1. **Async support** - We make external API calls to Gemini which are I/O bound. Async lets us not block while waiting.
> 2. **Automatic OpenAPI docs** - The /docs endpoint is auto-generated, useful for frontend devs.
> 3. **Type hints** - Pydantic integration catches data issues at the API boundary."

**Q: Why hash-based caching instead of Redis?**

> "For our current scale, database-level caching is sufficient. Adding Redis would introduce operational complexity. If we saw performance issues at scale, Redis would be the natural next step, but premature optimization is the root of all evil."

---

### "How would you scale this?"

**Q: What if you get 10,000 resumes to process?**

> "I'd implement three changes:
> 1. **Background job queue** - Use Celery + Redis. API returns a job_id immediately, client polls for results.
> 2. **Parallel Gemini calls** - Use asyncio.gather() to call Gemini for multiple resumes concurrently.
> 3. **Worker scaling** - Add more Celery workers to increase throughput."

**Q: How would you handle 1000 concurrent users?**

> "The API is already stateless, so I'd:
> 1. Deploy multiple FastAPI containers behind a load balancer (Nginx or K8s Ingress)
> 2. Use MongoDB replica set for read scaling
> 3. Add Redis for session state and caching hot paths
> 4. Implement rate limiting to protect against abuse"

**Q: What if Gemini API costs become too high?**

> "Several strategies:
> 1. **Aggressive caching** - We already cache by file hash, could extend to content-based deduplication.
> 2. **Smaller model** - Gemini Flash is already cost-optimized; could use even smaller models for some tasks.
> 3. **Local models** - For simpler parsing, run local Hugging Face models (but with accuracy trade-offs).
> 4. **Batch API** - Some LLM providers offer batch pricing at 50% discount."

---

### "What would you improve next?"

**Q: What's the biggest technical debt?**

> "The scoring algorithm could be more sophisticated. Currently using fuzzy string matching, but we could:
> 1. Use embedding-based semantic similarity (already have the sklearn import)
> 2. Weight skills by rarity/demand
> 3. Factor in recency of experience (5-year-old Python experience vs. last year)"

**Q: What feature would you add?**

> "An **interview scheduling** integration. Once candidates are ranked, allow recruiters to:
> 1. One-click send interview invites
> 2. Sync with calendar (Google Calendar API)
> 3. Track interview outcomes to improve scoring weights over time (feedback loop)"

**Q: What about security improvements?**

> "Priority list:
> 1. Add authentication (OAuth2/JWT)
> 2. Restrict CORS to known frontend domains
> 3. Implement rate limiting
> 4. Add audit logging (who processed which candidates)
> 5. Encrypt sensitive fields in MongoDB"

---

## 🎤 11. One-Minute & Five-Minute Explanation

### One-Minute Elevator Pitch

> "IntelliHire is an **AI recruitment platform** that automates the most time-consuming part of hiring -- **screening resumes**.
>
> You paste a job description URL, upload candidate resumes, and get a **ranked list** in minutes instead of hours.
>
> The AI extracts skills and experience from both the job posting and resumes, then calculates a **match score** based on three factors: experience similarity, skill overlap, and career trajectory.
>
> What makes it special is the **transparency** -- you can see exactly *why* each candidate scored high or low, and adjust the weights to match what matters most for your role.
>
> It's built with **FastAPI, React, and Google's Gemini AI**, designed to scale from startups to enterprises."

---

### Five-Minute Technical Explanation

> "Let me walk you through IntelliHire's architecture and the key engineering decisions.
>
> **The problem**: HR teams receive hundreds of resumes per job posting. Manual screening takes 3-5 minutes per resume, leading to 20+ hours for a single role. They need consistency, speed, and explainability.
>
> **Architecture Overview**:
> We have a **React/Next.js frontend** for the UI, a **FastAPI backend** for business logic, **MongoDB** for persistence, and **Google Vertex AI (Gemini)** for intelligent parsing.
>
> **The Data Flow**:
> 1. User pastes a job URL -- we fetch the HTML, extract text with BeautifulSoup, and send it to Gemini with a structured prompt. We get back JSON with title, required skills, seniority level, and responsibilities.
>
> 2. User uploads resumes -- we hash each file for deduplication, parse the content, and again use Gemini to extract name, skills, experience bullets, and inferred seniority level.
>
> 3. Scoring happens -- for each resume against the JD, we calculate three metrics:
>    - **Experience similarity**: Using fuzzy string matching (rapidfuzz library) to compare the experience descriptions. We apply square-root scaling to be forgiving of variations.
>    - **Skills overlap**: For each required skill, we find the best fuzzy match in the candidate's skills. This handles variations like 'Python' vs 'Python3' or 'K8s' vs 'Kubernetes'.
>    - **Trajectory alignment**: We map seniority levels to numbers and penalize mismatches. A senior applying for senior gets 100%, senior for mid gets 80%, etc.
>
>    The final score is a weighted average of these three, normalized to 0-100.
>
> **Key Technical Decisions**:
> - **MongoDB over Postgres**: Resume data is highly variable, document storage makes more sense than normalized tables.
> - **Hash-based caching**: We cache parsed resumes by file hash and scores by weights-hash. Same inputs = skip reprocessing.
> - **AI detection**: We run a second Gemini prompt to detect AI-generated resumes, adding a 'validity' penalty.
>
> **Scaling Path**:
> Currently single-instance, but FastAPI is stateless so horizontal scaling is straightforward. For high volume, I'd add a job queue (Celery + Redis) and process resumes as background tasks.
>
> **What I'd improve**:
> Move from string matching to **embedding-based similarity** using sentence transformers. Add **authentication** and **rate limiting** for production. Build a **feedback loop** where hiring outcomes improve the scoring weights over time."

---

## 📚 12. Core Concepts Deep Dive

### FastAPI Fundamentals

**What is FastAPI?**
FastAPI is a modern, high-performance Python web framework for building APIs. Think of it as Flask's younger, faster sibling.

**Key Concepts Used in IntelliHire:**

```python
# 1. Route Definition with Type Hints
@router.post("/batch-score", response_model=List[dict])
async def batch_score_resumes(
    jd_id: str = Body(...),           # Required field from JSON body
    resume_ids: List[str] = Body(...), # List of strings
    weights: Optional[Dict[str, float]] = Body(None),  # Optional with default
    db: MongoDB = Depends(get_db)      # Dependency injection
):
    pass

# 2. Dependency Injection
def get_db() -> MongoDB:
    return MongoDB  # Factory function

# 3. Async/Await for Non-Blocking I/O
async def batch_score_resumes(...):
    # This doesn't block while waiting for DB
    resume = await resumes_collection.find_one({"_id": object_id})
```

**Analogy:** 
Think of FastAPI like a restaurant waiter. Instead of waiting at one table until the kitchen finishes cooking (blocking), they take orders from multiple tables (async). When food is ready, they deliver it (await returns).

---

### React State Management

**How IntelliHire Manages State:**

```typescript
// 1. useState for Local State
const [jdUrl, setJdUrl] = useState("");
const [files, setFiles] = useState<File[]>([]);
const [results, setResults] = useState<Result[]>([]);

// 2. useMemo for Derived State (Expensive Calculations)
const weights = useMemo(() => {
    const sum = wExp + wSk + wTr;
    return {
        experience: wExp / sum,
        skills: wSk / sum,
        trajectory: wTr / sum,
    };
}, [wExp, wSk, wTr]);  // Only recalculate when these change

// 3. State Updates Trigger Re-renders
setResults(scoredData);  // React automatically re-renders components using 'results'
```

**Analogy:**
`useState` is like a sticky note that the component remembers. When you change the note (`setResults`), React automatically updates the screen to match.

`useMemo` is like a calculator with a memory function -- it only recalculates when the inputs change, saving computation.

---

### MongoDB Document Model

**Why Documents Instead of Tables?**

```javascript
// Relational (SQL) approach - 3 tables, many joins
// candidates: id, name
// skills: id, candidate_id, skill_name
// experience: id, candidate_id, description

// Document approach - 1 collection, no joins
{
  "_id": ObjectId("..."),
  "name": "Jane Smith",
  "skills": ["python", "react", "aws"],  // Embedded array
  "experience": [
    { "title": "Engineer", "bullets": [...] }
  ]
}
```

**Motor (Async MongoDB Driver):**
```python
# Synchronous (blocking)
result = collection.find_one({"_id": id})  # Thread waits here

# Async (non-blocking)
result = await collection.find_one({"_id": id})  # Event loop continues
```

---

### Fuzzy String Matching

**What is Fuzzy Matching?**
It's like spell-check for comparing strings. Instead of exact match, it calculates "how similar" two strings are.

```python
from rapidfuzz import fuzz

# Exact match required
"Python" == "python"  # False

# Fuzzy match (case-insensitive similarity)
fuzz.ratio("Python", "python")  # 83 (high match)
fuzz.ratio("Python", "Python3")  # 86 (still good!)
fuzz.ratio("kubernetes", "k8s")  # 30 (low, different words)

# Token set ratio (handles word order)
fuzz.token_set_ratio("machine learning engineer", "ML engineer")  # Higher
```

**Why This Matters:**
Resumes use varied terminology. "Python 3.9" should match "Python". "K8s" should partially match "Kubernetes". Fuzzy matching handles this gracefully.

---

### Cosine Similarity (For Future Enhancement)

**What is it?**
A way to measure similarity between two vectors (lists of numbers). Used in NLP to compare document embeddings.

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# JD embedding (from sentence transformer)
jd_vector = [0.2, 0.8, 0.5, ...]  # 384 dimensions

# Resume embedding
resume_vector = [0.3, 0.7, 0.6, ...]

# Similarity score (0 = completely different, 1 = identical)
similarity = cosine_similarity([jd_vector], [resume_vector])[0][0]
# Returns: 0.95 (very similar!)
```

**Analogy:**
Imagine two arrows pointing in 3D space. Cosine similarity measures the angle between them. Arrows pointing the same direction = similar. Perpendicular arrows = unrelated.

---

### Pydantic Data Validation

**What is Pydantic?**
A Python library that validates data at runtime and provides type safety.

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Resume(BaseModel):
    file_hash: str                          # Must be string
    file_name: str                          
    file_size: int                          # Must be integer
    parsed_data: Optional[Dict[str, Any]]   # Can be None
    
    class Config:
        populate_by_name = True  # Allow both 'id' and '_id'

# Invalid data = automatic error
Resume(file_hash=123, ...)  # ValidationError: file_hash must be string
```

**Why This Matters:**
API security. Invalid data is rejected before it reaches your business logic. No "undefined is not a function" errors.

---

## ✅ Summary Checklist

### Before Your Interview, Make Sure You Can Explain:

- [ ] **Project Overview**: What problem, who uses it, why needed
- [ ] **Data Flow**: UI → API → (Gemini + MongoDB) → Response
- [ ] **Tech Stack**: FastAPI, Next.js, MongoDB, Gemini -- why each was chosen
- [ ] **Scoring Algorithm**: Experience similarity + Skills overlap + Trajectory
- [ ] **Caching Strategy**: Hash-based deduplication and score caching
- [ ] **Error Handling**: How each failure mode is handled
- [ ] **Scaling Plan**: Background jobs, horizontal scaling, Redis caching
- [ ] **Trade-offs**: Document DB vs relational, string matching vs embeddings
- [ ] **Future Improvements**: Auth, rate limiting, feedback loops

### Key Code Files to Review:

| File | Key Concepts |
|------|--------------|
| `backend/app/api/api_v1/endpoints/scores.py` | Scoring algorithm, caching, AI detection |
| `backend/app/api/api_v1/endpoints/job_descriptions.py` | URL fetching, Gemini parsing |
| `backend/app/api/api_v1/endpoints/resumes.py` | Batch upload, deduplication |
| `frontend/app/page.tsx` | React state, API calls, data visualization |
| `backend/app/db/mongodb.py` | Motor async driver, connection management |

---

## 🎓 13. Technology Fundamentals for Beginners

This section explains the fundamental concepts of each technology used in IntelliHire, assuming you're a complete beginner. We'll use simple analogies and examples to make these concepts easy to understand and remember.

---

### 🐍 Python - The Core Language

**What is Python?**
Python is a programming language known for being easy to read and write. It's like English for computers.

**Analogy:** If programming languages were ways to give someone directions:
- **Assembly** = "Walk 47 steps north, turn 32.5 degrees left, walk 12 steps..."
- **Python** = "Go to the coffee shop on Main Street"

**Why Python for This Project?**
```python
# Python is readable - even non-programmers can understand:
if candidate.score > 80:
    send_interview_invite(candidate)
else:
    add_to_waiting_list(candidate)
```

**Key Python Concepts Used:**

```python
# 1. LISTS - Ordered collections
skills = ["python", "react", "aws"]
skills.append("docker")  # Add item
first_skill = skills[0]  # Access by index: "python"

# 2. DICTIONARIES - Key-value pairs (like a real dictionary!)
candidate = {
    "name": "Jane Smith",
    "score": 85,
    "skills": ["python", "react"]
}
print(candidate["name"])  # "Jane Smith"

# 3. FUNCTIONS - Reusable blocks of code
def calculate_score(experience, skills, trajectory):
    return experience * 0.5 + skills * 0.35 + trajectory * 0.15

# 4. ASYNC/AWAIT - Do other things while waiting
async def fetch_and_process():
    data = await get_from_database()  # Don't block while waiting
    return process(data)

# 5. CLASSES - Blueprints for objects
class Resume:
    def __init__(self, name, skills):
        self.name = name
        self.skills = skills
    
    def has_skill(self, skill):
        return skill in self.skills

jane = Resume("Jane", ["python", "react"])
print(jane.has_skill("python"))  # True
```

---

### ⚡ FastAPI - The Backend Framework

**What is FastAPI?**
FastAPI is a tool for building web APIs (Application Programming Interfaces) in Python. It handles HTTP requests from the frontend and returns responses.

**Analogy:** 
Imagine a **restaurant**:
- **Customer (Frontend)** → Places an order (HTTP request)
- **Waiter (FastAPI)** → Takes the order, brings it to the kitchen, returns with food
- **Kitchen (Business Logic)** → Prepares the meal
- **Food (Response)** → What the customer receives

**Basic FastAPI Concepts:**

```python
from fastapi import FastAPI, HTTPException

# Create the app (the restaurant)
app = FastAPI()

# Define an endpoint (a menu item)
@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """This function runs when someone visits /candidates/123"""
    candidate = find_in_database(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Not found")
    return candidate

# POST request (sending data)
@app.post("/candidates")
async def create_candidate(name: str, skills: list):
    """Create a new candidate"""
    new_id = save_to_database(name, skills)
    return {"id": new_id, "message": "Created!"}
```

**HTTP Methods Explained:**
| Method | Restaurant Analogy | Example |
|--------|-------------------|----------|
| GET | "Show me the menu" | Get candidate info |
| POST | "I'd like to order this" | Upload a new resume |
| PUT | "Change my order to X" | Update candidate details |
| DELETE | "Cancel my order" | Remove a candidate |

**Dependency Injection (Advanced but Important):**
```python
def get_database():
    """This creates a database connection"""
    return DatabaseConnection()

@app.get("/candidates")
async def list_candidates(db = Depends(get_database)):
    """FastAPI automatically calls get_database() and passes it in"""
    return db.query("SELECT * FROM candidates")
```

---

### ⚛️ React - The Frontend Library

**What is React?**
React is a JavaScript library for building user interfaces. Instead of writing one giant HTML file, you build small, reusable "components" like LEGO blocks.

**Analogy:**
Building a webpage like building with LEGOs:
- **Header Component** = The top LEGO piece (logo, navigation)
- **Button Component** = A small brick you can use anywhere
- **Card Component** = A medium structure showing candidate info
- **App** = All the pieces snapped together

**Core React Concepts:**

```jsx
// 1. COMPONENTS - Building blocks
function CandidateCard({ name, score }) {
  return (
    <div className="card">
      <h2>{name}</h2>
      <p>Score: {score}%</p>
    </div>
  );
}

// 2. PROPS - Data passed to components (like function arguments)
<CandidateCard name="Jane Smith" score={85} />
// Renders: Jane Smith, Score: 85%

// 3. STATE - Data that changes over time
import { useState } from 'react';

function Counter() {
  // count starts at 0, setCount changes it
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}

// 4. HOOKS - Special functions for state and side effects
import { useState, useEffect, useMemo } from 'react';

function Dashboard() {
  const [data, setData] = useState([]);
  
  // useEffect - Run code when component loads
  useEffect(() => {
    fetch('/api/candidates')
      .then(res => res.json())
      .then(data => setData(data));
  }, []);  // Empty array = run once on load
  
  // useMemo - Cache expensive calculations
  const topCandidates = useMemo(() => {
    return data.filter(c => c.score > 80);
  }, [data]);  // Only recalculate when data changes
  
  return <div>{/* render candidates */}</div>;
}
```

**Why React Re-renders:**
```
State Changes → React Detects Change → Component Re-renders → UI Updates

Example:
1. User clicks "Process Candidates"
2. setResults(newData) is called
3. React sees 'results' changed
4. Components using 'results' re-render
5. User sees ranked candidate list
```

---

### 🚀 Next.js - The React Framework

**What is Next.js?**
Next.js is a framework built on top of React that adds extra features like routing, server-side rendering, and API routes.

**Analogy:**
- **React** = Engine of a car
- **Next.js** = Complete car with steering wheel, GPS, air conditioning

**Key Next.js Features:**

```
1. FILE-BASED ROUTING
   Instead of configuring routes, just create files:
   
   frontend/app/
   ├── page.tsx       → localhost:3000/
   ├── about/
   │   └── page.tsx   → localhost:3000/about
   └── candidates/
       └── [id]/
           └── page.tsx → localhost:3000/candidates/123

2. SERVER COMPONENTS (New in Next.js 13+)
   Components that run on the server, not in the browser.
   Benefits: Faster page loads, smaller JavaScript bundles.

3. API ROUTES
   You can create backend APIs right in Next.js:
   frontend/app/api/hello/route.ts → localhost:3000/api/hello
```

**Client vs Server Components:**
```tsx
// SERVER COMPONENT (default) - runs on server
// Can access database, file system, etc.
async function CandidateList() {
  const candidates = await db.query('SELECT * FROM candidates');
  return <ul>{candidates.map(c => <li>{c.name}</li>)}</ul>;
}

// CLIENT COMPONENT - runs in browser
// Use for interactivity (clicks, state)
"use client";
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

---

### 📘 TypeScript - Type-Safe JavaScript

**What is TypeScript?**
TypeScript is JavaScript with added "types" - labels that tell you what kind of data a variable holds.

**Analogy:**
Imagine labeled boxes:
- **JavaScript**: Any box can hold anything (risky!)
- **TypeScript**: Boxes have labels - "Books Only", "Clothes Only" (safe!)

**Why TypeScript?**
```typescript
// WITHOUT TypeScript (JavaScript)
function greet(name) {
  return "Hello, " + name.toUpperCase();
}
greet(123);  // RUNTIME ERROR! 123.toUpperCase is not a function

// WITH TypeScript
function greet(name: string): string {
  return "Hello, " + name.toUpperCase();
}
greet(123);  // COMPILE ERROR! Caught before running!
// Type error: Argument of type 'number' is not assignable to type 'string'
```

**TypeScript in IntelliHire:**
```typescript
// Define the shape of data
interface Candidate {
  name: string;
  score: number;
  skills: string[];
}

// TypeScript ensures you use it correctly
function displayCandidate(candidate: Candidate) {
  console.log(candidate.name);       // ✅ OK
  console.log(candidate.age);        // ❌ Error: 'age' doesn't exist
  console.log(candidate.score + 10); // ✅ OK, score is a number
}

// Arrays with types
const candidates: Candidate[] = [];
candidates.push({ name: "Jane", score: 85, skills: ["python"] }); // ✅
candidates.push({ name: "John" }); // ❌ Error: missing 'score' and 'skills'
```

---

### 🍃 MongoDB - The Document Database

**What is MongoDB?**
MongoDB is a database that stores data as "documents" (like JSON objects) instead of tables with rows and columns.

**Analogy:**
- **SQL Database (PostgreSQL, MySQL)** = Filing cabinet with rigid folders
  - Every folder must have exact same sections
  - "Name", "Age", "Address" in every folder
  
- **MongoDB** = Flexible notebook
  - Each page can have different information
  - One page has 5 skills, another has 50 skills - both OK!

**SQL vs MongoDB:**
```
SQL TABLE:
+----+-------+-----+
| id | name  | age |
+----+-------+-----+
| 1  | Jane  | 28  |
| 2  | John  | 32  |
+----+-------+-----+

MONGODB COLLECTION:
{
  "_id": "abc123",
  "name": "Jane",
  "age": 28,
  "skills": ["python", "react"],  // Nested array!
  "experience": [                  // Nested objects!
    {"company": "Google", "years": 3},
    {"company": "Meta", "years": 2}
  ]
}
```

**Common MongoDB Operations:**
```python
# Using Motor (async MongoDB driver for Python)
from motor.motor_asyncio import AsyncIOMotorClient

# Connect
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["intellihire"]
collection = db["candidates"]

# CREATE - Insert a document
await collection.insert_one({
    "name": "Jane Smith",
    "skills": ["python", "react"]
})

# READ - Find documents
candidate = await collection.find_one({"name": "Jane Smith"})
all_seniors = await collection.find({"level": "senior"}).to_list(100)

# UPDATE - Modify documents
await collection.update_one(
    {"name": "Jane Smith"},
    {"$set": {"score": 95}}
)

# DELETE - Remove documents
await collection.delete_one({"name": "Jane Smith"})
```

**ObjectId Explained:**
```python
from bson import ObjectId

# MongoDB auto-generates unique IDs
# Example: "507f1f77bcf86cd799439011"
#          ^^^^^^^^ timestamp
#                  ^^^^^^ machine ID
#                        ^^^^ process ID
#                            ^^^^^^ counter

# To query by ID, convert string to ObjectId
id_string = "507f1f77bcf86cd799439011"
object_id = ObjectId(id_string)
document = await collection.find_one({"_id": object_id})
```

---

### 🤖 Google Vertex AI & Gemini - The AI Engine

**What is Vertex AI?**
Google Cloud's platform for machine learning. It hosts various AI models including Gemini.

**What is Gemini?**
Google's latest large language model (LLM) - like ChatGPT, it understands and generates text.

**Analogy:**
- **Vertex AI** = A factory that hosts different machines
- **Gemini** = One specific machine that understands language
- **Prompt** = Instructions you give the machine
- **Response** = What the machine produces

**How We Use Gemini:**
```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize connection to Google Cloud
vertexai.init(project="my-project", location="us-central1")

# Load the Gemini model
model = GenerativeModel("gemini-2.0-flash")

# Create a prompt
PROMPT = """
You are an expert resume parser. Extract structured data:
{
  "name": "extracted name",
  "skills": ["skill1", "skill2"]
}
"""

resume_text = "Jane Smith - Software Engineer - Python, React"

# Generate response
response = model.generate_content([PROMPT, Part.from_text(resume_text)])

# Parse the result
result = response.candidates[0].content.parts[0].text
# result = '{"name": "Jane Smith", "skills": ["python", "react"]}'
```

**LLM Prompting Tips:**
```
1. BE SPECIFIC
   Bad:  "Parse this resume"
   Good: "Extract name, skills, and experience as JSON"

2. GIVE EXAMPLES
   "For input 'John - 5 years Python', output: {name: 'John', skills: ['python']}"

3. SPECIFY OUTPUT FORMAT
   "Return ONLY valid JSON. No markdown. No commentary."

4. HANDLE EDGE CASES
   "If skill is ambiguous, use lowercase. If name is missing, use null."
```

---

### 🎨 Tailwind CSS - Utility-First Styling

**What is Tailwind CSS?**
A CSS framework where you style elements using small utility classes instead of writing custom CSS.

**Analogy:**
- **Traditional CSS** = Custom-tailored suit (made from scratch)
- **Tailwind CSS** = Mix-and-match wardrobe (combine pre-made pieces)

**Traditional CSS vs Tailwind:**
```html
<!-- TRADITIONAL CSS -->
<style>
.card {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
<div class="card">Content</div>

<!-- TAILWIND CSS -->
<div class="bg-white rounded-lg p-4 shadow-md">Content</div>
<!--      ^white    ^rounded   ^padding  ^shadow -->
```

**Common Tailwind Classes:**
| Class | What It Does |
|-------|-------------|
| `p-4` | padding: 1rem (16px) |
| `m-2` | margin: 0.5rem (8px) |
| `flex` | display: flex |
| `grid` | display: grid |
| `text-lg` | large text |
| `font-bold` | bold text |
| `bg-blue-500` | blue background |
| `hover:bg-blue-600` | darker blue on hover |
| `rounded-lg` | large border radius |
| `shadow-md` | medium shadow |

**Responsive Design:**
```html
<!-- Changes based on screen size -->
<div class="text-sm md:text-base lg:text-lg">
  <!-- Small screens: small text -->
  <!-- Medium screens (768px+): base text -->
  <!-- Large screens (1024px+): large text -->
</div>
```

---

### 📊 Recharts - Data Visualization

**What is Recharts?**
A React library for creating charts and graphs. It turns data into visual representations.

**Analogy:** 
If your data is ingredients, Recharts is the recipe for cooking beautiful charts.

**Basic Chart Example:**
```tsx
import { AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

const data = [
  { name: 'Jane', score: 85, skills: 90 },
  { name: 'John', score: 72, skills: 65 },
  { name: 'Bob', score: 68, skills: 80 },
];

function ScoreChart() {
  return (
    <AreaChart width={600} height={300} data={data}>
      <XAxis dataKey="name" />      {/* X-axis shows names */}
      <YAxis />                      {/* Y-axis auto-scales */}
      <Tooltip />                    {/* Hover for details */}
      <Area 
        dataKey="score" 
        fill="#8884d8"              {/* Purple fill */}
        stroke="#8884d8" 
      />
      <Area 
        dataKey="skills" 
        fill="#82ca9d"              {/* Green fill */}
        stroke="#82ca9d" 
      />
    </AreaChart>
  );
}
```

---

### 📄 jsPDF - Client-Side PDF Generation

**What is jsPDF?**
A JavaScript library that creates PDF files directly in the browser, without needing a server.

**Why Client-Side?**
- No server processing needed
- Works offline
- Instant generation
- Reduces server costs

**Basic Usage:**
```typescript
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

function generateReport() {
  // Create new PDF
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(20);
  doc.text("Candidate Report", 40, 40);
  
  // Add table
  autoTable(doc, {
    head: [['Name', 'Score']],
    body: [
      ['Jane Smith', '85%'],
      ['John Doe', '72%'],
    ],
    startY: 60,
  });
  
  // Download the PDF
  doc.save('candidate-report.pdf');
}
```

---

### 🔗 REST APIs - How Frontend Talks to Backend

**What is a REST API?**
REST (Representational State Transfer) is a way for different software systems to communicate over HTTP.

**Analogy:** 
REST API is like a waiter in a restaurant:
1. You (frontend) give your order (request) to the waiter (API)
2. Waiter takes it to the kitchen (backend)
3. Kitchen prepares the food (processes data)
4. Waiter brings back your food (response)

**REST Principles:**
```
1. RESOURCES - Things you can interact with (candidates, resumes, jobs)
2. ENDPOINTS - URLs for each resource
   GET    /candidates      → List all candidates
   GET    /candidates/123  → Get candidate with ID 123
   POST   /candidates      → Create new candidate
   PUT    /candidates/123  → Update candidate 123
   DELETE /candidates/123  → Delete candidate 123

3. STATELESS - Each request is independent (no memory)
4. JSON - Standard format for data exchange
```

**Making API Calls in JavaScript:**
```javascript
// GET request - fetch data
const response = await fetch('http://localhost:8000/api/candidates');
const candidates = await response.json();

// POST request - send data
const response = await fetch('http://localhost:8000/api/candidates', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Jane', score: 85 })
});
const newCandidate = await response.json();

// File upload with FormData
const formData = new FormData();
formData.append('file', selectedFile);

const response = await fetch('http://localhost:8000/api/resumes/upload', {
  method: 'POST',
  body: formData  // No Content-Type header needed for FormData
});
```

---

### 🔒 CORS - Cross-Origin Resource Sharing

**What is CORS?**
A security feature that controls which websites can request data from your API.

**Analogy:**
CORS is like a nightclub bouncer:
- **Bouncer (CORS)** checks if you're on the guest list (allowed origins)
- If you're allowed, you can enter (API responds)
- If not, you're turned away (browser blocks request)

**Why CORS Exists:**
```
Without CORS, any website could:
1. Make requests to your bank's API
2. Steal your data
3. Perform actions on your behalf

With CORS:
1. Bank's API only allows requests from bank.com
2. Evil-website.com gets blocked by the browser
```

**CORS in IntelliHire:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all (for development)
    # In production: allow_origins=["https://intellihire.com"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

---

### 🧮 Hashing (SHA-256) - Unique Fingerprints

**What is Hashing?**
A hash function takes any input and produces a fixed-size "fingerprint" that's unique to that input.

**Analogy:**
Hashing is like a fingerprint scanner:
- Every person has a unique fingerprint
- Same person → same fingerprint (always)
- Different people → different fingerprints
- You can't reverse a fingerprint back to a person

**How We Use Hashing:**
```python
import hashlib

# Same content = same hash (for deduplication)
resume_content = b"Jane Smith - Software Engineer - Python"
hash1 = hashlib.sha256(resume_content).hexdigest()
# Returns: "a1b2c3d4e5f6..." (64 characters)

# Even tiny changes = completely different hash
resume_modified = b"Jane Smith - Software Engineer - Python." # Added period
hash2 = hashlib.sha256(resume_modified).hexdigest()
# Returns: "x9y8z7w6v5..." (completely different!)

# Use case: Check if we've seen this resume before
existing = await collection.find_one({"file_hash": hash1})
if existing:
    print("Already processed this resume!")
```

---

### ⚡ Async/Await - Non-Blocking Operations

**What is Async Programming?**
A way to run tasks that take time (like API calls, database queries) without blocking other operations.

**Analogy:**
- **Synchronous (Blocking)**: You're cooking and must watch the pot. Can't do anything else.
- **Asynchronous (Non-Blocking)**: You put food in the oven, set a timer, and do other tasks while it cooks.

**Sync vs Async:**
```python
# SYNCHRONOUS (Blocking)
def process_resumes(resumes):
    for resume in resumes:
        score = call_gemini_api(resume)  # Wait here for each one
        save_to_db(score)                 # Then wait here
    # Total time: 5 resumes × 2 seconds = 10 seconds

# ASYNCHRONOUS (Non-Blocking)
async def process_resumes(resumes):
    tasks = []
    for resume in resumes:
        task = call_gemini_api_async(resume)  # Start all at once
        tasks.append(task)
    scores = await asyncio.gather(*tasks)      # Wait for all to finish
    for score in scores:
        await save_to_db(score)
    # Total time: ~2-3 seconds (parallel processing!)
```

**Key Keywords:**
```python
# async - marks a function as asynchronous
async def my_function():
    pass

# await - pause here until this operation completes
result = await some_slow_operation()

# Can ONLY use await inside async functions
```

---

### 📦 Environment Variables - Secret Configuration

**What are Environment Variables?**
Configuration values stored outside your code, typically in a `.env` file.

**Why Use Them?**
- **Security**: Don't commit API keys to Git
- **Flexibility**: Different settings for dev/staging/production
- **Secrets**: Database passwords, API keys

**Example `.env` File:**
```bash
# .env (NEVER commit this to Git!)
MONGODB_URL=mongodb://localhost:27017
GOOGLE_CLOUD_PROJECT=my-project-123
SECRET_KEY=super-secret-key-12345
```

**Using Environment Variables:**
```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
#                     ^variable name    ^default if not found

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if not project_id:
    raise ValueError("Missing GOOGLE_CLOUD_PROJECT!")
```

---

## 📝 Quick Reference Card

| Technology | What It Does | One-Line Summary |
|------------|--------------|------------------|
| **Python** | Backend language | Easy-to-read language with great AI libraries |
| **FastAPI** | Web framework | Creates REST APIs with automatic documentation |
| **React** | UI library | Builds interfaces from reusable components |
| **Next.js** | React framework | Adds routing, SSR, and optimization to React |
| **TypeScript** | Type-safe JS | JavaScript with compile-time error checking |
| **MongoDB** | Document database | Stores flexible JSON-like documents |
| **Vertex AI/Gemini** | AI platform | Google's LLM for text understanding |
| **Tailwind CSS** | Styling | Utility classes for rapid UI development |
| **Recharts** | Charts | React components for data visualization |
| **jsPDF** | PDF generation | Creates PDFs in the browser |
| **Motor** | Async MongoDB | Non-blocking MongoDB driver for Python |
| **Pydantic** | Validation | Ensures data matches expected types |
| **rapidfuzz** | String matching | Finds similar strings (handles typos) |

---

> 💡 **Pro Tip**: During interviews, connect your technical answers to **business impact**. "This caching strategy saves ~$X per month in API costs and reduces latency by Y%."

Good luck with your interview! 🚀
