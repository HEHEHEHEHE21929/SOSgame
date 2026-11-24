"""Flask app: serves the page and a tiny stateless JSON API (the browser keeps the game state)."""
from flask import Flask, jsonify, render_template, request
from game import engine

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/meta")
def meta():
    return jsonify(engine.meta())

@app.post("/api/<op>")
def api(op):
    fn = getattr(engine, "op_" + op, None)   # only functions named op_* are reachable
    if not fn:
        return jsonify(error="unknown action"), 404
    return jsonify(fn(request.get_json(force=True) or {}))

if __name__ == "__main__":
    app.run(debug=True)
