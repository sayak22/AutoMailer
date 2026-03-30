import csv
import smtplib
import time
import os
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ============================================================
#              CUSTOMIZE THESE FIELDS AS NEEDED
# ============================================================

# --- Sender Credentials ---
# These are read from environment variables so secrets are never hardcoded.
# Locally : set them in your shell before running.
# GitHub  : add them as repository secrets (Settings → Secrets → Actions).
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")

# --- Your Details ---
YOUR_NAME       = "Sayak Mondal"
YOUR_FIRST_NAME = "Sayak"
ROLE_NAME       = "SDE-1"               # Role you're applying for

# --- Resume Attachment (optional) ---
# Put your resume inside a `resume/` folder at the project root.
# Example: RESUME_PATH = "resume/Sayak_Mondal_Resume.pdf"
RESUME_PATH     = None

# --- Folder Paths ---
# pending/ : drop new CSV files here before each run
# sent/    : finished CSV files are moved here automatically
PENDING_FOLDER  = "pending"
SENT_FOLDER     = "sent"

# --- Email Subject ---
EMAIL_SUBJECT   = f"Inquiry Regarding {ROLE_NAME} Openings | {YOUR_FIRST_NAME}"

# --- Delay between emails (in seconds) to avoid spam filters ---
DELAY_SECONDS   = 5

# ============================================================
#                    EMAIL TEMPLATE
# ============================================================

def build_email_body(hr_name: str, company_name: str) -> str:
    """
    Builds the HTML email body. Edit the content below to customize your message.
    """
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 15px; color: #222222; line-height: 1.7;">

        <p>Hello <strong>{hr_name}</strong>,</p>

        <p>
            I hope this message finds you well! I wanted to reach out to check if there are any
            relevant openings for the role of <strong>{ROLE_NAME}</strong> at
            <strong>{company_name}</strong>.
        </p>

        <p>
            I am currently working as an <strong>SDE&nbsp;-&nbsp;1&nbsp;(Android)</strong> at
            <strong>Tata 1mg</strong> with <strong>1+ year of experience</strong>, and have
            previously interned at <strong>BluSmart</strong> and <strong>MyFab11</strong>.
        </p>

        <p>My core skill set includes:</p>
        <ul>
            <li>Kotlin-based Android development using Jetpack components
                (Compose, MVVM, Coroutines, Room)</li>
            <li>Firebase integration (Auth, Firestore, Cloud Messaging)</li>
            <li>REST APIs, Git, and Agile workflows</li>
        </ul>

        <p>
            I hold a degree in <strong>Computer Science &amp; Engineering</strong> from
            <strong>IIIT Una</strong>.
        </p>

        <p>
            I have attached my resume for your reference and would truly appreciate it if you
            could let me know about any suitable opportunities or refer me to the right team.
        </p>

        <p>
            Thank you for your time and consideration — I look forward to hearing from you!
        </p>

        <p>
            Warm regards,<br/>
            <strong>{YOUR_NAME}</strong>
        </p>

    </body>
    </html>
    """
    return html

# ============================================================
#                    CORE FUNCTIONS
# ============================================================

def send_email(smtp_server, recipient_email: str, hr_name: str, company_name: str):
    """Compose and send a single email."""
    msg = MIMEMultipart("alternative")
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = recipient_email
    msg["Subject"] = EMAIL_SUBJECT

    # Attach HTML body
    html_body = build_email_body(hr_name, company_name)
    msg.attach(MIMEText(html_body, "html"))

    # Attach resume if provided
    if RESUME_PATH and os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(RESUME_PATH)}"',
        )
        msg.attach(part)
    elif RESUME_PATH:
        print(f"  ⚠️  Resume file not found at '{RESUME_PATH}' — sending without attachment.")

    smtp_server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())


def update_sent_status(csv_path: str, rows: list, fieldnames: list):
    """Rewrite the CSV with updated 'sent' statuses."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pick_next_csv() -> str | None:
    """
    Returns the path of the first .csv file found in the PENDING_FOLDER,
    sorted alphabetically. Returns None if the folder is empty or missing.
    """
    if not os.path.isdir(PENDING_FOLDER):
        print(f"⚠️  Pending folder '{PENDING_FOLDER}/' does not exist.")
        return None

    csv_files = sorted([
        f for f in os.listdir(PENDING_FOLDER)
        if f.lower().endswith(".csv")
    ])

    if not csv_files:
        print(f"📭 No CSV files found in '{PENDING_FOLDER}/'. Nothing to do today.")
        return None

    chosen = os.path.join(PENDING_FOLDER, csv_files[0])
    print(f"📂 Selected file: {chosen}")
    if len(csv_files) > 1:
        print(f"   ({len(csv_files) - 1} more file(s) queued for future days)")
    return chosen


