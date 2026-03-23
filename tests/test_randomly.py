import unittest
import hyrandom

class Testhyrandom(unittest.TestCase):
    
    def test_random_bounds(self):
        val = hyrandom.random()
        self.assertTrue(0.0 <= val < 1.0)
        
    def test_randint(self):
        val = hyrandom.randint(10, 20)
        self.assertTrue(10 <= val <= 20)

    def test_choice(self):
        options = ['A', 'B', 'C']
        self.assertIn(hyrandom.choice(options), options)

    def test_token_urlsafe(self):
        token = hyrandom.token_urlsafe(32)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 32)
        
    def test_security_exceptions(self):
        with self.assertRaises(NotImplementedError):
            hyrandom.getstate()

if __name__ == '__main__':
    unittest.main()