from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from datetime import date
from letter_utils.generate_letter_content import generate_letter_content

# File name
file_name = "business_letter.pdf"

test_data = {
  "status": "success",
  "batch_id": "b4c6d833-f1c7-4074-b6a9-dedaabe3b710",
  "patient": {
    "id": 1,
    "name": "Ron",
    "age": 18,
    "sex": "M",
    "address": "Golders Green",
    "conditions": ""
  },
  "results": [
    {
      "test_name": "Haemoglobin",
      "value": "118",
      "unit": "g/L",
      "flag": "Low",
      "reference_low": "115",
      "reference_high": "165",
      "source_file": "oneline.csv",
      "batch_id": "b4c6d833-f1c7-4074-b6a9-dedaabe3b710"
    }
  ]
}

# Generate dynamic text
letter_content = generate_letter_content(test_data, "llama3.2:1b")

# Create a canvas
c = canvas.Canvas(file_name, pagesize=LETTER)
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
recipient = test_data["patient"]["name"]
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

print(f"PDF letter generated: {file_name}")
