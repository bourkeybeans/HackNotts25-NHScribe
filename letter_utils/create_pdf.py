import os
import hashlib
import secrets
from datetime import date

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LETTERS_DIR = os.path.join(PROJECT_ROOT, "letters")

# Ensure the letters folder exists
os.makedirs(LETTERS_DIR, exist_ok=True)


def generate_unique_filename(extension=".html"):
    """Generate a unique hash-based filename that doesn't collide."""

    while True:
        # Create a random 16-byte token and hash it
        token = secrets.token_bytes(16)
        hash_name = hashlib.sha256(token).hexdigest()[:12]  # 12-char hash
        file_name = f"letter_{hash_name}{extension}"
        file_path = os.path.join(LETTERS_DIR, file_name)
        if not os.path.exists(file_path):
            return file_name, hash_name


def create_pdf(patient_name: str, letter_content: str, doctor_name: str = "Farhan") -> dict:
    """Create an HTML letter and return its filename and letter_uid."""

    file_name, letter_uid = generate_unique_filename()
    file_path = os.path.join(LETTERS_DIR, file_name)

    # Generate current date
    today = date.today().strftime("%B %d, %Y")

    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Letter - {patient_name}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.6;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            background-color: #ffffff;
            color: #000000;
        }}
        
        .letterhead {{
            border-bottom: 2px solid #003366;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .sender-info {{
            font-weight: bold;
            font-size: 14pt;
            color: #003366;
            margin-bottom: 5px;
        }}
        
        .sender-address {{
            font-size: 10pt;
            color: #666666;
            margin-bottom: 10px;
        }}
        
        .date {{
            font-size: 12pt;
            margin-bottom: 30px;
        }}
        
        .recipient {{
            margin-bottom: 20px;
            font-size: 12pt;
        }}
        
        .letter-body {{
            font-size: 12pt;
            white-space: pre-wrap;
            margin-bottom: 30px;
        }}
        
        .signature {{
            margin-top: 40px;
            font-size: 12pt;
        }}
        
        .signature-line {{
            margin-bottom: 5px;
        }}
        
        .signature-name {{
            font-weight: bold;
        }}
        
        .signature-title {{
            font-style: italic;
            color: #666666;
            font-size: 11pt;
        }}
        
        .download-section {{
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            text-align: center;
            font-size: 12pt;
        }}
        
        .download-btn {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12pt;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: background-color 0.2s;
        }}
        
        .download-btn:hover {{
            background: #c82333;
        }}
        
        .download-btn:visited {{
            color: white;
        }}
        
        /* Editable content styling */
        .editable {{
            border: 1px solid transparent;
            padding: 2px;
            border-radius: 3px;
            transition: border-color 0.2s;
        }}
        
        .editable:hover {{
            border-color: #cccccc;
        }}
        
        .editable:focus {{
            outline: none;
            border-color: #007bff;
            background-color: #f8f9fa;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                margin: 0;
                padding: 0.5in;
            }}
            .download-section {{
                display: none;
            }}
            .editable {{
                border: none;
            }}
            .editable:hover {{
                border: none;
            }}
        }}
    </style>
</head>
<body data-letter-id="{letter_uid}">
    <div class="letterhead">
        <div class="sender-info">NHS</div>
        <div class="sender-address">
            123 Main Street<br>
            Springfield, USA 12345
        </div>
    </div>
    
    <div class="date">{today}</div>
    
    <div class="recipient">
        Dear {patient_name},
    </div>
    
    <div class="letter-body editable" contenteditable="true" id="letter-content">
{letter_content}
    </div>
    
    <div class="signature">
        <div class="signature-line">Sincerely,</div>
        <div class="signature-name">{doctor_name}</div>
        <div class="signature-title">NHS Medical Professional</div>
    </div>
    
    <div class="download-section">
        <p><strong>Download Options:</strong></p>
        <a href="/letters/{letter_uid}/pdf" class="download-btn" target="_blank">
            📄 Download PDF
        </a>
        <button class="download-btn" onclick="window.print()">
            🖨️ Print Letter
        </button>
    </div>

    <script>
        // Auto-save functionality
        let saveTimeout;
        const letterContent = document.getElementById('letter-content');
        
        function autoSave() {{
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {{
                // Send updated content to server
                const updatedContent = letterContent.textContent;
                
                // Get letter ID from URL or data attribute
                const letterId = document.body.getAttribute('data-letter-id');
                if (letterId) {{
                    fetch(`http://10.249.84.213:8000/letters/${{letterId}}/content`, {{
                        method: 'PUT',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ content: updatedContent }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        console.log('Auto-saved:', data);
                    }})
                    .catch(error => {{
                        console.error('Auto-save failed:', error);
                    }});
                }}
            }}, 2000); // Save after 2 seconds of inactivity
        }}
        
        // Add event listener for content changes
        letterContent.addEventListener('input', autoSave);
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            // Ctrl+S to save
            if (e.ctrlKey && e.key === 's') {{
                e.preventDefault();
                autoSave();
            }}
        }});
    </script>
</body>
</html>"""

    # Write HTML to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return {
        "pdf_url": file_name,
        "letter_uid": letter_uid,
        "file_path": file_name
    }


if __name__ == "__main__":
    print(create_pdf("Benjamin Stacey", "This is a test letter content.\n\nThank you for your attention."))
