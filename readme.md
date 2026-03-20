# FootNotif ⚽📩

FootNotif is a small **FastAPI** project that lets people **subscribe to football teams** and receive **email notifications** about upcoming matches (daily or weekly).

It uses the **football-data.org API** to fetch teams and matches, and a **SQLite** database to store subscribers and subscriptions.

The project also includes a **React + Vite + TypeScript admin interface** to manage subscribers easily.

---

# Features

- ✅ Create subscribers (email + notification frequency)
- ✅ Subscribe an email to multiple teams
- ✅ List subscribers
- ✅ List a subscriber’s subscribed teams
- ✅ Remove a subscriber
- ✅ Remove a subscription (email + team)
- ✅ Search teams by name
- ✅ Send notifications on demand via an API endpoint
- ✅ Admin interface (React + Vite + TypeScript)
- ✅ Scheduled notifications support
- ✅ Local persistence with SQLite
- ✅ Logging for scheduled job runs

---

# Tech stack

## Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- **SQLite**
- **football-data.org API**
- **SMTP email sending**
- **python-dotenv**

## Frontend

- **React**
- **Vite**
- **TypeScript**
- **Axios**

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/EthanCoutard/FootNotif.git
cd FootNotif
```

---

## 2. Run the install script

**Prerequisites:** Python & Node.js installed

The project includes installation scripts that automatically:

- create the Python **virtual environment**
- install **Python dependencies**
- install **Node dependencies**
- configure the **scheduled notification job**

### Windows

| Command                         | Effect                                 |
|---------------------------------|----------------------------------------|
| `install.ps1`                   | installs + starts API + starts Front   |
| `install.ps1 -NoFront`          | installs + starts API only             |
| `install.ps1 -NoStart`          | installs only                          |
| `install.ps1 -NoStart -NoFront` | installs only (NoStart takes priority) |
| `start.ps1`                     | starts API + starts Front              |
| `start.ps1 -NoFront`            | starts API only                        |


### Linux

```bash
bash install.sh
```

⚠️ After installation you **must configure the `.env` files** before running the project.

---

# Environment variables (.env)

Two `.env` files are required.

---

# Root `.env` (API configuration)

Copy the example file:

```bash
cp .env.example .env
```

Example configuration:

```env
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
API_TOKEN=your_football_data_api_token
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
API_PORT=8000
```

---

# Gmail configuration (App Password)

If you use Gmail, you **cannot use your normal password**.  
You must create an **App Password**.

Steps:

1. Go to  
   https://myaccount.google.com/security

2. Enable **2-Step Verification** if it is not already enabled.

3. Go to **App passwords**

4. Create a new app password:
   - App: **Mail**
   - Device: **Other**

5. Google will generate a **16-character password**.

Example:

```
abcd efgh ijkl mnop
```

Use this value for:

```
APP_PASSWORD
```

in your `.env`.

---

# football-data API token

You also need an API token from:

```
https://football-data.org
```

Steps:

1. Create a free account
2. Go to your dashboard
3. Copy your API key
4. Paste it into your `.env`

```
API_TOKEN=your_token_here
```

---

# Frontend `.env`

The admin interface also uses environment variables.

Copy the example file:

```bash
cp football-admin/.env.example football-admin/.env
```

Example:

```env
VITE_API_URL=http://127.0.0.1:8080
```

---

# Running the API

Start the backend API:

```bash
.venv/bin/python3 app.py
```

The API will start on:

```
http://127.0.0.1:YOUR_PORT
```

Health endpoint:

```
GET /health
```

---

# Admin Interface

FootNotif includes a **React + Vite + TypeScript admin interface**.

It allows you to:

- view subscribers
- manage subscriptions
- search teams
- trigger notifications manually

## Run the admin interface

```bash
cd football-admin
npm run dev
```

The admin interface runs on:

```
http://localhost:5173
```

---

# Scheduled notifications

FootNotif includes scripts that automatically run a job responsible for sending notifications.

The job performs the following actions:

1. Creates the `logs/` directory if needed  
2. Checks if the API is running (`GET /health`)  
3. Starts the API if necessary  
4. Triggers the notification endpoint  
5. Writes logs to `logs/job.log`

---

# Scheduled tasks

The scheduled notification job is **installed automatically by the install script**.

## Windows

Uses **Windows Task Scheduler**.

Task installed automatically by:

```
install.bat
```

The task runs daily at **00:00** and executes:

```
runJob.bat
```

---

## Linux

Uses **cron**.

Cron entry installed automatically by:

```
install.sh
```

The cron job runs daily at **00:00** and executes:

```
runJob.sh
```

---

# Notification logic

Implemented in:

```
core/service.py
```

Rules:

- **DAILY subscribers** receive matches for the next **1 day**
- **WEEKLY subscribers** are processed on **Sunday**
- Weekly subscribers receive matches for the next **7 days**

The endpoint returns:

- list of notified emails
- number of notifications sent

---

# API endpoints overview

Base URL:

```
http://127.0.0.1:8000
```

---

## Health

```
GET /health
```

Returns:

```json
{"message":"ok"}
```

---

## Subscribers

List subscribers

```
GET /subscribers
```

Create subscriber

```
POST /subscribers
```

Delete subscriber

```
DELETE /subscribers/{email}
```

List subscriber teams

```
GET /subscribers/{email}/teams
```

---

## Subscriptions

Create subscription

```
POST /subscriptions
```

Remove subscription

```
DELETE /subscriptions/{email}/{teamName}
```

---

## Teams

Search teams

```
GET /teams/search?q=...
```

---

## Notifications

Trigger notifications manually

```
POST /notifications/send
```

---

# Example API requests

Create subscriber

```bash
curl -X POST "http://127.0.0.1:8000/subscribers" \
-H "Content-Type: application/json" \
-d '{"email":"user@example.com","frequency":"DAILY"}'
```

Subscribe to teams

```bash
curl -X POST "http://127.0.0.1:8000/subscriptions" \
-H "Content-Type: application/json" \
-d '{"email":"user@example.com","teams":["Paris Saint-Germain FC","FC Barcelona"]}'
```

Search teams

```bash
curl "http://127.0.0.1:8000/teams/search?q=paris"
```

Send notifications manually

```bash
curl -X POST "http://127.0.0.1:8000/notifications/send"
```

---

# Project structure

```
FootNotif/
├── api/
│   └── api.py
├── core/
│   ├── database.py
│   ├── football_api.py
│   ├── mailer.py
│   ├── service.py
│   └── __init__.py
├── football-admin/
│   ├── src/
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.cjs
│   ├── tailwind.config.cjs
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── .env.example
├── data/
│   └── app.db
├── logs/
├── .env.example
├── .gitignore
├── install.sh
├── install.bat
├── installTask.sh
├── installTask.bat
├── runJob.sh
├── runJob.bat
├── app.py
├── config.py
└── requirements.txt
```

---

# Contributing

Contributions are welcome.

1. Fork the repository

2. Create a branch

```bash
git checkout -b feat/my-feature
```

3. Commit your changes

```bash
git commit -m "feat: add feature"
```

4. Push your branch

```bash
git push origin feat/my-feature
```

5. Open a Pull Request

---

# License

No license file is currently included.
