import os
import datetime

# ── Globals ────────────────────────────────────────────────────────────────────
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# ── Credentials (set as env vars or GitHub secrets — never hardcode) ───────────
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")  # Gmail App Password

# ── Your details ───────────────────────────────────────────────────────────────
YOUR_NAME       = "Sayak Mondal"   # ← Your full name (used in email sign-off)
YOUR_FIRST_NAME = "Sayak"          # ← Your first name (used in email subject)
ROLE_NAME       = "SDE-1"          # ← Role you are applying for
SKILLS          = [
    "Kotlin", "XML","Jetpack Compose", "MVVM", "Flows", "Coroutines", "Room DB",
    "REST APIs", "JSON", "SQL", "MongoDB", "Git"
]  # ← Core skills

# ── Paths ──────────────────────────────────────────────────────────────────────
RESUME_PATH    = "resume/Sayak_Mondal_Resume.pdf"  # ← Path to resume PDF; None to skip
PENDING_FOLDER = "pending"   # ← Drop new CSV files here
SENT_FOLDER    = "sent"      # ← Processed CSV files are archived here
LOGS_FOLDER    = "logs"      # ← Log files are saved here

# ── Behaviour ──────────────────────────────────────────────────────────────────
DELAY_SECONDS   = 5                            # ← Seconds to wait between emails
REQUIRED_FIELDS = {"name", "company", "mail"}  # ← CSV columns that must be non-empty
