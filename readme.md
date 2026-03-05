# FootNotif ⚽📩

FootNotif is a small **FastAPI** project that lets people **subscribe to football teams** and receive **email notifications** about upcoming matches (daily or weekly).  
It uses the **football-data.org API** to fetch teams/matches and a **SQLite** database to store subscribers + subscriptions.

---

## Features

- ✅ Create subscribers (email + notification frequency)
- ✅ Subscribe an email to multiple teams
- ✅ List subscribers
- ✅ List a subscriber’s subscribed teams
- ✅ Remove a subscriber
- ✅ Remove a subscription (email + team)
- ✅ Search teams by name
- ✅ Send notifications on demand via an API endpoint
- ✅ Scheduled job support:
  - Windows Task Scheduler (`installTask.bat`)
  - Linux cron (`installTask.sh`)
- ✅ Local persistence with SQLite (`data/app.db`)
- ✅ Logging for scheduled job runs (`logs/job.log`)

---

## Tech stack

- **Python**
- **FastAPI** (API)
- **Uvicorn** (server)
- **SQLite** (database)
- **football-data.org API** (teams + matches)
- **SMTP** (email sending)
- **python-dotenv** (`.env` configuration)

---

## Installation

### 1) Clone the repo
```bash
git clone https://github.com/EthanCoutard/FootNotif.git
cd FootNotif
```

### 2) Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

---

## Environment variables (.env)

Create a `.env` file at the project root (you can copy `.env.exemple`).

**Example `.env`:**
```env
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
API_TOKEN=your_football_data_api_token
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Notes
- `API_TOKEN` comes from **football-data.org**.
- If you use Gmail, you usually need an **App Password** (not your normal password).
- `SMTP_PORT` must be an integer.

---

## How to run the API

### Option A — Run directly
```bash
python app.py
```

The API starts on:
- `http://127.0.0.1:8000`

### Option B — Run with uvicorn (manual)
```bash
uvicorn app:main --reload
```

> If you use this option, you may want to adapt `app.py` or create an `asgi.py` later. The project currently starts uvicorn from inside `app.py`.

---

## How the scheduled notification system works

FootNotif provides scripts that run a “job” that does:

1. Create `logs/` if needed  
2. Check if the API is running (`GET /health`)  
3. If not running, start it automatically  
4. Trigger sending notifications by calling `POST /notifications/send`  
5. Append output to `logs/job.log`

### Windows (Task Scheduler)

- Install the scheduled task (daily at **00:00**):
```bat
installTask.bat
```

- The task runs:
  - `runJob.bat`

### Linux (cron)

- Install a cron entry (daily at **00:00**):
```bash
bash installTask.sh
```

- The cron runs:
  - `runJob.sh`



---

## Notification logic (daily vs weekly)

The notification sending logic is implemented in `core/service.py`:

- **DAILY subscribers**: receive matches for the next **1 day**
- **WEEKLY subscribers**: only processed on **Sunday**, and receive matches for the next **7 days**
- When notifications are sent, the endpoint returns:
  - list of emails notified
  - count of recipients

---

## API endpoints overview

Base URL: `http://127.0.0.1:8000`

### Health
- `GET /health`  
  Returns `{"message":"ok"}`

### Subscribers
- `GET /subscribers`  
  List all subscribers

- `POST /subscribers`  
  Create a subscriber

- `DELETE /subscribers/{email}`  
  Delete a subscriber by email

- `GET /subscribers/{email}/teams`  
  Get teams subscribed by that email

### Subscriptions
- `POST /subscriptions`  
  Subscribe an email to one or multiple teams

- `DELETE /subscriptions/{email}/{teamName}`  
  Remove a single subscription

### Teams
- `GET /teams/search?q=...`  
  Search team names in the local DB

### Notifications
- `POST /notifications/send`  
  Trigger “send notifications now”

---

## Project structure

```text
FootNotif/
├─ api/
│  └─ api.py                # FastAPI routes + request/response models
├─ core/
│  ├─ database.py           # SQLite schema + queries
│  ├─ football_api.py       # football-data.org client (teams + matches)
│  ├─ mailer.py             # SMTP email sender (HTML template)
│  ├─ service.py            # business logic (subscriptions + sending rules)
│  └─ __init__.py
├─ logs/                    # job logs (created automatically)
├─ data/
│  └─ app.db                # SQLite DB (created automatically)
├─ .env.exemple             # env example
├─ .gitignore
├─ app.py                   # app entrypoint (init DB, service, run uvicorn)
├─ config.py                # loads env + validates config
├─ installTask.bat          # Windows scheduled task installer
├─ installTask.sh           # cron installer
├─ runJob.bat               # scheduled job runner (Windows)
├─ runJob.sh                # scheduled job runner (Linux)
└─ requirements.txt
```

---

## Example API requests

### 1) Create a subscriber
```bash
curl -X POST "http://127.0.0.1:8000/subscribers" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","frequency":"DAILY"}'
```

### 2) Subscribe to teams
Team names must match what exists in the `teams` table (loaded from football-data.org on startup).
```bash
curl -X POST "http://127.0.0.1:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","teams":["Paris Saint-Germain FC","FC Barcelona"]}'
```

### 3) List subscriber’s teams
```bash
curl "http://127.0.0.1:8000/subscribers/user@example.com/teams"
```

### 4) Search teams
```bash
curl "http://127.0.0.1:8000/teams/search?q=paris"
```

### 5) Send notifications now
```bash
curl -X POST "http://127.0.0.1:8000/notifications/send"
```

### 6) Delete a subscription
```bash
curl -X DELETE "http://127.0.0.1:8000/subscriptions/user@example.com/FC%20Barcelona"
```

### 7) Delete a subscriber
```bash
curl -X DELETE "http://127.0.0.1:8000/subscribers/user@example.com"
```

---

## How to contribute

Contributions are welcome.

1. Fork the repo
2. Create a branch:
   ```bash
   git checkout -b feat/my-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "feat: add my feature"
   ```
4. Push your branch:
   ```bash
   git push origin feat/my-feature
   ```
5. Open a Pull Request

### Suggested improvements
- Add OpenAPI examples / tags in FastAPI routes
- Add Docker support
- Improve email template formatting
- Add tests (pytest)
- Fix `runJob.sh` to force POST on `/notifications/send`
- Add pagination + better team search

---

## License

No license file is currently included.  
If you plan to make this project public/open-source, consider adding a `LICENSE` (MIT, Apache-2.0, etc.).
