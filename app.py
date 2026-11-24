"""MAGYAR POLITIKA - main entry and stateless API."""
from flask import Flask, jsonify, render_template, request
from game import engine
from game import expansion

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/meta")
def meta():
    return jsonify(engine.meta())


@app.post("/api/<op>")
def api(op):
    """Run only explicitly supported game operations."""
    fn = getattr(engine, "op_" + op, None)
    if fn is None:
        return jsonify(error="Unknown game action."), 404
    try:
        data = request.get_json(silent=True) or {}
        result = fn(data)
        if op == "tick":
            result = expansion.after_tick(result)
        return jsonify(result)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return jsonify(error=f"Invalid game action: {exc}"), 400


@app.post("/api/expansion/<op>")
def expansion_api(op):
    """Handle optional classroom-simulation actions and scenario decisions."""
    fn = getattr(expansion, "op_" + op, None)
    if fn is None:
        return jsonify(error="Unknown simulation action."), 404
    try:
        data = request.get_json(silent=True) or {}
        return jsonify(fn(data))
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return jsonify(error=f"Invalid simulation action: {exc}"), 400


if __name__ == "__main__":
    app.run(debug=True)
