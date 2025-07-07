from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class AuthService:
    def __init__(self):
        self.users = load_json("users.json")

    def login(self, username, password):
        return self.users.get(username) == password

    def register(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        save_json("users.json", self.users)
        return True

class CatalogService:
    def __init__(self):
        self.products = load_json("products.json")

    def get_all_products(self):
        return self.products

    def add_product(self, product_id, name, price):
        self.products[product_id] = {"name": name, "price": price}
        save_json("products.json", self.products)

class CartService:
    def __init__(self):
        self.carts = load_json("carts.json")

    def get_cart(self, user_id):
        return self.carts.get(user_id, {})

    def add_to_cart(self, user_id, product_id, quantity):
        if user_id not in self.carts:
            self.carts[user_id] = {}
        cart = self.carts[user_id]
        cart[product_id] = cart.get(product_id, 0) + quantity
        save_json("carts.json", self.carts)

class ApiGateway:
    def __init__(self):
        self.auth = AuthService()
        self.catalog = CatalogService()
        self.cart = CartService()

    def login_user(self, username, password):
        return self.auth.login(username, password)

    def register_user(self, username, password):
        return self.auth.register(username, password)

    def get_products(self):
        return self.catalog.get_all_products()

    def add_product(self, product_id, name, price):
        self.catalog.add_product(product_id, name, price)

    def get_cart(self, user_id):
        return self.cart.get_cart(user_id)

    def add_to_cart(self, user_id, product_id, quantity):
        self.cart.add_to_cart(user_id, product_id, quantity)

#ui-interface
app = FastAPI()
gateway = ApiGateway()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/catalog", response_class=HTMLResponse)
async def catalog(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if gateway.login_user(username, password):
        return templates.TemplateResponse("index.html", {"request": request, "username": username})
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if gateway.register_user(username, password):
        return templates.TemplateResponse("index.html", {"request": request, "username": username})
    raise HTTPException(status_code=400, detail="Пользователь уже существует")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/add_product")
async def add_product(product_id: str = Form(...), name: str = Form(...), price: int = Form(...)):
    gateway.add_product(product_id, name, price)
    return {"status": "Товар добавлен"}

@app.get("/products")
async def get_products():
    return gateway.get_products()

@app.post("/add_to_cart")
async def add_to_cart(user_id: str = Form(...), product_id: str = Form(...), quantity: int = Form(...)):
    gateway.add_to_cart(user_id, product_id, quantity)
    return {"status": "Добавлено в корзину"}

@app.get("/cart/{user}")
async def get_cart(user: str):
    raw_cart = gateway.get_cart(user)
    products = gateway.get_products()
    enriched_cart = {
        pid: {"name": products[pid]["name"], "quantity": qty}
        for pid, qty in raw_cart.items() if pid in products
    }
    return enriched_cart