import functions_framework
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from google.cloud import firestore
from datetime import datetime

app = FastAPI()
# Targeting your exam-db
db_client = firestore.Client(database="exam-db")

class ActionRequest(BaseModel):
    action: str
    details: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_website():
    # Fetching fresh data
    tasks_ref = db_client.collection("tasks").order_by("created_at", direction=firestore.Query.DESCENDING).limit(10).stream()
    events_ref = db_client.collection("events").order_by("created_at", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    tasks_html = "".join([f"<div class='p-2 border-bottom'>✅ {t.to_dict().get('details')}</div>" for t in tasks_ref])
    events_html = "".join([f"<div class='p-2 border-bottom'>📅 {e.to_dict().get('details')}</div>" for e in events_ref])

    return f"""
    <html>
        <head>
            <title>Exam Prep Assistant</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background: #f4f7f6; font-family: 'Segoe UI', sans-serif; }}
                .chat-box {{ height: 350px; overflow-y: auto; background: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd; }}
                .user-msg {{ text-align: right; color: #0d6efd; margin-bottom: 10px; }}
                .bot-msg {{ text-align: left; color: #198754; margin-bottom: 10px; }}
                .card {{ border-radius: 15px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body class="container py-5">
            <div class="row">
                <div class="col-md-7">
                    <h2 class="mb-4 text-secondary">Multi-Agent Dashboard</h2>
                    <div class="card mb-4">
                        <div class="card-header bg-primary text-white font-weight-bold">Calendar Section</div>
                        <div class="card-body">{events_html or "No schedule items yet."}</div>
                    </div>
                    <div class="card">
                        <div class="card-header bg-success text-white font-weight-bold">Live Task List</div>
                        <div class="card-body">{tasks_html or "No tasks logged."}</div>
                    </div>
                </div>
                <div class="col-md-5">
                    <h2 class="mb-4 text-secondary">Agent Chat</h2>
                    <div class="chat-box mb-3" id="chatWindow">
                        <div class="bot-msg"><b>Assistant:</b> Ready to schedule your exam prep. Try adding a meeting!</div>
                    </div>
                    <div class="input-group shadow-sm">
                        <input type="text" id="userInput" class="form-control" placeholder="Type here...">
                        <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>

            <script>
                async function sendMessage() {{
                    const input = document.getElementById('userInput');
                    const chat = document.getElementById('chatWindow');
                    const val = input.value;
                    if (!val) return;

                    chat.innerHTML += `<div class='user-msg'><b>You:</b> ${{val}}</div>`;
                    input.value = '';

                    // Logic: If it contains 'meeting' or 'exam', route to calendar, else tasks
                    let route = val.toLowerCase().includes('meeting') || val.toLowerCase().includes('exam') ? '/calendar' : '/tasks';
                    let actionType = route === '/calendar' ? 'create' : 'add';

                    try {{
                        const response = await fetch(route, {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{action: actionType, details: val}})
                        }});
                        
                        if (response.ok) {{
                            chat.innerHTML += `<div class='bot-msg'><b>Assistant:</b> Saved to ${{route.replace('/','')}}! Updating...</div>`;
                            setTimeout(() => {{ window.location.reload(); }}, 1200);
                        }}
                    }} catch (err) {{
                        chat.innerHTML += `<div class='bot-msg text-danger'><b>Error:</b> Server connection failed.</div>`;
                    }}
                    chat.scrollTop = chat.scrollHeight;
                }}
            </script>
        </body>
    </html>
    """

@app.post("/calendar")
def manage_calendar(req: ActionRequest):
    # Appends the current date to the detail string
    current_date = datetime.now().strftime("%Y-%m-%d")
    final_details = f"{req.details} (Scheduled on: {current_date})"
    
    db_client.collection("events").add({
        "details": final_details,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return {"status": "success"}

@app.post("/tasks")
def manage_tasks(req: ActionRequest):
    db_client.collection("tasks").add({
        "details": req.details, 
        "created_at": firestore.SERVER_TIMESTAMP 
    })
    return {"status": "success"}

@functions_framework.http
def fast_api_handler(request):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        response = client.request(request.method, request.path, json=request.get_json(silent=True), headers=dict(request.headers))
        if "text/html" in response.headers.get("content-type", ""): return response.text
        return (response.json(), response.status_code)
