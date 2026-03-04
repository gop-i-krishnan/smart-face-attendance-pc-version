import unittest
from pathlib import Path

from core.config import AppConfig, RecognitionConfig


class TestConfig(unittest.TestCase):
    def test_recognition_defaults(self):
        cfg = RecognitionConfig()
        self.assertEqual(cfg.img_size, (160, 160))
        self.assertGreater(cfg.sim_threshold, 0.0)
        self.assertLessEqual(cfg.sim_threshold, 1.0)
        self.assertGreaterEqual(cfg.required_frames, 1)

    def test_app_paths_are_path_objects(self):
        cfg = AppConfig()
        self.assertIsInstance(cfg.model_path, Path)
        self.assertIsInstance(cfg.gallery_path, Path)
        self.assertIsInstance(cfg.names_path, Path)
        self.assertIsInstance(cfg.attendance_dir, Path)
        self.assertIsInstance(cfg.database_path, Path)


if __name__ == "__main__":
    unittest.main()
