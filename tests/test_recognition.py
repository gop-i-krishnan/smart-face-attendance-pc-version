import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from core.config import AppConfig, RecognitionConfig
from core.recognition import FaceRecognitionEngine


class FakeInterpreter:
    def __init__(self, model_path):
        self.model_path = model_path
        self.embedding = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)

    def allocate_tensors(self):
        return None

    def get_input_details(self):
        return [{"dtype": np.float32, "index": 0, "quantization": (0.0, 0)}]

    def get_output_details(self):
        return [{"dtype": np.float32, "index": 0, "quantization": (0.0, 0)}]

    def set_tensor(self, index, value):
        self.last_input = (index, value)

    def invoke(self):
        return None

    def get_tensor(self, index):
        return self.embedding


class FakeCascade:
    def __init__(self, _):
        self.faces = [(10, 10, 30, 30)]

    def detectMultiScale(self, gray, scale, neighbors):
        return self.faces


class TestFaceRecognitionEngine(unittest.TestCase):
    def _build_engine(self, temp_dir: str, required_frames: int = 2):
        gallery = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        )
        gallery_path = Path(temp_dir) / "gallery.npy"
        names_path = Path(temp_dir) / "names.txt"
        np.save(gallery_path, gallery)
        names_path.write_text("Alice\nBob\n", encoding="utf-8")

        app_cfg = AppConfig(
            model_path=Path(temp_dir) / "model.tflite",
            gallery_path=gallery_path,
            names_path=names_path,
            attendance_dir=Path(temp_dir) / "logs",
        )
        rec_cfg = RecognitionConfig(required_frames=required_frames, sim_threshold=0.5)
        return FaceRecognitionEngine(app_cfg, rec_cfg)

    @patch("core.recognition.cv2.CascadeClassifier", FakeCascade)
    @patch("core.recognition.tf.lite.Interpreter", FakeInterpreter)
    def test_marks_present_after_required_frames(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            engine = self._build_engine(tmp_dir, required_frames=2)
            frame = np.zeros((120, 120, 3), dtype=np.uint8)

            _, newly_marked_first = engine.process_frame(frame.copy())
            _, newly_marked_second = engine.process_frame(frame.copy())
            _, newly_marked_third = engine.process_frame(frame.copy())

            self.assertEqual(newly_marked_first, [])
            self.assertEqual(newly_marked_second, ["Alice"])
            self.assertEqual(newly_marked_third, [])
            self.assertEqual(engine.attendance["Alice"], "PRESENT")

    @patch("core.recognition.cv2.CascadeClassifier", FakeCascade)
    @patch("core.recognition.tf.lite.Interpreter", FakeInterpreter)
    def test_unknown_face_when_similarity_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            engine = self._build_engine(tmp_dir, required_frames=1)
            frame = np.zeros((120, 120, 3), dtype=np.uint8)
            engine.recognition_config = RecognitionConfig(
                required_frames=1,
                sim_threshold=0.99,
            )
            engine.interpreter.embedding = np.array(
                [[0.0, 0.0, 1.0, 0.0]], dtype=np.float32
            )

            _, newly_marked = engine.process_frame(frame.copy())

            self.assertEqual(newly_marked, [])
            self.assertEqual(engine.attendance["Alice"], "ABSENT")
            self.assertEqual(engine.attendance["Bob"], "ABSENT")


if __name__ == "__main__":
    unittest.main()
