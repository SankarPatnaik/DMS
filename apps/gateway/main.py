from fastapi import FastAPI

app = FastAPI(title="DMF Gateway")

@app.get("/health")
def health():
    return {"status":"ok"}
