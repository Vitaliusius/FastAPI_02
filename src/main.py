from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
def get_index():
    return FileResponse(Path("frontend") / "index.html")


app.mount("/", StaticFiles(directory="frontend"), name="frontend")
