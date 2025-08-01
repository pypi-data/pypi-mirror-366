import unittest
import eses

class TestEses(unittest.TestCase):
    def test_donate(self):
        result = eses.donate()
        self.assertIn('status', result)
        
    def test_proxy_management(self):
        initial_count = len(eses.get_proxy_list())
        eses.add_proxy("http://testproxy.example.com")
        self.assertEqual(len(eses.get_proxy_list()), initial_count + 1)
        eses.clear_proxies()
        self.assertEqual(len(eses.get_proxy_list()), 0)

if __name__ == '__main__':
    unittest.main()