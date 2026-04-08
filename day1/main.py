from fastapi import FastAPI
import uvicorn

app = FastAPI()
# How Decorater Work Under The Hood
def home():
    return {"message": "Hello from manually decorated route"}

home = app.get("/")(home)

@app.get("/test")
def test_route():
    return {"message": "Hello from @ decorator route"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
