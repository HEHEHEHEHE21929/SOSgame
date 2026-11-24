import unittest
from game import engine


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


if __name__ == "__main__":
    unittest.main()
