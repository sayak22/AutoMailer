from config import YOUR_NAME, YOUR_FIRST_NAME, ROLE_NAME


def build_email(hr_name: str, company_name: str) -> tuple[str, str]:
    """Returns (subject, html_body) personalised for the given recipient."""

    # ← Edit the subject line format here
    subject = f"Application for {ROLE_NAME} openings at {company_name} | {YOUR_FIRST_NAME}"

    # ← Edit the email body here to personalise your message
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
            <li>Kotlin-based Android development using Jetpack components (Compose, MVVM, Coroutines, Room)</li>
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

        <p><strong>I can join within 30 days of receiving an offer letter.</strong></p>

        <p>Thank you for your time and consideration — I look forward to hearing from you!</p>

        <p>Warm regards,<br/><strong>{YOUR_NAME}</strong></p>

    </body>
    </html>
    """
    return subject, html
