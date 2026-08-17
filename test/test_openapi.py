import unittest

from testing_framework.testers.openapi import resolve_ref, validate_schema


class OpenApiTests(unittest.TestCase):
    def setUp(self):
        self.spec = {
            "components": {
                "schemas": {
                    "Health": {
                        "type": "object",
                        "required": ["status", "count"],
                        "properties": {
                            "status": {"type": "string", "enum": ["healthy"]},
                            "count": {"type": "integer"},
                        },
                    }
                }
            }
        }

    def test_resolves_local_reference(self):
        schema = resolve_ref(self.spec, {"$ref": "#/components/schemas/Health"})
        self.assertEqual(schema["type"], "object")

    def test_valid_payload_has_no_errors(self):
        errors = validate_schema({"status": "healthy", "count": 2}, {"$ref": "#/components/schemas/Health"}, self.spec, "$")
        self.assertEqual(errors, [])

    def test_reports_required_type_and_enum_errors(self):
        errors = validate_schema({"status": "down", "count": "2"}, {"$ref": "#/components/schemas/Health"}, self.spec, "$")
        self.assertTrue(any("enum" in item for item in errors))
        self.assertTrue(any("esperado integer" in item for item in errors))


if __name__ == "__main__":
    unittest.main()

