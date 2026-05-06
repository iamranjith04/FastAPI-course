from fastapi.testclient import TestClient

from main import app

clientapp = TestClient(app)
def test_put_methods():
    response = clientapp.put("/put/jame")
    assert response.status_code == 200
    assert response.json() ==  {"message": "hello jame from put"}

def test_get_header_and_cookies():
    cookie_id="102"
    host="yyy"
    response = clientapp.get("/headersAndCookies",
                             cookies={"cookie_id": cookie_id},
                             headers={ "host":host})

    assert response.status_code==200
    assert response.json() == {"cookie_id": 102, "accept_encoding": "gzip, deflate", "host": host}

def test_background():
    response = clientapp.post("/background",
                              params={"message": "Hello", "q": "query for hello"})

    assert response.status_code == 200
    assert response.json() == "Success"

def test_user_login():
    response = clientapp.post("/userLogin",
                              json= {
                                  "name": "ram",
                                  "age": 21,
                                  "username": "ram@123",
                                  "password": "123456789"
                              })
    assert response.status_code == 200
    assert response.json() == {
        "username": "ram@123",
        "message": "Welcome User"
    }