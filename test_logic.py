import unittest
import os

class TestAppIntegrity(unittest.TestCase):
    def test_config_exists(self):
        self.assertTrue(os.path.exists('module_1/config.json'), "Файл конфігурації має бути!")

    def test_logs_folder(self):
        self.assertTrue(os.path.exists('logs'), "Папка логів має бути створена автоматично")

if __name__ == '__main__':
    unittest.main()