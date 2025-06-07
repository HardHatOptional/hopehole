import os
import time
import shutil
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Watch and processed folders
WATCH_FOLDER = os.getenv("WATCH_FOLDER", os.path.expanduser("~/Desktop/PyPIT Bin"))
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", os.path.join(WATCH_FOLDER, "Processed"))

class PyPITHandler(FileSystemEventHandler):
    def process(self, path):
        item_name = os.path.basename(path)
        print(f"Processing: {item_name}")

        prompt = ChatPromptTemplate.from_template(
            "I've dropped '{item}' into PyPIT Bin. Decide exactly how it should be processed:"
        )

        llm = ChatOpenAI(model_name="gpt-4-turbo")
        decision = (prompt | llm).invoke({"item": item_name}).content.strip()

        print(f"AI decision: {decision}")

        if not os.path.exists(PROCESSED_FOLDER):
            os.makedirs(PROCESSED_FOLDER)

        decision_file = os.path.join(PROCESSED_FOLDER, f"{item_name}_decision.txt")
        with open(decision_file, "w") as f:
            f.write(decision)

        dest_path = os.path.join(PROCESSED_FOLDER, item_name)
        shutil.move(path, dest_path)

        subprocess.run(["git", "-C", WATCH_FOLDER, "add", "."])
        subprocess.run(["git", "-C", WATCH_FOLDER, "commit", "-m", f"Processed '{item_name}': {decision}"])
        subprocess.run(["git", "-C", WATCH_FOLDER, "push", "origin", "main"])

    def on_created(self, event):
        if event.is_directory and event.src_path == PROCESSED_FOLDER:
            return
        time.sleep(1)
        self.process(event.src_path)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(PyPITHandler(), WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"Watching {WATCH_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
