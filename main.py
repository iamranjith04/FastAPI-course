from typing import List, Literal

from fastapi import (FastAPI,
                     Query,
                     Path,
                     Body,
                     Cookie,
                     Header,
                     Form,
                     File,
                     UploadFile,
                     status,
                     HTTPException,
                     Request)
from fastapi.encoders import jsonable_encoder

from fastapi.responses import JSONResponse
import uvicorn
from starlette.status import HTTP_204_NO_CONTENT
from pydantic import BaseModel, Field

app=FastAPI()

@app.get("/",
         tags=["Get"] ,
         summary="my first hello world get route",
         description="this my first fast api i build for studty purpose",
         status_code=HTTP_204_NO_CONTENT)
async def hello_world():
    return {"Message": "hello world my first web page"}

@app.put("/put", tags=["Put"])
async def put():
    """
    This is a put function example
    - **point 1**: point 1 description
    - **point 2**: point 2 description
    :return:
    """
    return {"message": "hello from put"}

@app.get("/items/{item_id}/{item_name}", tags=["Get"] )
async def return_item(item_id: int = Path(..., ge=200 , lt=1000),
                      item_name: str = Path(..., min_length=1)):
    return {item_id:item_name}


@app.put("/addUser", tags=["Put"])
async def add_user(name: str = Query("Guest", min_length=3, max_length=10),
                   password: str= Query(..., min_length=8)):
    return {name:password}


class Item(BaseModel):
    id: int
    name: str
    price: float
    tax: float | None =None #nullable

class User(BaseModel):
    name: str
    phone_no: str | None = Field(None, max_length=10, min_length=10, title="User mobile number")

@app.post("/add_item", tags=["Request Body"])
async def create_item(item: Item):
    return item

#Making Query Variable into Body Variable using Body()
@app.post("/bill_item", tags=["Request Body"])
async def generate_bill(items: list[Item], user: User, discount: int | None = Body(...)):
    """
    When you have multiple Pydantic models in a FastAPI endpoint (like your items and user),
    FastAPI automatically expects them to be keys in a single JSON body.
    However, if you have only one Pydantic model, but you still want it to be wrapped in a
    specific key, you use the embed=True parameter within Body()
    """
    total = 0
    for item in items:
        total+=item.tax+item.price
    if discount:
        final_price = total - (total * (discount/100))
        return {user.name : final_price}
    return {user.name: total}

#Header and cookie parameter
@app.get("/headersAndCookies", tags=["Header", "Cookie"])
async def get_header_and_cookies(
  cookie_id : int | None = Cookie(None),
  accept_encoding : str | None = Header(None),
  host : str|None = Header(None)
):
    return {
        "cookie_id": cookie_id,
        "accept_encoding": accept_encoding,
        "host" : host
    }

#Form fields
@app.post("/login", tags=["Form"])
async def login(username: str = Form(...), password: str = Form(..., min_length=8)):
    return {username : password}

#File upload
@app.post("/files", tags=["File"])
async def files_read(file: bytes|None = File(None)):

    if not file:
        return "No file found"
    return {"fileLength: ":len(file)}

@app.post("/uploadFile", tags=["File"])
async def upload_file(file: UploadFile|None = None):
    if not file:
        return "No file found"
    return {"fileName: ": file.filename }

@app.post("/MultipleFileUpload", tags=["File"])
async def mut_file_upload(files: List[UploadFile] = File(...)):
    if not files:
        return "No file found"
    return {"fileName: ": [file.filename for file in files] }

#Response Model
class UserDetails(BaseModel):
    name: str
    age: int
    username: str

class UserLogin(UserDetails):
    password: str = Field(..., min_length=8)

class UserLoginOutput(UserDetails):
    message : str="Welcome User"

@app.post("/userLogin", response_model=UserLoginOutput, response_model_exclude={"name", "age"}, tags=["Response_model"])
async def user_login(user: UserLogin):
    return user

@app.post("/old_server", status_code=status.HTTP_204_NO_CONTENT, tags=["Response_model"])
async def old_server():
    return "hello from old server"

#Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content=f"Hello i am exception handler. Server is lazy! message from server: {exc.detail}")

@app.get("/test/{no}", tags=["Exception"])
async def test_execption(no: int):
    if no%3 == 0:
        raise HTTPException(detail="I dont like multiple of 3", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"Entered No" : no}

#JSON Compatible Encoder
class ItemModel(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5

class ItemModelInput(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None

item_list={
    "foo": {"name": "pen", "description":"Hello pen", "price":10},
    "bah": {"name":"note", "price":35},
    "mah" :{"name": "bottle", "price": 100}
}

@app.get("/list_item/list/{item_id}", tags=["Json Encoder"])
async def list_item_get(item_id : str):
    if item_id not in item_list:
        return "key not found"
    return item_list[item_id]

@app.post("/list_item/addItem", tags=["Json Encoder"])
async def add_list_item(item_id: str, item: ItemModel):
    item_list[item_id] = jsonable_encoder(item)
    return item_list[item_id]

@app.patch("/list_item/edit/{item_id}", tags=["Json Encoder"])
async def edit_item_list(item_id: str, item: ItemModelInput):
    if item_id not in item_list:
        return "key not found"
    stored_item_data = item_list[item_id]
    stored_item_model = ItemModel(**stored_item_data)
    update_item=item.model_dump(exclude_unset=True)  #item.dict() is deprecated
    update_item_new = stored_item_model.model_copy(update=update_item) # .copy() is deprecated
    item_list[item_id] = jsonable_encoder(update_item_new)
    return update_item_new


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=7800, reload=True)


