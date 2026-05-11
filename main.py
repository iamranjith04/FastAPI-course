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


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


