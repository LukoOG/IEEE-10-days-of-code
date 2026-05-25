# Notes API — IEEE CS UNILAG 10 Days of Code Challenge

A simple Notes API built with FastAPI as part of the **IEEE Computer Society UNILAG 10 Days of Code Challenge (Backend Track)**.

This project implements a basic **CRUD (Create, Read, Update, Delete)** Notes API without a persistent database. Data is temporarily stored in memory and resets whenever the server restarts.

---

## Features

- Create a note
- Get all notes
- Get a single note by ID
- Update a note
- Delete a note
- Automatic API documentation with Swagger UI

---

## Tech Stack

- **Python**
- **FastAPI**
- **Uvicorn**
- **Pydantic**

---

## Project Structure

```text
notes-api/
│── app/
│   ├── main.py
│   ├── schemas.py
│   └── storage.py
│
│── requirements.txt
│── README.md
└── .gitignore
```

### File Breakdown

| File | Description |
|------|-------------|
| `main.py` | Contains all API routes and application logic |
| `schemas.py` | Contains request and response models using Pydantic for validation |
| `storage.py` | Acts as a temporary in-memory database |

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/LukoOG/IEEE-10-days-of-code
cd IEEE-10-days-of-code
```

### 2. Create a Virtual Environment

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

You should see output similar to:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

The API is now running locally.

---

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

Visit: <http://127.0.0.1:8000/docs>