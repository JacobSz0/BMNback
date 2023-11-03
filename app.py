from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json

def create_connection():
    connection = sqlite3.connect("bmn.db")
    return connection

def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bmns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bmn_data TEXT NOT NULL
    )
    """)
    connection.commit()
    connection.close()

create_table()  # Call this function to create the table

class BMNCreate(BaseModel):
    title: str
    lengthy_description: str
    image_1: str
    image_2: str
    date_watched: str

class BMN(BMNCreate):
    id: int

def get_all_bmns():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, bmn_data FROM bmns")
    bmns = cursor.fetchall()
    connection.close()

    bmns_list = []
    for bmn in bmns:
        bmn_dict = {"id": bmn[0], **json.loads(bmn[1])}
        bmns_list.append(bmn_dict)

    return bmns_list

def create_bmn(bmn: BMNCreate):
    connection = create_connection()
    cursor = connection.cursor()
    bmn_data = json.dumps({"title": bmn.title, "lengthy_description": bmn.lengthy_description, "image_1": bmn.image_1, "image_2": bmn.image_2, "date_watched": bmn.date_watched, })
    cursor.execute("INSERT INTO bmns (bmn_data) VALUES (?)", (bmn_data,))
    connection.commit()
    bmn_id = cursor.lastrowid
    connection.close()
    return bmn_id

def get_bmn_by_id(bmn_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT bmn_data FROM bmns WHERE id = ?", (bmn_id,))
    bmn = cursor.fetchone()
    connection.close()
    if bmn:
        return json.loads(bmn[0])
    else:
        raise HTTPException(status_code=404, detail="BMN not found")

def update_bmn(bmn_id: int, bmn: BMNCreate):
    connection = create_connection()
    cursor = connection.cursor()
    bmn_data = json.dumps({"title": bmn.title, "lengthy_description": bmn.lengthy_description, "image_1": bmn.image_1, "image_2": bmn.image_2, "date_watched": bmn.date_watched, })
    cursor.execute("UPDATE bmns SET bmn_data = ? WHERE id = ?", (bmn_data, bmn_id))
    connection.commit()
    connection.close()

def delete_bmn(bmn_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM bmns WHERE id = ?", (bmn_id,))
    connection.commit()
    connection.close()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the CRUD API"}

@app.get("/bmns/")
def get_all_bmns_endpoint():
    all_bmns = get_all_bmns()
    return {"bmns": all_bmns}

@app.post("/bmns/")
def create_bmn_endpoint(bmn: BMNCreate):
    bmn_id = create_bmn(bmn)
    return {"id": bmn_id, "title": bmn.title, "lengthy_description": bmn.lengthy_description, "image_1": bmn.image_1, "image_2": bmn.image_2, "date_watched": bmn.date_watched, }

@app.get("/bmns/{bmn_id}")
def get_bmn(bmn_id: int):
    bmn = get_bmn_by_id(bmn_id)
    return {"bmn": bmn}

@app.put("/bmns/{bmn_id}")
def update_bmn_endpoint(bmn_id: int, bmn: BMNCreate):
    get_bmn_by_id(bmn_id)
    update_bmn(bmn_id, bmn)
    return {"message": "BMN updated successfully", "id": bmn_id, "content": bmn}

@app.delete("/bmns/{bmn_id}")
def delete_bmn_endpoint(bmn_id: int):
    get_bmn_by_id(bmn_id)
    delete_bmn(bmn_id)
    return {"message": "BMN deleted successfully"}
