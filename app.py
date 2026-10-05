import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, render_template, g

DB_PATH = Path(__file__).with_name("inventory.db")
LOW_STOCK_LIMIT = 10

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS products (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL UNIQUE,
                name       TEXT NOT NULL,
                category   TEXT NOT NULL,
                quantity   INTEGER NOT NULL CHECK (quantity >= 0),
                price      REAL NOT NULL CHECK (price >= 0)
            )"""
        )


def row_to_dict(row):
    d = dict(row)
    d["low_stock"] = d["quantity"] <= LOW_STOCK_LIMIT
    return d


def parse_product(data, partial=False):
    """Validate JSON body. Returns (clean_dict, error_message)."""
    clean = {}
    for field in ("product_id", "name", "category"):
        if field in data or not partial:
            value = str(data.get(field, "")).strip()
            if not value:
                return None, f"{field.replace('_', ' ').title()} is required."
            clean[field] = value
    if "quantity" in data or not partial:
        try:
            qty = int(str(data.get("quantity")).strip())
        except (TypeError, ValueError):
            return None, "Quantity must be a whole number."
        if qty < 0:
            return None, "Quantity cannot be negative."
        clean["quantity"] = qty
    if "price" in data or not partial:
        try:
            price = float(str(data.get("price")).strip())
        except (TypeError, ValueError):
            return None, "Price must be a number."
        if price < 0 or price != price or price == float("inf"):
            return None, "Price cannot be negative."
        clean["price"] = round(price, 2)
    return clean, None


def error(message, status=400):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return render_template("index.html", low_limit=LOW_STOCK_LIMIT)


@app.get("/api/products")
def list_products():
    q = request.args.get("q", "").strip()
    sql, args = "SELECT * FROM products", []
    if q:
        sql += " WHERE name LIKE ? OR product_id LIKE ? OR category LIKE ?"
        args = [f"%{q}%"] * 3
    sql += " ORDER BY name COLLATE NOCASE"
    rows = get_db().execute(sql, args).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.post("/api/products")
def add_product():
    data, err = parse_product(request.get_json(silent=True) or {})
    if err:
        return error(err)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO products (product_id, name, category, quantity, price)"
            " VALUES (:product_id, :name, :category, :quantity, :price)",
            data,
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error(f"Product ID '{data['product_id']}' already exists.", 409)
    row = db.execute("SELECT * FROM products WHERE product_id = ?", (data["product_id"],)).fetchone()
    return jsonify(row_to_dict(row)), 201


@app.put("/api/products/<pid>")
def update_product(pid):
    body = request.get_json(silent=True) or {}
    body.pop("product_id", None)  # ID is fixed after creation
    data, err = parse_product(body, partial=True)
    if err:
        return error(err)
    if not data:
        return error("Nothing to update.")
    db = get_db()
    sets = ", ".join(f"{k} = :{k}" for k in data)
    cur = db.execute(f"UPDATE products SET {sets} WHERE product_id = :pid", {**data, "pid": pid})
    db.commit()
    if cur.rowcount == 0:
        return error("Product not found.", 404)
    row = db.execute("SELECT * FROM products WHERE product_id = ?", (pid,)).fetchone()
    return jsonify(row_to_dict(row))


@app.post("/api/products/<pid>/stock")
def adjust_stock(pid):
    try:
        delta = int(str((request.get_json(silent=True) or {}).get("delta")).strip())
    except (TypeError, ValueError):
        return error("Change must be a whole number.")
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE product_id = ?", (pid,)).fetchone()
    if row is None:
        return error("Product not found.", 404)
    new_qty = row["quantity"] + delta
    if new_qty < 0:
        return error(f"Only {row['quantity']} in stock; cannot remove {abs(delta)}.", 422)
    db.execute("UPDATE products SET quantity = ? WHERE product_id = ?", (new_qty, pid))
    db.commit()
    row = db.execute("SELECT * FROM products WHERE product_id = ?", (pid,)).fetchone()
    return jsonify(row_to_dict(row))


@app.delete("/api/products/<pid>")
def delete_product(pid):
    db = get_db()
    cur = db.execute("DELETE FROM products WHERE product_id = ?", (pid,))
    db.commit()
    if cur.rowcount == 0:
        return error("Product not found.", 404)
    return jsonify({"deleted": pid})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
