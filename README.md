# AutoMailer

Sends personalised cold emails to HR contacts from CSV files — one file per day at 10:30 AM IST — fully automated via GitHub Actions. No server, no Colab, no manual trigger needed.

---

## How it works

1. Drop a CSV file into `pending/`
2. GitHub Actions runs every day at 10:30 AM IST
3. The script picks the first CSV alphabetically, sends all emails in it, then moves the file to `sent/`
4. If any emails fail, the file stays in `pending/` and only the failed rows are retried the next day
5. A timestamped log file is written to `logs/` after every run

---

## Project structure

```
AutoMailer/
├── send_hr_emails.py     # Entry point — orchestrates the send loop
├── config.py             # All configurable settings (edit this)
├── email_template.html   # The HTML skeleton and message body (edit this)
├── email_builder.py      # Reads the template and sets the subject line
├── mailer.py             # Gmail SMTP connection and email dispatch
├── csv_handler.py        # CSV read, write, pick, and archive logic
├── logger.py             # Timestamped logging to console + file
├── pending/              # Drop new CSV batches here
├── sent/                 # Processed CSVs are archived here automatically
├── logs/                 # run_YYYY-MM-DD_HH-MM-SS.log files
├── resume/               # Place your resume PDF here
└── .github/workflows/
    └── send_emails.yml   # GitHub Actions schedule (10:30 AM IST daily)
```

---

## CSV format

Each CSV file must have the following columns:

| Column    | Description              |
|-----------|--------------------------|
| `name`    | HR contact's name        |
| `company` | Company name             |
| `mail`    | Recipient email address  |
| `sent`    | Status — managed by the script (`no` / `yes` / `skipped` / `failed`) |

Rows with any missing field are automatically marked `skipped` and logged.

---

## Setup

### 1. Clone and push to GitHub

```bash
git clone <your-repo-url>
cd AutoMailer
git push origin main
```

### 2. Add GitHub secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret           | Value                          |
|------------------|--------------------------------|
| `SENDER_EMAIL`   | Your Gmail address             |
| `SENDER_PASSWORD`| Your Gmail App Password ¹      |

> ¹ Generate at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). Requires 2FA enabled.

### 3. Configure `config.py`

```python
YOUR_NAME       = "Your Full Name"
YOUR_FIRST_NAME = "FirstName"
ROLE_NAME       = "SDE-1"
RESUME_PATH     = "resume/Your_Resume.pdf"  # or None to skip
DELAY_SECONDS   = 5
```

### 4. Customise the email

- Edit `email_template.html` to change the HTML message body.
- Edit `email_builder.py` to change the subject line parameters.

### 5. Add CSV files

Place one or more `.csv` files in `pending/` and push them. The script processes one per day.

---

## Scheduling

The workflow runs at `cron: '0 5 * * *'` (05:00 UTC = 10:30 AM IST).

To change the time, edit `.github/workflows/send_emails.yml`:
```yaml
- cron: 'MINUTE HOUR * * *'   # always in UTC (IST = UTC + 5:30)
```

Common examples:

| IST time  | Cron          |
|-----------|---------------|
| 8:00 AM   | `0 2 * * *`   |
| 9:30 AM   | `0 4 * * *`   |
| 10:30 AM  | `0 5 * * *`   |
| 12:00 PM  | `30 6 * * *`  |

You can also trigger a run manually from the **Actions** tab on GitHub using **Run workflow**.

---

## Logs

Each run produces a log file at `logs/run_YYYY-MM-DD_HH-MM-SS.log` with:
- Per-email status: `SENT` / `SKIPPED` / `FAILED` with name, company, address, and failure reason
- Session summary: total counts, duration, archive status
- All entries are timestamped

Log files are committed back to the repo automatically after each GitHub Actions run.

---

## Row status reference

| Status    | Meaning                                              |
|-----------|------------------------------------------------------|
| `no`      | Not yet attempted                                    |
| `yes`     | Successfully sent                                    |
| `skipped` | Missing required field(s) — will not be retried      |
| `failed`  | Send failed — will be retried on the next run        |
