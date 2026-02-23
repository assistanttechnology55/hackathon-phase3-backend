# 🚀 Phase 3 Backend - Todo AI Chatbot

FastAPI backend with OpenAI Agents SDK and MCP Server for AI-powered task management.

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database connection
│   ├── models.py            # SQLModel models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── chat.py          # Chat endpoint with AI
│       └── tasks.py         # MCP tools for tasks
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
cd D:\hackathon-2\phase-3\backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` with your credentials:

```env
# Get from https://console.neon.tech
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/todo_db

# Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# Random 32+ character string
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long
```

### 3. Set Up Neon Database

1. Go to https://console.neon.tech
2. Create new project
3. Copy connection string
4. Paste in `DATABASE_URL` in `.env`

### 4. Run the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login

### Chat
- `POST /api/{user_id}/chat` - Send message & get AI response

### MCP Tools
- `POST /api/mcp/add_task` - Create new task
- `POST /api/mcp/list_tasks` - List tasks
- `POST /api/mcp/complete_task` - Mark task complete
- `POST /api/mcp/delete_task` - Delete task
- `POST /api/mcp/update_task` - Update task

## 🧪 Test the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Chat
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

### 3. MCP Tools
```bash
curl -X POST http://localhost:8000/api/mcp/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1", "title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

## 🎯 Features

✅ **FastAPI** - Modern, fast Python web framework
✅ **SQLModel** - Type-safe ORM
✅ **Neon PostgreSQL** - Serverless database
✅ **OpenAI Agents SDK** - AI-powered responses
✅ **MCP Server** - Standardized tool interface
✅ **Better Auth** - JWT authentication
✅ **CORS Enabled** - Works with frontend

## 🔧 Development

### Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

### View API docs:
Open `http://localhost:8000/docs`

### View database tables:
Tables are created automatically on first run:
- `users` - User accounts
- `tasks` - Todo items
- `conversations` - Chat sessions
- `messages` - Chat messages

## 📝 MCP Tools Specification

The MCP server exposes 5 tools for the AI agent:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create task | user_id, title, description |
| `list_tasks` | List tasks | user_id, status |
| `complete_task` | Complete task | user_id, task_id |
| `delete_task` | Delete task | user_id, task_id |
| `update_task` | Update task | user_id, task_id, title, description |

## 🚀 Deployment

### Deploy to Railway/Render:

1. Push to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy!

### Environment Variables for Production:
- `DATABASE_URL` - Neon PostgreSQL URL
- `OPENAI_API_KEY` - OpenAI API key
- `BETTER_AUTH_SECRET` - JWT secret
- `DEBUG=False`
- `LOG_LEVEL=INFO`

---

**Built for Hackathon II: Spec-Driven Development**
