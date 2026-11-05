# Mini Games

A multiplayer and single-player mini-games web application built with **Flask, Flask-SocketIO, SQLite, HTML, CSS, and JavaScript**.

## Available Games

- Rock Paper Scissors
- Hangman (Currently only single player)
- Tic-Tac-Toe
- Memory Game 

## Tech Stack

| Technology | Purpose |
|---|---|
| Python & Flask | Backend and routing |
| Flask-SocketIO | Real-time multiplayer |
| SQLite | Database |
| HTML & CSS | Frontend structure and styling |
| JavaScript | Game logic and interactivity |
| Docker | Containerized deployment |
| uv | Python dependency management |

### Prerequisites

Choose either Docker or a local Python environment.

**For Docker:**
- Git
- Docker
- Docker Compose

**For local setup:**
- Git
- Python
- uv

### 1. Clone the repository

```bash
git clone https://github.com/Tushar-GIT08/MiniGames
cd MiniGames
```

### 2. Configure environment variables

Create a `.env` file in the project's root directory:

```env
SECRET_KEY="generated-secret-key"
```

Replace the placeholder with a securely generated secret key.

### 3. Run the application

**Using Docker:**

```bash
docker compose up --build
```

**Using uv:**

```bash
uv sync
uv run app.py
```

Open the local URL displayed in your terminal to access the application.

## Data Persistence

Mini Games uses SQLite to store user accounts and game records.

The database is initialized automatically. When using Docker, data is preserved across container rebuilds through a persistent volume.

Keep the `data/` directory intact to retain your saved data.


