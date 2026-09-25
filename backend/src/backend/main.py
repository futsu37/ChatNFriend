from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"Health check": "Working"}