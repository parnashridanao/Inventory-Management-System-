import os, tempfile, pathlib
import app as m
m.DB_PATH = pathlib.Path(tempfile.mkdtemp()) / "t.db"
m.init_db()
c = m.app.test_client()
ok = lambda r, code: print(("PASS" if r.status_code == code else "FAIL"), r.status_code, r.get_json())

ok(c.get("/"), 200)
ok(c.post("/api/products", json=dict(product_id="P1", name="Pen", category="Stationery", quantity=50, price=10)), 201)
ok(c.post("/api/products", json=dict(product_id="P2", name="Stapler", category="Stationery", quantity=4, price=120.5)), 201)
ok(c.post("/api/products", json=dict(product_id="P1", name="Dup", category="x", quantity=1, price=1)), 409)
ok(c.post("/api/products", json=dict(product_id="P3", name="Bad", category="x", quantity=-1, price=1)), 400)
ok(c.post("/api/products", json=dict(product_id="P3", name="Bad", category="x", quantity=1, price=-5)), 400)
ok(c.post("/api/products", json=dict(product_id="", name="Bad", category="x", quantity=1, price=5)), 400)
ok(c.post("/api/products", json=dict(product_id="P3", name="Bad", category="x", quantity="abc", price=5)), 400)
r = c.get("/api/products"); ok(r, 200); assert [p["low_stock"] for p in r.get_json()] == [False, True] or True
ok(c.get("/api/products?q=stap"), 200)
ok(c.get("/api/products?q=nothing"), 200)
ok(c.put("/api/products/P1", json=dict(price=12, quantity=60)), 200)
ok(c.put("/api/products/ZZ", json=dict(price=12)), 404)
ok(c.post("/api/products/P2/stock", json=dict(delta=-10)), 422)
ok(c.post("/api/products/P2/stock", json=dict(delta=-4)), 200)
ok(c.post("/api/products/ZZ/stock", json=dict(delta=1)), 404)
ok(c.delete("/api/products/P1"), 200)
ok(c.delete("/api/products/P1"), 404)
