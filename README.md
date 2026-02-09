# AutoSpeed 🚗⚡

AutoSpeed is a modular Flask web application built using the application factory pattern and a clean blueprint architecture.  
The frontend uses HTML, CSS, JavaScript, and Bootstrap 5. The backend uses Jinja templating for dynamic rendering, and SQLAlchemy
for the database. 

The project will be deployed on Digital Ocean.

---

## Purpose

AutoSpeed is intended as a personal portfolio and blogging website for technology.  

---

## Features

- Flask application factory (`create_app`)
- Modular blueprint structure (`main` blueprint)
- Bootstrap 5 integration via Flask-Bootstrap5
- Template inheritance with `base.html.`
- Clean project layout for scalability

---

## Getting Started

### 1. Create and activate a virtual environment

python3 -m venv venv

--LINUX:
. venv/bin/activate

--WINDOWS:
venv\Scripts\Activate

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Set environment variables 

--LINUX:
export FLASK_APP=speed.py
export FLASK_DEBUG=1

--WINDOWS:
$Env:Flask_app = "speed.py"

### 4. Run the application

--LINUX:
flask run

--WINDOWS:
flask run --debug

Visit: `http://127.0.0.1:5000/`

---

## Docker (Planned)

A `Dockerfile` will be added to containerize the application:

- Python base image  
- Install dependencies  
- Copy project files  
- Expose port 5000  
- Run Flask in production mode  

---

## License

This project is licensed under the MIT License.

