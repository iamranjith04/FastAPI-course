from fastapi import FastAPI, Query, Path, Body, Cookie, Header,Form
import uvicorn
from starlette.status import HTTP_204_NO_CONTENT
from pydantic import BaseModel, Field

app=FastAPI()

@app.get("/",
         tags=["Get"] ,
         summary="my first hello world get route",
         description="this my first fast api i build for studty purpose",
         status_code=HTTP_204_NO_CONTENT)
async def helloWorld():
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
    However, if you have only one Pydantic model but you still want it to be wrapped in a
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
async def getHeaderAndCookies(
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
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(..., min_length=8)):
    return {username : password}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


