# AutoSpeed 🚗⚡

AutoSpeed is a modular Flask web application built using the application factory pattern and a clean blueprint architecture.  
The frontend uses HTML, CSS, and Bootstrap 5. The backend uses Jinja templating for dynamic rendering, and SQLAlchemy
for the database. 

The project will be deployed on Digital Ocean.

---

## Purpose

AutoSpeed is intended as a personal portfolio and blogging website for technology. Users can create, view, 
edit, and delete entries.  

---

## Features

- Production built
- Flask application factory
- Modular blueprint structure
- Template inheritance
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

### 3. Run the application

[run in root]
flask --app wsgi run --debug 

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

