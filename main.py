from fastapi import FastAPI, Depends
import uvicorn


app=FastAPI()

#Dependencies
async def common_operation(message: str,q:str|None = None):
    res = {"message" : message}
    if q:
        res.update({"q": q})
    return res

@app.get("/items")
async def get_items(item_name: str, common_dict = Depends(common_operation)):
    common_dict.update({"item_name":item_name})
    return common_dict

@app.get("/users")
async def get_user(user_name: str, common_dict = Depends(common_operation)):
    common_dict.update({"user_name":user_name})
    return common_dict

#Class as Dependency
class Item:
    def __init__(self, item_id: int, item_name: str, price: float):
        self.item_id = item_id
        self. item_name = item_name
        self.price = price

@app.post("/post_item/{item_id}")
async def post_item(common: Item = Depends(Item)):
    return common

#Sub-Dependency
def func1(q: str|None = None):
    return q

def func2(q: str|None = Depends(func1), q2: str = "q2"):
    if q:
        return q
    return q2

@app.get("/sub-dependency/")
async def sub_dependency(q = Depends(func2)):
    return q
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


