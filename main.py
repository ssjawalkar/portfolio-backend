"""
FastAPI backend for the personal portfolio site.

This backend exposes simple REST endpoints that return structured JSON data
describing the user's profile, skills, projects and professional experience.
It also accepts contact form submissions and persists them to a local
text file.  When deploying the API on Render, ensure that the process
listens on the port provided by the environment (Render sets the
``PORT`` environment variable) and allows cross origin requests from
the Vercel frontend.

The data served here is manually curated from the user's résumé and
GitHub repositories【254256442915727†screenshot】.  You can modify these
structures to add or update information without changing the API
contract.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------

class ContactRequest(BaseModel):
    """Schema for contact form submissions."""

    name: str = Field(..., min_length=1, description="Sender's full name")
    email: EmailStr = Field(..., description="Valid email address")
    message: str = Field(..., min_length=1, description="Message body")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Submission time")


# -----------------------------------------------------------------------------
# Static portfolio data
#
# Ideally these would be loaded from a database or external service, but for
# simplicity and to make the API self contained we define them inline.  The
# frontend will consume these endpoints to populate the React components.
# -----------------------------------------------------------------------------

ABOUT = {
    "name": "Samihan Jawalkar",
    "location": "Dallas, TX, USA",
    "role": "Software Engineer",
    "bio": (
        "Samihan Jawalkar is a software engineer based in Dallas, Texas. "
        "He has experience designing and implementing scalable microservices, "
        "building CI/CD pipelines and DevOps workflows, and integrating "
        "AI/ML models into production systems. Samihan has worked at companies "
        "such as ConsultAdd and Avaya, where he built retrieval augmented "
        "generation (RAG) services using FastAPI and Milvus, designed CI/CD "
        "pipelines with Azure DevOps, Jenkins and ArgoCD, and developed "
        "cloud native microservices on Docker and Kubernetes. He earned an "
        "MS in Computer Science from the University of North Carolina at "
        "Charlotte (GPA 3.9/4.0) and a BE in Computer Engineering from "
        "Savitribai Phule Pune University."
    ),
    "email": "samihan.jawalkar@gmail.com",
    "linkedin": "https://linkedin.com/in/samihan-jawalkar/",
    "github": "https://github.com/ssjawalkar",
}

SKILLS = {
    "Languages": [
        "Python",
        "Bash",
        "Shell scripting",
        "TypeScript",
        "HTML5",
        "JavaScript",
        "Java",
    ],
    "Frameworks": [
        "Node.js",
        "Express.js",
        "Django",
        "Flask",
        "Angular",
        "Spring Boot",
    ],
    "Databases": [
        "SQL",
        "MongoDB",
        "Google BigQuery",
    ],
    "Cloud & DevOps": [
        "Azure (Virtual Machines, AKS, Storage Accounts, Key Vault)",
        "Azure DevOps",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "GitHub Actions",
        "ArgoCD",
        "Terraform",
    ],
    "Tools & Technologies": [
        "Datadog",
        "Prometheus",
        "Grafana",
        "Git",
        "Kafka",
        "Playwright",
    ],
}

PROJECTS: List[dict] = [
    {
        "title": "Audio Transcribe",
        "description": (
            "A Java/Spring Boot application that transcribes audio files into text "
            "using OpenAI’s Whisper model.  The service exposes REST APIs and "
            "provides a simple interface to upload audio and retrieve accurate "
            "transcriptions."
        ),
        "tech_used": ["Java", "Spring Boot", "OpenAI Whisper"],
        "github_link": "https://github.com/ssjawalkar/Audio-To-Text",
    },
    {
        "title": "Breast Cancer Detection",
        "description": (
            "A machine‑learning project that applies the K‑Nearest Neighbors "
            "algorithm to classify breast cancer tumours as benign or malignant "
            "using diagnostic measurements from the Wisconsin dataset."
        ),
        "tech_used": ["Python", "scikit‑learn", "KNN"],
        "github_link": "https://github.com/ssjawalkar/Breast-Cancer-Detection",
    },
    {
        "title": "Trading Website",
        "description": (
            "An MVC‑based web application for a simulated trading platform.  It "
            "uses MongoDB with Mongoose for data modelling and Express.js/Node.js "
            "to serve RESTful APIs.  The project implements authentication, "
            "role‑based authorisation, session tracking, password encryption and "
            "server‑side validations."
        ),
        "tech_used": ["MongoDB", "Express.js", "Node.js"],
        "github_link": "https://github.com/ssjawalkar/Lets_Trade",
    },
    {
        "title": "Budget Planner",
        "description": (
            "A simple Java application that helps users create budgets, plan "
            "expenses and track spending categories.  The project demonstrates "
            "basic object‑oriented design and file I/O in Java."
        ),
        "tech_used": ["Java"],
        "github_link": "https://github.com/ssjawalkar/Budget-Planner-Java",
    },
]

EXPERIENCE: List[dict] = [
    {
        "company": "ConsultAdd",
        "role": "Software Engineer",
        "location": "Irving, Texas",
        "start_date": "March 2025",
        "end_date": "Present",
        "responsibilities": [
            "Collaborated with Walmart on the Insights Service, integrating runtime "
            "signals from multiple sources and leveraging GenAI/LLM techniques to "
            "correlate errors and accelerate incident resolution【254256442915727†screenshot】.",
            "Integrated Milvus vector DB to store and query embedded knowledge "
            "artefacts for Retrieval‑Augmented Generation (RAG) workflows, improving "
            "document‑based AI insights【254256442915727†screenshot】.",
            "Designed and implemented RESTful APIs using Flask and FastAPI to fetch "
            "anomaly data, generate insight events and present summarised results"
            "【254256442915727†screenshot】.",
            "Developed CRUD APIs and implemented efficient cleanup logic for Milvus "
            "vector DB and Google Cloud Storage【254256442915727†screenshot】.",
            "Automated unit and integration tests with PyTest, increasing test "
            "coverage from 0 % to 50 %【254256442915727†screenshot】."
        ],
    },
    {
        "company": "Avaya",
        "role": "Software Engineer",
        "location": "Irving, Texas",
        "start_date": "Feb 2023",
        "end_date": "Nov 2024",
        "responsibilities": [
            "Designed and implemented CI/CD pipelines using Azure DevOps, Jenkins "
            "and ArgoCD, reducing deployment errors by 20 % and deployment "
            "downtime by 40 %【254256442915727†screenshot】.",
            "Developed FastAPI‑based microservices to analyse customer–agent chat "
            "conversations with LangChain for RAG and OpenAI, enabling efficient "
            "retrieval and generation of contextual insights【254256442915727†screenshot】.",
            "Automated certificate and key renewal for more than 200 certificates using "
            "Azure DevOps, Jenkins and GitHub Actions, preventing outages and "
            "improving system security【254256442915727†screenshot】.",
            "Built scalable microservices on Docker and Kubernetes to improve "
            "performance and scalability【254256442915727†screenshot】.",
            "Established real‑time monitoring and alerting in Datadog with custom "
            "dashboards to track key metrics and enable swift resolution of P1 and "
            "P2 incidents【254256442915727†screenshot】.",
            "Maintained RESTful APIs using Spring Boot and led front‑end development "
            "with Angular, achieving 85 % code coverage and developing over 100 "
            "Playwright automation scripts【254256442915727†screenshot】."
        ],
    },
    {
        "company": "Cognizant",
        "role": "Software Developer (Associate)",
        "location": "Pune, India",
        "start_date": "Oct 2018",
        "end_date": "Aug 2021",
        "responsibilities": [
            "Built and deployed Python applications for data messaging and file "
            "processing, automating complex ETL processes with Python and Bash "
            "scripts.  The automation reduced manual workload by 80 % and saved 45 "
            "hours per week【254256442915727†screenshot】.",
            "Developed a web UI within the STB Master Data Management (MDM) platform "
            "using JavaScript to automate supply chain processes【254256442915727†screenshot】.",
            "Created reusable data transformation workflows in Informatica ETL to "
            "execute complex business rules, boosting system performance by 50 % "
            "through strategic tuning【254256442915727†screenshot】."
        ],
    },
]


# -----------------------------------------------------------------------------
# FastAPI application
# -----------------------------------------------------------------------------

app = FastAPI(title="Portfolio API", version="1.0.0")

# Configure CORS to allow the frontend running on a separate domain to
# communicate with this API.  During development we allow all origins; when
# deploying you can restrict this to your Vercel domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/about")
async def get_about() -> dict:
    """Return basic profile information."""
    return ABOUT


@app.get("/skills")
async def get_skills() -> dict:
    """Return categorised list of technical skills."""
    return SKILLS


@app.get("/projects")
async def get_projects() -> List[dict]:
    """Return a list of highlighted projects."""
    return PROJECTS


@app.get("/experience")
async def get_experience() -> List[dict]:
    """Return professional experience entries."""
    return EXPERIENCE


@app.post("/contact")
async def submit_contact(request: ContactRequest) -> dict:
    """Handle contact form submissions.

    The message is appended to a local ``messages.txt`` file along with a
    timestamp.  In a production deployment you might send an email or store
    the message in a database instead.
    """
    log_entry = f"{request.timestamp.isoformat()}	{request.name}	{request.email}	{request.message}\n"
    try:
        with open("messages.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist message: {exc}",
        ) from exc
    return {"status": "success", "message": "Thank you for reaching out!"}


@app.get("/")
async def root() -> dict:
    """Root endpoint that documents available endpoints."""
    return {
        "endpoints": [
            "/about",
            "/skills",
            "/projects",
            "/experience",
            "/contact (POST)",
        ],
        "message": "Welcome to Samihan Jawalkar's portfolio API."
    }
