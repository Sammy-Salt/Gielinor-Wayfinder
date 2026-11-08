import unittest

from validate_world_objects import validate


class WorldObjectValidationTests(unittest.TestCase):
    def sample(self):
        return {
            "schemaVersion": 1,
            "region": {"regionId": 12850, "x": 50, "y": 50},
            "objectCount": 1,
            "objects": [{
                "objectId": 100, "name": "Lumbridge object",
                "x": 3222, "y": 3218, "plane": 0,
                "shape": 10, "orientation": 0, "layer": "scenery"
            }]
        }

    def test_valid_region(self):
        self.assertEqual(validate(self.sample()), [])

    def test_rejects_wrong_region(self):
        data = self.sample()
        data["objects"][0]["x"] = 3136
        self.assertIn("objects[0] is outside the declared region", validate(data))

    def test_rejects_duplicate_placement(self):
        data = self.sample()
        data["objects"].append(dict(data["objects"][0]))
        data["objectCount"] = 2
        self.assertTrue(any("duplicates an earlier placement" in e for e in validate(data)))

    def test_rejects_wrong_count(self):
        data = self.sample()
        data["objectCount"] = 9
        self.assertIn("objectCount does not match objects length", validate(data))


if __name__ == "__main__":
    unittest.main()
