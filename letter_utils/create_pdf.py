from fastapi import FastAPI
import os
import hashlib
import secrets
from datetime import date

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LETTERS_DIR = os.path.join(PROJECT_ROOT, "letters")

# Ensure the letters folder exists
os.makedirs(LETTERS_DIR, exist_ok=True)


def generate_unique_filename(extension=".pdf"):
    """Generate a unique hash-based filename that doesn't collide."""

    while True:
        # Create a random 16-byte token and hash it
        token = secrets.token_bytes(16)
        hash_name = hashlib.sha256(token).hexdigest()[:12]  # 12-char hash
        file_name = f"{hash_name}{extension}"
        file_path = os.path.join(LETTERS_DIR, file_name)
        if not os.path.exists(file_path):
            return file_name


def create_pdf(patient_name: str, letter_content: str) -> str:
    """Create a PDF with the word 'Test' and return its filename."""

    file_name = generate_unique_filename()
    file_path = os.path.join(LETTERS_DIR, file_name)

    # Create a canvas
    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER

    # --- Margins ---
    left_margin = 1 * inch
    right_margin = 1 * inch
    usable_width = width - left_margin - right_margin

    # --- Letterhead / Sender Info ---
    sender_name = "NHS"
    sender_address = ["123 Main Street", "Springfield, USA 12345"]
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, height - 1 * inch, sender_name)
    c.setFont("Helvetica", 11)
    for i, line in enumerate(sender_address):
        c.drawString(left_margin, height - (1.2 + i * 0.2) * inch, line)

    # --- Date ---
    today = date.today().strftime("%B %d, %Y")
    c.drawString(left_margin, height - 2.0 * inch, today)

    # --- Recipient Info ---
    recipient = patient_name
    y_position = height - 2.6 * inch
    c.drawString(left_margin, y_position - 1.3 * inch, f"Dear {recipient},")

    # --- Body Text (auto-wrap) ---
    c.setFont("Times-Roman", 12)
    text_object = c.beginText(left_margin, y_position - 1.8 * inch)

    # Split letter content into wrapped lines based on usable width
    for paragraph in letter_content.split("\n"):
        wrapped_lines = simpleSplit(paragraph, "Times-Roman", 12, usable_width)
        for line in wrapped_lines:
            text_object.textLine(line)
        text_object.textLine("")  # paragraph spacing

    c.drawText(text_object)

    # --- Sign-Off ---
    c.setFont("Times-Roman", 12)
    c.drawString(left_margin, 1.8 * inch, "Sincerely,")
    c.setFont("Times-Bold", 12)
    c.drawString(left_margin, 1.4 * inch, "Farhan")
    c.setFont("Times-Italic", 12)
    c.drawString(left_margin, 1.2 * inch, "Unpaid Intern NHS")

    # Save
    c.save()

    return {"filename": file_name}


if __name__ == "__main__":
    print(create_pdf("Benjamin Stacey", "poaijegpioajeiogjopiawjeg"))
