from fastapi import FastAPI


app = FastAPI(title="scholara")

@app.get("/")
def root():
    return "Welcome to scholara"
