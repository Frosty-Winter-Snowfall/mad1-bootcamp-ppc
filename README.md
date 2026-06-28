# 📌 Placement Portal Cell

A simple placement portal built as part of the **MAD-1 Bootcamp May 2026**. The portal provides separate interfaces for students, companies, and administrators to make the placement process easier to manage.

## ✨ Features

### 👨‍🎓 Student

* Register and log in
* View available placement drives
* Apply to drives
* Track application status
* Update profile

### 🏢 Company

* Register and wait for admin approval
* Create placement drives
* View applicants
* Manage posted drives

### 🛠️ Admin

* Approve or reject company registrations and drives
* View all students and companies
* Search students and companies
* Monitor placement statistics
* Manage the overall portal

---

## 🧰 Tech Stack

* **Python**
* **Flask**
* **SQLAlchemy**
* **Jinja2**
* **Bootstrap 5**
* **HTML & CSS**

---

## 📂 Project Structure

```text
placement-portal/
│── app.py
│── templates/
│── static/
│── instance/
      │── placement.db
│── requirements.txt
│── howtorun.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd placement-portal
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## 🌱 Screens Included

* Login & Registration
* Student Dashboard
* Company Dashboard
* Admin Dashboard
* Placement Drives
* Search Functionality
* Application Management

---

## 💙 About

This project was created as part of the **MAD-1 Bootcamp May Term 2026** to practice full-stack web development using Flask. It helps students understand authentication, role-based access control, CRUD operations, database relationships, and building a complete web application from scratch.

Thanks for checking it out! 😊
