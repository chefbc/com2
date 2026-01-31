"""
Inject contact form config (e.g. email subject) from mkdocs.yml into the contact page.
Subject is set in extra.contact_form.subject and replaced in the hidden input at build time.
"""

try:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page
except ImportError:
    MkDocsConfig = None
    Page = None

PLACEHOLDER = "CONTACT_FORM_SUBJECT_PLACEHOLDER"


def on_page_content(html: str, *, page: Page, config: MkDocsConfig, files):
    """Replace contact form subject placeholder with value from mkdocs.yml"""
    if page.file.src_path != "contact.md":
        return html
    extra = getattr(config, "extra", {}) or {}
    contact_config = extra.get("contact_form") or {}
    subject = contact_config.get("subject", "Contact Form Submission")
    if PLACEHOLDER in html:
        html = html.replace(PLACEHOLDER, subject)
    return html
