# Multi-Agent Productivity Assistant

An AI-powered system designed to manage study schedules and exam preparation tasks using a Multi-Agent orchestration model.

## 🚀 Live Demo
- **Service URL:** [https://productivity-assistant-api-34968598333.us-central1.run.app](https://productivity-assistant-api-34968598333.us-central1.run.app)
- **Database:** Google Cloud Firestore (`exam-db`)

## 🧠 Architecture & Problem Statement Alignment
This project follows the **Gen AI Academy** requirements for stateful multi-agent systems:
- **Orchestration:** A Primary Agent coordinates between two specialized tools: `manage_calendar` and `manage_tasks`.
- **Persistence:** All data is stored in a structured Firestore database (`exam-db`), ensuring a "Single Source of Truth" for both the AI and the Web Dashboard.
- **Workflow:** The system handles multi-step requests (e.g., "Find the SBI PO exam, add it to my calendar, and set a reminder to study math").

## 🛠️ Key Features
- **Calendar Section:** Automatically appends the current date and time to scheduled events using Python's `datetime`.
- **Interactive Dashboard:** A real-time web view that syncs with the AI's actions.
- **FastAPI Backend:** Deployed as a scalable Cloud Run service.

## 📁 Repository Contents
- `main.py`: The core logic for the API and Dashboard.
- `openapi.yaml`: The schema defining the toolset for Vertex AI.
- `requirements.txt`: Necessary libraries (FastAPI, Google Cloud Firestore).
