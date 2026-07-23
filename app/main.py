from fastapi import FastAPI

app = FastAPI(title="Fast Blog API")

@app.get("/")
def read_root():
    return {"message": "fast-blog API is running"}
