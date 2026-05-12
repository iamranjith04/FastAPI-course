import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run("main:app.py", host="127.0.0.1", port=8000, reload=True)
