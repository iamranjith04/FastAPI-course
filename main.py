import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Query, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError


app = FastAPI()

SECRET_KEY = "@#this#keyistosign%the^jwttokenforvalidation$$"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    age: int
    full_name: str|None = None

class UserInDB(User):
    hash_password : str

fake_db = {
    "johndoe":{
        "username": "johndoe",
        "age": 18,
        "full_name": "johndoe",
        "hash_password": "$2b$12$siBLi3Q273ZwqB7.3q4vuOBkc4YuvQmr42itqEJsNn6kROFiBGHJm"
    }
}

def hashed_password(password):
    return pwd_context.hash(password)

def password_verify(password, hash_db_password):
    return pwd_context.verify(password, hash_db_password)

def get_db(username):
    if username in fake_db:
        return UserInDB(**fake_db[username])
    return None

def generate_token(username, expire_time_in_minutes, role):
    claims = {
        "sub":username,
        "iat": datetime.now(timezone.utc),
        "exp":datetime.now(timezone.utc)+timedelta(minutes=expire_time_in_minutes),
        "role": role
    }
    jwt_token = jwt.encode(claims, SECRET_KEY, algorithm="HS256")
    return jwt_token

def verify_token(token = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        username =  payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return username

@app.post("/register-user/")
async def register_user(user: User = Form(), password: str = Query(..., min_length=8)):
    user_db = get_db(user.username)
    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")
    user_db = UserInDB(username=user.username,
                       age= user.age,
                       full_name=user.full_name,
                       hash_password = hashed_password(password))
    fake_db[user.username]=user_db.model_dump()
    return "Registered successfully"

@app.post("/login")
async def login_user(form_data : OAuth2PasswordRequestForm = Depends()):
    user_db = get_db(form_data.username)
    if not user_db or not password_verify(form_data.password, user_db.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username or password")

    token = generate_token(user_db.username, expire_time_in_minutes=30, role="admin")

    return {"access_token": token , "token_type": "bearer"}

@app.get("/all-users")
async def get_all_users(user_name = Depends(verify_token)):
    return {
        "message" : f"Hello {user_name}",
        "users" : [user for user in fake_db.keys()]
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
