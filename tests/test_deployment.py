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

    def test_candidate_validation(self):
        state = engine.op_new({"party": "MDF"})
        with self.assertRaises(ValueError):
            engine.op_appoint({"state": state, "county": 0, "name": "Made-up name"})

    def test_parliament_assets_are_served(self):
        from app import app
        with app.test_client() as client:
            js = client.get("/static/parliament.js")
            css = client.get("/static/parliament.css")
            page = client.get("/")
            self.assertEqual(js.status_code, 200)
            self.assertEqual(css.status_code, 200)
            self.assertIn(b"parliament.js", page.data)
            self.assertIn(b"parliament.css", page.data)


if __name__ == "__main__":
    unittest.main()
