
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_storage
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the File Sorter API!"}

@app.get("/api/storage")
def get_storage_info():
    return analyze_storage()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
