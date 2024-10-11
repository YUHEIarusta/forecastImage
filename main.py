from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/forecast")
def forecast():
    return {"forecast": "Today's weather is sunny."}
