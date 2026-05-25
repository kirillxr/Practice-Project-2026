from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "calories.db")
MAX_WEIGHT = 15000

app = FastAPI(title="CalorieCalc")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app/templates"))

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def index(request: Request):
    con = db()
    cur = con.cursor()
    
    products = cur.execute("SELECT id, name, calories FROM products ORDER BY name").fetchall()
    totals = cur.execute("SELECT COALESCE(SUM(total_calories),0) as tc, COALESCE(SUM(total_protein),0) as tp, COALESCE(SUM(total_fat),0) as tf, COALESCE(SUM(total_carbs),0) as tcarb FROM history WHERE DATE(created_at)=DATE('now')").fetchone()
    history = cur.execute("SELECT id, product_name, weight_grams, total_calories FROM history WHERE DATE(created_at)=DATE('now') ORDER BY created_at DESC LIMIT 50").fetchall()
    con.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, "products": products,
        "total_calories": round(totals["tc"], 1), "total_protein": round(totals["tp"], 1),
        "total_fat": round(totals["tf"], 1), "total_carbs": round(totals["tcarb"], 1),
        "history": history, "success": request.query_params.get("success"),
        "error": request.query_params.get("error")
    })

@app.post("/add-from-db")
def add_db(product_id: int = Form(...), weight: float = Form(...)):
    if weight <= 0 or weight > MAX_WEIGHT:
        return RedirectResponse(url=f"/?error=Вес должен быть от 1 до {MAX_WEIGHT} грамм", status_code=303)
    
    con = db()
    prod = con.execute("SELECT name, calories, protein, fat, carbs FROM products WHERE id=?", (product_id,)).fetchone()
    if not prod:
        con.close()
        return RedirectResponse(url="/?error=Продукт не найден", status_code=303)
    
    r = weight / 100
    cal = round(prod["calories"] * r, 1)
    prot = round((prod["protein"] or 0) * r, 1)
    fat = round((prod["fat"] or 0) * r, 1)
    carb = round((prod["carbs"] or 0) * r, 1)
    
    con.execute("INSERT INTO history (product_name, weight_grams, total_calories, total_protein, total_fat, total_carbs) VALUES (?,?,?,?,?,?)", (prod["name"], weight, cal, prot, fat, carb))
    con.commit()
    con.close()
    return RedirectResponse(url=f"/?success={prod['name']} ({weight}г) + {cal} ккал", status_code=303)

@app.post("/add-manual")
def add_manual(
    product_name: str = Form(...),
    protein: float = Form(...),
    fat: float = Form(...),
    carbs: float = Form(...),
    weight: float = Form(...)
):
    if not product_name or not product_name.strip():
        return RedirectResponse(url="/?error=Введите название продукта", status_code=303)
    if weight <= 0 or weight > MAX_WEIGHT:
        return RedirectResponse(url=f"/?error=Вес должен быть от 1 до {MAX_WEIGHT} грамм", status_code=303)
    if protein < 0 or fat < 0 or carbs < 0:
        return RedirectResponse(url="/?error=БЖУ не могут быть отрицательными", status_code=303)
    
    cal_per_100 = protein*4 + fat*9 + carbs*4
    r = weight / 100
    cal = round(cal_per_100 * r, 1)
    total_protein = round(protein * r, 1)
    total_fat = round(fat * r, 1)
    total_carbs = round(carbs * r, 1)
    
    con = db()
    con.execute("INSERT INTO history (product_name, weight_grams, total_calories, total_protein, total_fat, total_carbs) VALUES (?,?,?,?,?,?)", (product_name.strip(), weight, cal, total_protein, total_fat, total_carbs))
    con.commit()
    con.close()
    return RedirectResponse(url=f"/?success={product_name.strip()} ({weight}г) + {cal} ккал", status_code=303)

@app.post("/delete-history/{hid}")
def delete_history(hid: int):
    con = db()
    if not con.execute("SELECT id FROM history WHERE id=?", (hid,)).fetchone():
        con.close()
        return RedirectResponse(url="/?error=Запись не найдена", status_code=303)
    con.execute("DELETE FROM history WHERE id=?", (hid,))
    con.commit()
    con.close()
    return RedirectResponse(url="/?success=Продукт удалён", status_code=303)

@app.get("/api/products")
def get_products():
    con = db()
    cursor = con.cursor()
    cursor.execute("SELECT id, name, calories, protein, fat, carbs FROM products ORDER BY name")
    products = [dict(row) for row in cursor.fetchall()]
    con.close()
    return JSONResponse(products)

@app.get("/api/stats")
def get_stats():
    con = db()
    cursor = con.cursor()
    cursor.execute('''
        SELECT 
            COALESCE(SUM(total_calories), 0) as total_calories,
            COALESCE(SUM(total_protein), 0) as total_protein,
            COALESCE(SUM(total_fat), 0) as total_fat,
            COALESCE(SUM(total_carbs), 0) as total_carbs
        FROM history
        WHERE DATE(created_at) = DATE('now')
    ''')
    totals = cursor.fetchone()
    con.close()
    return JSONResponse({
        "totals": dict(totals),
        "history": []
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
