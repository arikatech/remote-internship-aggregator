from __future__ import annotations

TAG_RULES: dict[str, list[str]] = {
    # level
    "internship": [
        "intern",
        "internship",
        "intern program",
        "summer intern",
        "winter intern",
        "stage",  # common in EU postings
        "placement",
    ],
    "new_grad": [
        "new grad",
        "new graduate",
        "graduate program",
        "graduate scheme",
        "entry level",
        "junior",
    ],
    "mid_level": [
        "mid level",
        "mid-level",
        "associate",
    ],
    "senior": [
        "senior",
        "lead",
    ],

    # roles
    "backend": ["backend", "back-end", "api", "server-side", "microservices"],
    "frontend": ["frontend", "front-end", "react", "vue", "angular", "ui"],
    "fullstack": ["fullstack", "full stack"],
    "ml": ["machine learning", "ml engineer", "deep learning"],
    "data": ["data science", "data scientist", "data engineer", "analytics", "bi"],
    "devops": ["devops", "ci/cd", "sre", "terraform", "ansible"],
    "cloud": ["aws", "azure", "gcp", "cloud", "kubernetes", "k8s"],

    # languages
    "python": ["python", "django", "fastapi", "flask"],
    "java": ["java", "spring", "spring boot"],
    "cpp": ["c++", "cpp"],
    "csharp": ["c#", "csharp"],
    "dotnet": [".net", "dotnet", "asp.net", "aspnet"],
    "javascript": ["javascript", "js "],
    "typescript": ["typescript", "ts "],
    "go": ["golang", "go "],
}

REMOTE_KEYWORDS: list[str] = [
    "remote",
    "work from home",
    "wfh",
    "distributed",
    "fully remote",
    "anywhere",
]