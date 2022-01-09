from fastapi import FastAPI, Query
from enum import Enum
from pydantic import BaseModel, Field
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

@app.get("/items/")
async def get_user(q: Optional[str] = None):
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
