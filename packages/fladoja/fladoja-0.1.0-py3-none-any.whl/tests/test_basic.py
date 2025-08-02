import unittest
from fladoja import Fladoja

class TestFladoja(unittest.TestCase):
    def setUp(self):
        self.app = Fladoja("TestApp")
        
    def test_route_registration(self):
        @self.app.site('/test')
        def test_route(params):
            return "OK"
            
        self.assertIn('/test', self.app.routes)
        
    def test_template_rendering(self):
        result = self.app.file_template("missing.html")
        self.assertIn("not found", result)

if __name__ == "__main__":
    unittest.main()