import unittest
from game import engine, expansion


class DeploymentTests(unittest.TestCase):
    def test_candidate_roster_is_available_to_metadata(self):
        metadata = engine.meta()
        self.assertIn("mp_candidates", metadata)
        self.assertIn("Antall József", metadata["mp_candidates"])

    def test_application_import_and_new_game(self):
        from app import app
        with app.test_client() as client:
            self.assertEqual(client.get("/api/meta").status_code, 200)
            response = client.post("/api/new", json={"party": "MDF"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["party"], "MDF")

    def test_candidate_recruitment_adds_named_person_to_selected_county(self):
        state = engine.op_new({"party": "MDF"})
        state["money"] = 20
        updated = engine.op_appoint({"state": state, "county": 0, "name": "Antall József"})
        self.assertEqual(updated["county_mps"]["0"], "Antall József")
        self.assertEqual(updated["money"], 18)

    def test_candidate_validation(self):
        state = engine.op_new({"party": "MDF"})
        with self.assertRaises(ValueError):
            engine.op_appoint({"state": state, "county": 0, "name": "Made-up name"})

    def test_advisor_selection_returns_a_persistable_state(self):
        state = engine.op_new({"party": "MDF"})
        updated = engine.op_mentor({"state": state, "mentor": "antall"})
        self.assertEqual(updated["mentor"], "antall")

    def test_playability_assets_are_served_and_observer_loop_is_guarded(self):
        from app import app
        from pathlib import Path
        source = Path("static/playability.js").read_text(encoding="utf-8")
        self.assertIn("card.dataset.rendered!==html", source)
        self.assertIn("report.dataset.rendered!==html", source)
        with app.test_client() as client:
            self.assertEqual(client.get("/static/playability.js").status_code, 200)
            self.assertEqual(client.get("/static/playability.css").status_code, 200)
            self.assertIn(b"playability.js", client.get("/").data)

    def test_corrupt_choices_cost_public_money_and_reduce_trust(self):
        state = engine.op_new({"party": "MDF"})
        state.update(inpower=True, money=50)
        updated = expansion.op_corrupt({"state": state, "action": "holiday"})
        self.assertEqual(updated["money"], 38)
        self.assertLess(updated["trust"], 100)
        self.assertEqual(updated["corruption"], 1)

    def test_corrupt_choices_are_unavailable_outside_government(self):
        state = engine.op_new({"party": "MDF"})
        updated = expansion.op_corrupt({"state": state, "action": "holiday"})
        self.assertEqual(updated["money"], state["money"])
        self.assertIn("only while", updated["flash"])

    def test_fictional_emergency_schedule_and_humanitarian_choice(self):
        state = engine.op_new({"party": "MDF"})
        state["m"] = (2029 - 1991) * 12 + 5
        event_state = expansion.after_tick(state)
        self.assertEqual(event_state["event"]["id"], "scenario-nuclear")
        updated = expansion.op_emergency_choice({"state": event_state, "i": 0})
        self.assertIsNone(updated["event"])
        self.assertIn("fictional classroom scenario", updated["flash"])

    def test_expansion_endpoints_are_served(self):
        from app import app
        state = engine.op_new({"party": "MDF"})
        with app.test_client() as client:
            response = client.post("/api/expansion/corrupt", json={"state": {**state, "inpower": True, "money": 50}, "action": "holiday"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["corruption"], 1)
            self.assertEqual(client.get("/static/enhancements.js").status_code, 200)


if __name__ == "__main__":
    unittest.main()
