# 📄 Document Converter

A simple and easy-to-use **document conversion application** built in Python.
This project lets you upload files and convert them between popular document formats via a web interface.

> \_This repository contains the source code, templates, and scripts required to build and deploy the app.\_

---

## 🚀 Features

✔ Upload documents from your computer
✔ Convert between multiple file types
✔ Web interface to manage uploads and downloads
✔ Lightweight and easy to run locally

* pdf -> word
* word -> pdf
* excel -> pdf
* image -> pdf
* text -> pdf
* pdf -> image
* ppt -> pdf
* word -> text
* link -> qr code

---

## 🛠️ Tech Stack

- Python
- Flask (or your framework of choice)
- HTML templates
- Shell scripts (for build/deploy)
- Other Python libraries (listed in `requirements.txt`)

---

## 📦 Installation

### 1. Clone the repository

```sh

git clone https://github.com/vsurya2011/Document-converter.git

cd Document-converter

```

---

### 2. Create and activate a virtual environment
```sh

python3 -m venv venv

source venv/bin/activate        # macOS/Linux

venv\\Scripts\\activate           # Windows

```

---

### 3. Install dependencies

```sh

pip install -r requirements.txt

```

---

## ▶️ Running the App

To start the conversion app locally:
```sh

python app.py

```
This will launch the web server. Visit:
```sh

http://localhost:5000

```
in your browser to use the converter interface.

---

## 🗂️ Project Structure

```

Document-converter/

├── app.py               # Main application logic

├── templates/           # Frontend HTML pages

├── requirements.txt     # Python dependencies

├── build.sh             # Build / setup script

└── render.yaml          # Deployment config (if used)

```

---

## 🧪 Usage

* Open the app in your browser.
* Upload one or more document files.
* Choose target format (e.g., PDF, DOCX, TXT).
* Download your converted file(s).

---

### ⭐ Star the repository if you find this project useful!
