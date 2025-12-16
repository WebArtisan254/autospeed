# AutoSpeed 🚗⚡

AutoSpeed is a modular Flask web application built using the application factory pattern and a clean blueprint architecture.  
The frontend uses HTML, CSS, and Bootstrap 5, while the backend is powered by Flask and SQLAlchemy.

This project is designed with DevOps principles in mind.  
The long‑term goal is to containerize the application with Docker and automate deployment to Microsoft Azure using Ansible.

---

## Purpose

AutoSpeed serves as a personal knowledge hub where I can publish articles, walkthroughs, and technical notes.  
The goal is to document the steps I take while learning new technologies, solving problems, and building projects.  
This includes topics like Linux workflows, Flask development, automation, DevOps tooling, and deployment strategies.

---

## Features

- Flask application factory (`create_app`)
- Modular blueprint structure (`main` blueprint)
- Bootstrap 5 integration via Flask-Bootstrap5
- Template inheritance with `base.html`
- Clean project layout for scalability
- Ready for Docker containerization
- Planned Ansible automation for Azure deployment

---

## Getting Started

### 1. Create and activate a virtual environment

python3 -m venv venv
. venv/bin/activate

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Set environment variables 

export FLASK_APP=speed.py
export FLASK_DEBUG=1


### 4. Run the application

flask run 

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

## Ansible + Azure Deployment (Planned)

The deployment pipeline will include:

- Ansible playbooks for provisioning Azure resources  
- Automated deployment of the Docker container  
- Environment variable management  
- Optional CI/CD integration  

---

## License

This project is licensed under the MIT License.