def move_to_sent(csv_path: str):
    """Move a processed CSV file from pending/ to sent/."""
    os.makedirs(SENT_FOLDER, exist_ok=True)
    filename    = os.path.basename(csv_path)
    destination = os.path.join(SENT_FOLDER, filename)

    # Avoid overwriting if a file with same name already exists in sent/
    if os.path.exists(destination):
        base, ext = os.path.splitext(filename)
        import datetime
        stamp       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = os.path.join(SENT_FOLDER, f"{base}_{stamp}{ext}")

    shutil.move(csv_path, destination)
    print(f"\n📁 Moved '{csv_path}' → '{destination}'")


def main():
    # --- Validate credentials ---
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ SENDER_EMAIL or SENDER_PASSWORD environment variable is not set.")
        print("   Set them locally, or add them as GitHub Actions secrets.")
        return

    # --- Pick the next CSV from pending/ ---
    csv_path = pick_next_csv()
    if csv_path is None:
        return

    # --- Read CSV ---
    rows       = []
    fieldnames = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader     = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)

    # Ensure 'sent' column exists
    if "sent" not in fieldnames:
        fieldnames.append("sent")
        for row in rows:
            row.setdefault("sent", "no")

    pending = [r for r in rows if r.get("sent", "").strip().lower() != "yes"]
    print(f"📋 Total entries : {len(rows)}")
    print(f"📬 Emails to send: {len(pending)}\n")

    if not pending:
        print("✅ All emails in this file were already sent. Moving to sent/.")
        move_to_sent(csv_path)
        return

    # --- Connect to Gmail SMTP ---
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("🔐 Logged in to Gmail SMTP successfully.\n")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Make sure you are using a Gmail App Password.")
        print("   Generate one at: https://myaccount.google.com/apppasswords")
        return
    except Exception as e:
        print(f"❌ Could not connect to SMTP server: {e}")
        return

    # --- Send Emails ---
    sent_count  = 0
    error_count = 0

    for row in rows:
        if row.get("sent", "").strip().lower() == "yes":
            continue  # Skip already-sent entries

        company = row.get("company", "").strip()
        email   = row.get("mail", "").strip()
        name    = row.get("name", "").strip()

        if not email:
            print(f"  ⚠️  Skipping {name} at {company} — no email address found.")
            row["sent"] = "skipped"
            continue

        print(f"  📧 Sending to {name} ({company}) → {email} ...", end=" ")

        try:
            send_email(server, email, name, company)
            row["sent"] = "yes"          # Mark as sent in memory
            sent_count += 1
            print("✅ Sent")
        except Exception as e:
            error_count += 1
            print(f"❌ Failed ({e})")

        # Update CSV after every email so progress is saved even if script crashes
        update_sent_status(csv_path, rows, fieldnames)

        time.sleep(DELAY_SECONDS)        # Polite delay between sends

    server.quit()

    # --- Summary ---
    print(f"\n{'='*45}")
    print(f"  ✅ Successfully sent : {sent_count}")
    print(f"  ❌ Failed            : {error_count}")
    print(f"{'='*45}")

    # --- Move file to sent/ ---
    move_to_sent(csv_path)


if __name__ == "__main__":
    main()
