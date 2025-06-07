# hopehole / PyPIT Automation
Python-based watchdog automation using OpenAI via LangChain to process files dropped into a watch folder.

## Features
- Watch a folder for new files
- Ask an LLM for processing instructions
- Save decisions and move items to a `Processed/` directory
- (Optional) Auto-commit and push changes to Git

## Setup
1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` and `WATCH_FOLDER`.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --no-cache-dir -r requirements.txt
   ```

## Usage
```bash
python PyPIT.py
```  
or
```bash
python auto_wash.py
```

## Docker
```bash
docker build -t hopehole .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e WATCH_FOLDER=/watch \
  -v /local/watch:/watch hopehole
```

## Production Recommendations
- Use environment variables or a secrets manager for API keys
- Run as a service (systemd, Docker, etc.)
- Add logging and error handling around file and API operations

MIT License