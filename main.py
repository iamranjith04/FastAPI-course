from fastapi import FastAPI, Query, Path
import uvicorn
from starlette.status import HTTP_204_NO_CONTENT
from pydantic import BaseModel

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




if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


