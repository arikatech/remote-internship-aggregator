# Remote Internship Aggregator & Alert System

A production-style backend system that aggregates remote internship and tech job postings from multiple sources and sends personalized alerts to users via a Telegram bot based on their selected tags and filters.

---

## Live Demo

**API documentation**

https://remote-internship-aggregator.onrender.com/docs

**Telegram Bot**

https://t.me/talenthub_notify_bot

---

# Overview

Finding remote internships often requires checking dozens of company career pages and job boards.

This system automates that process.

The platform continuously ingests job postings from multiple sources, processes and tags them, matches them with user preferences, and sends real-time notifications through Telegram.

Users can configure their preferences using a Telegram bot interface and receive alerts when new matching jobs appear.

---

# Features

### Job ingestion

Aggregates job postings from multiple sources:

* RSS feeds
* Greenhouse job boards
* Lever job boards
* HTML career pages

### Intelligent tagging

Jobs are automatically tagged based on detected keywords:

* Roles: backend, frontend, fullstack
* Fields: data, machine learning, devops
* Languages: python, java, go, dotnet, javascript
* Levels: internship, new grad, mid level, senior
* Work mode: remote

### Personalized subscriptions

Users can configure job alerts via Telegram:

* select technology tags
* enable internship-only mode
* filter remote jobs
* pause notifications anytime

### Real-time notifications

When new jobs are discovered, the system:

1. matches jobs with user subscriptions
2. prevents duplicate notifications
3. sends formatted job alerts through Telegram

### Automated ingestion pipeline

A scheduled ingestion pipeline runs daily via GitHub Actions.

---

# Architecture

The system is built following a **clean architecture / domain-driven structure** separating:

* API layer
* domain logic
* infrastructure integrations
* persistence

```
app
 ├── api
 │   └── routes
 │
 ├── core
 │   ├── config
 │   ├── logging
 │   └── migrations
 │
 ├── db
 │   ├── models
 │   └── session
 │
 ├── domain
 │   └── usecases
 │
 ├── infra
 │   ├── ingestion
 │   └── telegram
 │
 ├── scheduler
 │
 └── main.py
```

---

# Tech Stack

Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic

Database

* PostgreSQL

Infrastructure

* Docker
* Render deployment
* GitHub Actions (scheduled ingestion)

External integrations

* Telegram Bot API
* Greenhouse job boards
* Lever job boards
* RSS feeds

---

# Core System Flow

### 1. Job ingestion

Sources are defined in the database.

Each source has a connector depending on its type:

* RSS
* Greenhouse API
* Lever API
* HTML scraper

The ingestion pipeline collects new jobs and stores them in the database.

---

### 2. Tagging

Each job description is analyzed using keyword rules to generate tags such as:

```
backend
python
devops
machine learning
internship
remote
```

Tags are stored in the job record.

---

### 3. Subscription matching

When a new job appears:

1. all active subscriptions are loaded
2. job tags are compared with user preferences
3. matching users are identified

Matching rules support:

* tag filtering
* internship-only mode
* remote filtering
* keyword search

---

### 4. Notification delivery

Matching users receive Telegram notifications.

Duplicate alerts are prevented through a notification delivery table.

Example message:

```
🆕 Backend Engineer Intern
🏢 Stripe
📍 Remote
🏷 backend, python, internship
🔗 https://job-url
```

---

# Telegram Bot Interface

Users interact with the system through a Telegram bot.

Available features:

* start bot
* manage technology tags
* view selected tags
* pause notifications
* open job links directly

The bot stores user preferences as subscription records in the database.

---

# Deployment

The application is deployed on Render.

Deployment includes:

* FastAPI web service
* PostgreSQL database
* automated database migrations
* scheduled ingestion via GitHub Actions

---

# Scheduled Ingestion

A GitHub Actions workflow triggers the ingestion pipeline daily.

```
.github/workflows/daily-ingest.yml
```

The workflow calls the secure ingestion endpoint to collect new jobs.

---

# Example API Endpoints

| Endpoint            | Description               |
| ------------------- | ------------------------- |
| `/healthz`          | service health check      |
| `/sources`          | manage job sources        |
| `/jobs`             | view collected jobs       |
| `/subscriptions`    | manage user subscriptions |
| `/telegram/webhook` | Telegram bot webhook      |

---

# Future Improvements

Possible extensions:

* web dashboard for managing subscriptions
* additional job sources
* advanced ML-based job classification
* metrics and observability
* job ranking based on relevance
* email notifications

---

# Author

Arika
Computer Science & Data Analysis Student
