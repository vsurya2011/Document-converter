from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import qrcode
import time
import subprocess  # Required to run LibreOffice on Linux
import zipfile  # NEW: Required for ZIP conversion

# Linux-compatible libraries
from pdf2docx import Converter
from PIL import Image, ImageDraw
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document

app = Flask(__name__)

# 1. SETUP PATHS (Optimized for Linux/Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png") 

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# On Render/Linux, poppler is installed globally, so we set this to None
POPPLER_PATH = None 

def convert_via_libreoffice(input_path, output_folder):
    """Uses LibreOffice to convert Word/Excel/PPT to PDF on Linux."""
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'pdf', 
        '--outdir', output_folder, input_path
    ], check=True)

def make_stylish_qr(data, logo_path, output_path):
    """Generates a QR code for the provided link data with a central logo."""
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    try:
        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            qr_width, qr_height = qr_img.size
            logo_max_size = qr_width // 3 
            logo.thumbnail((logo_max_size, logo_max_size), Image.LANCZOS)

            bg_size = (logo.width + 20, logo.height + 20)
            logo_bg = Image.new("RGBA", bg_size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(logo_bg)
            draw.rounded_rectangle([(0, 0), bg_size], radius=15, fill=(255, 255, 255, 255))

            pos_logo = ((bg_size[0] - logo.width) // 2, (bg_size[1] - logo.height) // 2)
            logo_bg.paste(logo, pos_logo, mask=logo)
            pos = ((qr_width - bg_size[0]) // 2, (qr_height - bg_size[1]) // 2)
            qr_img.paste(logo_bg, pos, mask=logo_bg)
    except Exception as e:
        print(f"QR Logo processing error: {e}")

    qr_img.save(output_path)

@app.route('/')
def index():
    return render_template("index1.html")

@app.route('/upload')
def upload_page():
    # This renders index2.html where users pick files
    return render_template("index2.html")

@app.route('/qr-converter')
def qr_upload_page():
    return render_template("index3.html")

@app.route('/api/convert', methods=['POST'])
def convert_api():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        files = request.files.getlist('file') # Get all uploaded files
        conversion = request.args.get('type', '').upper().replace('%20', ' ')

        if not files or files[0].filename == "":
            return jsonify({"error": "No file selected"}), 400

        unique_prefix = str(int(time.time()))
        output_path = ""

        # ---------- ZIP CONVERSION (Multi-file support) ----------
        if "ZIP" in conversion:
            zip_filename = f"converted_{unique_prefix}.zip"
            output_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            
            with zipfile.ZipFile(output_path, 'w') as zipf:
                for file in files:
                    sf_name = secure_filename(file.filename)
                    temp_input = os.path.join(UPLOAD_FOLDER, f"zip_{unique_prefix}_{sf_name}")
                    file.save(temp_input)
                    zipf.write(temp_input, sf_name)
                    os.remove(temp_input) # Clean up temp file after zipping

        # ---------- SINGLE FILE CONVERSIONS ----------
        else:
            file = files[0] # Single file logic for other types
            safe_name = f"{unique_prefix}_{secure_filename(file.filename)}"
            filename_no_ext = os.path.splitext(safe_name)[0]
            input_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, safe_name))
            file.save(input_path)

            if "PDF TO WORD" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".docx")
                cv = Converter(input_path)
                cv.convert(output_path)
                cv.close()

            elif any(x in conversion for x in ["WORD TO PDF", "PPT TO PDF", "EXCEL TO PDF"]):
                convert_via_libreoffice(input_path, OUTPUT_FOLDER)
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".pdf")

            elif "PDF TO IMAGE" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".jpg")
                images = convert_from_path(input_path)
                if images:
                    images[0].save(output_path, "JPEG")
                else:
                    raise Exception("Conversion failed.")

            elif "IMAGE TO PDF" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".pdf")
                img = Image.open(input_path)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, "PDF")

            elif "TEXT TO PDF" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".pdf")
                c = canvas.Canvas(output_path, pagesize=letter)
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                y = 750
                for line in lines:
                    c.drawString(40, y, line.strip())
                    y -= 15
                c.save()

            elif "WORD TO TEXT" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + ".txt")
                doc = Document(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write("\n".join([p.text for p in doc.paragraphs]))

            elif "LINK TO QR CODE" in conversion:
                output_path = os.path.join(OUTPUT_FOLDER, filename_no_ext + "_qr.png")
                with open(input_path, 'r', errors='ignore') as f:
                    link_content = f.read().strip()
                qr_link = link_content if link_content else "https://google.com"

                logo_file = request.files.get('logo')
                current_logo_path = LOGO_PATH 
                temp_logo_created = False

                if logo_file and logo_file.filename != "":
                    temp_logo_name = f"tmp_{unique_prefix}_{secure_filename(logo_file.filename)}"
                    temp_logo_path = os.path.join(UPLOAD_FOLDER, temp_logo_name)
                    logo_file.save(temp_logo_path)
                    current_logo_path = temp_logo_path
                    temp_logo_created = True
                
                make_stylish_qr(qr_link, current_logo_path, output_path)

                if temp_logo_created and os.path.exists(current_logo_path):
                    os.remove(current_logo_path)

        if not output_path or not os.path.exists(output_path):
            return jsonify({"error": f"Failed to generate output for: {conversion}"}), 500

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
