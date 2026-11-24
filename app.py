"""Stateless Flask API for MAGYAR POLITIKA."""
from flask import Flask, jsonify, render_template, request

from game.data import COUNTIES, PARTIES, POLICIES, CAMPAIGNS, MENTORS
from game.engine import new_game, advance_month, campaign, enact_policy, resolve_event, election

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/config")
def config():
    return jsonify({
        "parties": PARTIES,
        "counties": COUNTIES,
        "policies": POLICIES,
        "campaigns": CAMPAIGNS,
        "mentors": MENTORS,
    })


@app.post("/api/new")
def create_game():
    body = request.get_json(force=True)
    return jsonify(new_game(body.get("party", "MDF"), body.get("leader", "")))


@app.post("/api/advance")
def advance():
    body = request.get_json(force=True)
    state = body.get("state", {})
    months = max(1, min(int(body.get("months", 1)), 4))
    for _ in range(months):
        state = advance_month(state)
    return jsonify(state)


@app.post("/api/campaign")
def run_campaign():
    body = request.get_json(force=True)
    return jsonify(campaign(body["state"], body["action"], body.get("county")))


@app.post("/api/policy")
def run_policy():
    body = request.get_json(force=True)
    return jsonify(enact_policy(body["state"], body["policy"]))


@app.post("/api/event")
def run_event():
    body = request.get_json(force=True)
    return jsonify(resolve_event(body["state"], body.get("choice", 0)))


@app.post("/api/election")
def run_election():
    body = request.get_json(force=True)
    return jsonify(election(body["state"]))


if __name__ == "__main__":
    app.run(debug=True)
