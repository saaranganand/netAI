# netAI

A closed-loop system that translates high-level network intents into validated P4_16 programs for the V1Model architecture, with automatic compilation, logic verification, and persistence.

## Overview

Uses an LLM to generate P4 code from natural language user-provided intent, verifies compilation of generated code with p4c in Docker, runs simple logic checks, and stores each program in a PostgreSQL database.

## Prerequisites

- **Operating System:** WSL2 (Ubuntu) or native Linux/macOS  
- **Python:** 3.12+  
- **Docker:** for running the P4 compiler image (`p4lang/p4c:latest`)  
- **PostgreSQL:** for storing generated programs
- **Groq API key:** Available at https://console.groq.com/keys

## Installation

1. **Clone the repo**

```
git clone https://github.com/saaranganand/netAI.git
cd netAI
```

2. Create a Python virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies

```
pip install -r requirements.txt
```

4. Pull the P4 compiler Docker image

```
docker pull p4lang/p4c:latest
```

5. Ensure PostgreSQL is running (create user & database):

```
sudo service postgresql start
sudo -u postgres createuser netai_user --pwprompt
sudo -u postgres createdb netai_db -O netai_user
```

## Configuration

Create a .env file in the project root with:
```env
GROQ_API_KEY=groq_key_goes_here
GROQ_MODEL=gemma2-9b-it

DATABASE_URL=postgresql+psycopg2://your_username_here:your_password_here@localhost/netai_db
```

## Usage

Run the main script

```
python src/main.py
```

and enter your intent when prompted.

- The generated P4 code will be written to out/program.p4.

- Compilation and logic-verifier results will be printed.

- Each run is recorded in the `programs` table in the database.

## Directory Structure

```
netAI/
├── src/
│   ├── main.py           # prompt assembly & loop
│   ├── llm_client.py     # LLM abstraction
│   ├── compiler.py       # Docker-based p4c runner
│   ├── logic.py          # logic/verifier
│   └── db.py             # database
├── prompts/              # instruction & example fragments
│   ├── instructions.txt
│   ├── example1.txt
│   ├── example2.txt
│   ├── example3.txt
│   └── final.txt
├── out/                  
│   └── program.p4        # LLM-generated P4 code
├── requirements.txt
├── README.md
└── .env                  # user-specific environment variables
```
