from fastapi import FastAPI, Depends, HTTPException, status
from enum import Enum
from jose import jwt
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional


class Type(Enum):
    hardware = "hardware"
    software = "software"


class Item(BaseModel):
    name: str
    # preis: int
    preis: int = Field(42, title="preis", gt=0, lt=1000)
    typ: Type


class ReturnItem(BaseModel):
    name: str
    typ: Type


items = [
    {"name": "Computer", "preis": 1000, "typ": "hardware"},
    {"name": "Monitor", "preis": 800, "typ": "hardware"},
    {"name": "Diablo 3", "preis": 40, "typ": "software"},
    {"name": "Windows", "preis": 50, "typ": "software"},
]


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if data.username == "test" and data.password == "test":
        access_token = jwt.encode({"user": data.username}, key="secret")
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/items/")
#@app.get("/items/", dependencies=[Depends(oauth2_scheme)])
async def get_user(q: Optional[str] = None, token: str = Depends(oauth2_scheme)):
#async def get_user(q: Optional[str] = None):
    if q:
        data = []
        for item in items:
            if item.get("typ") == q:
                data.append(item)
        return data
    return items


@app.get("/items/{item_id}")
async def get_user(item_id: int):
    return items[item_id]


@app.post("/items/", response_model=ReturnItem)
async def create_item(item: Item):
    items.append(item)
    return item


@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    items[item_id] = item
    return item


@app.delete("/items/{item_id}")
async def create_item(item_id: int):
    item = items[item_id]
    items.pop(item_id)
    return {"deleted": item}
