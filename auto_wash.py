import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Initialize ChatOpenAI
llm = ChatOpenAI(model_name="gpt-4-turbo")

# Watch and processed folders
WATCH_FOLDER = os.getenv("WATCH_FOLDER", os.path.expanduser("~/Desktop/PyPIT Bin"))
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", os.path.join(WATCH_FOLDER, "Processed"))

class PyPITHanlder(FileSystemEventHandler):
    def process_item(self, path):
        item_name = os.path.basename(path)
        print(f"Processing '{item_name}'...")

        # LangChain interaction
        prompt = ChatPromptTemplate.from_template(
            "A file or folder named '{name}' was dropped into PyPIT Bin. "
            "Decide intelligently what should happen next (organize, analyze, summarize, etc.):"
        )
        
        chain = prompt | llm
        response = chain.invoke({"name": item_name})

        decision = response.content.strip()
        print(f"AI Decision: {decision}")

        # Save AI decision as a text file next to the processed item
        decision_file = os.path.join(PROCESSED_FOLDER, f"{item_name}_AI_decision.txt")
        with open(decision_file, "w") as f:
            f.write(decision)

        # Move the item into the processed folder
        dest_path = os.path.join(PROCESSED_FOLDER, item_name)
        shutil.move(path, dest_path)

        # Optional: Auto Git commit
        subprocess.run(["git", "-C", PYPIT_BIN_FOLDER, "add", "."])
        subprocess.run(["git", "-C", PYPIT_BIN_FOLDER, "commit", "-m", f"Processed {item_name}: {decision}"])
        subprocess.run(["git", "-C", PYPIT_BIN_FOLDER, "push", "origin", "main"])
        print(f"'{item_name}' processed and committed!")

    def on_created(self, event):
        # Skip processing the 'Processed' folder itself
        if event.is_directory and event.src_path == PROCESSED_FOLDER:
            return
        # Slight delay ensures file is fully copied
        time.sleep(2)
        self.process_item(event.src_path)

if __name__ == "__main__":
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    observer = Observer()
    observer.schedule(PyPITHanlder(), PYPIT_BIN_FOLDER, recursive=False)
    observer.start()
    print(f"PyPIT Bin is live at '{PYPIT_BIN_FOLDER}'")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
