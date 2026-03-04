from __future__ import annotations

import time
from collections import defaultdict

import cv2
import numpy as np
import tensorflow as tf

from core.config import AppConfig, RecognitionConfig


class FaceRecognitionEngine:
    def __init__(self, app_config: AppConfig, recognition_config: RecognitionConfig):
        self.app_config = app_config
        self.recognition_config = recognition_config

        self.interpreter = tf.lite.Interpreter(model_path=str(app_config.model_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.gallery = np.load(app_config.gallery_path).astype(np.float32)
        self.gallery = self.gallery / (
            np.linalg.norm(self.gallery, axis=1, keepdims=True) + 1e-10
        )

        with app_config.names_path.open("r", encoding="utf-8") as file:
            self.names = [line.strip() for line in file.readlines() if line.strip()]

        self.attendance = {name: "ABSENT" for name in self.names}
        self.frame_count = defaultdict(int)
        self.last_seen: dict[str, float] = {}

    def _run_embedding(self, face_bgr: np.ndarray) -> np.ndarray:
        img = cv2.resize(face_bgr, self.recognition_config.img_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        img = (img - 127.5) / 128.0
        inp = np.expand_dims(img, axis=0)

        if self.input_details["dtype"] == np.int8:
            scale, zero = self.input_details["quantization"]
            inp = np.round(inp / scale + zero).astype(np.int8)
            inp = np.clip(inp, -128, 127)

        self.interpreter.set_tensor(self.input_details["index"], inp)
        self.interpreter.invoke()
        emb = self.interpreter.get_tensor(self.output_details["index"]).squeeze()

        if self.output_details["dtype"] == np.int8:
            scale, zero = self.output_details["quantization"]
            emb = (emb.astype(np.float32) - zero) * scale

        return emb / (np.linalg.norm(emb) + 1e-10)

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, list[str]]:
        newly_marked: list[str] = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            mh = int(h * self.recognition_config.margin)
            mw = int(w * self.recognition_config.margin)
            y1 = max(0, y - mh)
            y2 = min(frame.shape[0], y + h + mh)
            x1 = max(0, x - mw)
            x2 = min(frame.shape[1], x + w + mw)

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            emb = self._run_embedding(face)
            sims = self.gallery @ emb
            best_idx = int(np.argmax(sims))
            best_score = float(sims[best_idx])

            if best_score > self.recognition_config.sim_threshold:
                name = self.names[best_idx]
                current_time = time.time()

                if name in self.last_seen and (
                    current_time - self.last_seen[name]
                    > self.recognition_config.timeout_seconds
                ):
                    self.frame_count[name] = 0

                self.frame_count[name] += 1
                self.last_seen[name] = current_time

                if (
                    self.frame_count[name] >= self.recognition_config.required_frames
                    and self.attendance[name] != "PRESENT"
                ):
                    self.attendance[name] = "PRESENT"
                    newly_marked.append(name)

                label = f"{name} ({best_score:.2f})"
                color = (15, 118, 110)
            else:
                label = f"Unknown ({best_score:.2f})"
                color = (185, 28, 28)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        y0 = frame.shape[0] - 100
        for person, status in self.attendance.items():
            status_color = (15, 118, 110) if status == "PRESENT" else (249, 115, 22)
            cv2.putText(
                frame,
                f"{person}: {status}",
                (20, y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                status_color,
                2,
            )
            y0 += 25

        return frame, newly_marked
