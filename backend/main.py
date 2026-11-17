from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def home():
    return{"message":"Studymate AI is running"}