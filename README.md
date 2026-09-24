# 🚗 AI Car Mechanic Chatbot

An AI-powered car mechanic assistant that helps users troubleshoot vehicle problems through a conversational interface. Users can describe symptoms, upload media, receive AI-assisted diagnosis, and book a mechanic/service appointment.

## ✨ Features

* 💬 AI-powered car troubleshooting chat
* 🔧 Vehicle issue diagnosis and possible causes
* 📷 Image/file upload for vehicle problems
* 🧠 Conversation history support
* ⚠️ Safety warnings for potentially dangerous issues
* 📅 Mechanic/service booking
* 📱 Responsive React UI
* 🔐 Environment-based API configuration
* 🌐 REST API using Django

## 🛠️ Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Axios
* Lucide React

### Backend

* Python
* Django
* Django REST-style APIs
* SQLite
* Google Gemini API

### Deployment

* Frontend: Vercel
* Backend: AWS / compatible Python hosting

---

# 📁 Project Structure

```text
ai-car-mechanic/
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── ...
│   ├── package.json
│   └── .env
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   └── ...
│
├── .gitignore
└── README.md
```

# 🚀 Setup Instructions

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-car-mechanic.git
cd ai-car-mechanic
```

## 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Run migrations:

```bash
python manage.py migrate
```

Start the Django server:

```bash
python manage.py runserver
```

Backend will run at:

```text
http://127.0.0.1:8000
```

---

## 3. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

> Restart the Vite development server whenever `.env` values are changed.

---

# 🔌 API Documentation

Base URL:

```text
http://127.0.0.1:8000
```

## 1. Chat

### POST `/api/chat/`

Sends a user's vehicle-related question to the AI mechanic.

### Request

```json
{
  "message": "My car is making a clicking sound when I start it.",
  "conversation_id": null,
  "history": []
}
```

### Response

```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "data": {
    "conversation_id": null,
    "user_message": "My car is making a clicking sound when I start it.",
    "reply": "A clicking sound during startup may indicate a weak battery..."
  }
}
```

---

## 2. Upload Media

### POST `/api/upload/`

Uploads an image or other supported media file related to the vehicle problem.

### Request

`multipart/form-data`

```text
file: vehicle-image.jpg
```

### Response

```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file": {
    "name": "vehicle-image.jpg",
    "size": 24567,
    "content_type": "image/jpeg"
  }
}
```

---

## 3. Diagnosis

### POST `/api/diagnosis/`

Generates a structured diagnosis based on the conversation.

### Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "My car is overheating."
    },
    {
      "role": "assistant",
      "content": "Is the coolant level low?"
    }
  ]
}
```

### Response

```json
{
  "success": true,
  "diagnosis": {
    "title": "Engine Overheating",
    "severity": "high",
    "summary": "The vehicle may have a cooling system issue.",
    "service": "Cooling system inspection",
    "confidence": 0.82
  }
}
```

---

## 4. Create Booking

### POST `/api/booking/`

Creates a mechanic/service booking.

### Request

```json
{
  "customer_name": "John Doe",
  "phone": "9876543210",
  "preferred_date": "2026-09-25",
  "preferred_time": "10:00",
  "problem_description": "Engine overheating",
  "diagnosis": "Possible cooling system issue"
}
```

### Response

```json
{
  "success": true,
  "message": "Booking created successfully",
  "booking": {
    "id": 1,
    "status": "pending"
  }
}
```

---

## 5. Get Booking

### GET `/api/booking/{id}/`

Retrieves the status of an existing booking.

Example:

```text
GET /api/booking/1/
```

### Response

```json
{
  "success": true,
  "booking": {
    "id": 1,
    "status": "pending"
  }
}
```

---

# 🏗️ Architecture

The application follows a simple **three-layer architecture**:

```text
┌──────────────────────────────┐
│        React Frontend        │
│                              │
│ Chat UI / Upload / Booking   │
└──────────────┬───────────────┘
               │ HTTP / REST
               ▼
┌──────────────────────────────┐
│       Django Backend         │
│                              │
│ API Views / Validation       │
│ Booking / Upload / Diagnosis │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│   SQLite    │  │ Gemini API  │
│  Database   │  │ AI Service  │
└─────────────┘  └─────────────┘
```

### Request Flow

1. User enters a vehicle-related problem in the React chat.
2. React sends the request to the Django `/api/chat/` endpoint.
3. Django validates the request and sends the relevant conversation context to the AI service.
4. Gemini generates a car-related response.
5. Django returns the response to React.
6. When enough information is available, the user can request a diagnosis.
7. If the user wants service, the booking form sends booking information to Django.
8. Django stores the booking in SQLite.

## 🤖 AI Design

The AI service is restricted to automobile-related topics such as:

* Engine
* Brakes
* Battery
* Tyres
* Transmission
* Suspension
* Electrical systems
* Maintenance
* Mechanical troubleshooting

The AI is instructed to:

* Ask follow-up questions when information is missing.
* Avoid claiming certainty without sufficient evidence.
* Provide possible causes rather than unsupported definitive diagnoses.
* Include safety warnings when appropriate.
* Reject unrelated questions politely.

## 🔒 Security & Configuration

Sensitive values such as API keys are stored in environment variables.

Do **not** commit `.env` files to GitHub.

Use `.env.example` for required configuration:

```env
GEMINI_API_KEY=
```

The repository `.gitignore` should include:

```text
.env
*.env
node_modules/
venv/
__pycache__/
dist/
```

## 🧪 Testing

Backend:

```bash
python manage.py test
```

Frontend:

```bash
npm run build
```

APIs can also be tested using Postman or curl.

## 📌 Future Improvements

* User authentication
* Persistent conversation history
* Cloud media storage
* Real-time mechanic communication
* Service-center management
* More structured AI diagnosis
* Automated booking confirmation
* Production database such as PostgreSQL

## 👨‍💻 Author

**Pawan Sharma**

Full Stack Developer
React • JavaScript • Python • Django • Node.js • REST APIs

