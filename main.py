import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": dict(
        username="johndoe",
        full_name="John Doe",
        email="johndoe@example.com",
        hashed_password="fakehashedsecret",
        disabled=False,
    ),
    "alice": dict(
        username="alice",
        full_name="Alice Wonderson",
        email="alice@example.com",
        hashed_password="fakehashedsecret2",
        disabled=False,
    ),
}

def get_db(username):
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

def fake_hash_password(password: str):
    return f"fakehashed{password}"


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str





def fake_decode_token(token):
    if token in fake_users_db:
        return UserInDB(**fake_users_db[token])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    print(user)
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    """
    This function is useful for swagger to get the token and set the token for future request. It identifies
    this route by the tokenurl field in OAuth2PasswordBearer(). the return type also fixed as it expect access_token,
    and token_type
    """
    user = get_db(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    hashed_password = fake_hash_password(credentials.password)
    if hashed_password != user.hashed_password:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    This function expect a authorization header of bearer token which is the username in db
    curl -X GET "http://127.0.0.1:8000/users/me" -H "Authorization: Bearer johndoe"
    """
    return current_user


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    """
       This function expect a authorization header of bearer token which is the username in db
       curl -X GET "http://127.0.0.1:8000/items" -H "Authorization: Bearer johndoe"
    """
    return {"token": token}

if __name__ == '__main__':
    uvicorn.run("main:app.py", host="127.0.0.1", port=8000, reload=True)
