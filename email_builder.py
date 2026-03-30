import os
from config import YOUR_NAME, YOUR_FIRST_NAME, ROLE_NAME, SKILLS


def build_email(hr_name: str, company_name: str) -> tuple[str, str]:
    """Returns (subject, html_body) personalised for the given recipient."""

    subject = f"Application for {ROLE_NAME} openings at {company_name} | {YOUR_FIRST_NAME}"

    template_path = "email_template.html"
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Missing {template_path}! Please create it with your HTML content.")

    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    # Wrap each skill in a soft grey bubble span
    bubble_style = "display:inline-block; background-color:#efefe9; color:#666666; padding:5px 10px; margin:0 6px 6px 0; border-radius:12px; font-size:12px;"
    skills_html = "".join(f'<span style="{bubble_style}">{s}</span>' for s in SKILLS)

    # Inject the variables into the HTML template safely
    html = html_template.format(
        hr_name=hr_name,
        company_name=company_name,
        ROLE_NAME=ROLE_NAME,
        YOUR_NAME=YOUR_NAME,
        YOUR_FIRST_NAME=YOUR_FIRST_NAME,
        SKILLS=skills_html
    )

    return subject, html