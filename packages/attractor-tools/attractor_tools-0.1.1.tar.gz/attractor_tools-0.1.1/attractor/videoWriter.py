import numpy as np
import cv2

class VideoFileWriter:
    def __init__(self, filename: str, fps: int = 30):
        self.filename = filename
        self.fps = fps
        self.writer: cv2.VideoWriter | None = None
        self.frame_size: tuple[int, int] | None = None
        self.is_color = None
        self.initialized = False

    def _init_writer(self, frame_shape):
        self.frame_size = (frame_shape[1], frame_shape[0])
        self.is_color = len(frame_shape) == 3
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(self.filename, fourcc, self.fps, self.frame_size, isColor=True)
        self.initialized = True

    def add_frame(self, frame: np.ndarray, a: float | None = None, b: float | None = None):
        if not self.initialized:
            self._init_writer(frame.shape)

        if (frame.shape[1], frame.shape[0]) != self.frame_size:
            return

        if len(frame.shape) == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        if not self.is_color and len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        if a is not None and b is not None:
            text = f"a = {a:.4f}, b = {b:.4f}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)

        if self.writer is None:
            return
        self.writer.write(frame)

    def save(self):
        if self.writer is not None:
            self.writer.release()
            print(f"path: '{self.filename}'")

def count_significant_pixels(frame: np.ndarray, threshold: int = 20, min_pixels: int = 100, verbose = False):
    # Umwandeln in Graustufen für einfacheren Vergleich
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Pixel, die sich von der häufigsten Farbe unterscheiden
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    dominant_value = np.argmax(hist)
    mask = np.abs(gray.astype(int) - dominant_value) > threshold
    count = np.count_nonzero(mask)
    result = count >= min_pixels
    if verbose:
        print(f"non-zero values ({threshold=}): {count} ")
    return result

def is_mostly_uniform(frame: np.ndarray, threshold: float = 5.0, verbose = False) -> bool:
    variance = np.var(frame)
    result = bool(variance < threshold)
    if verbose:
        print(f"frame variance: {round(variance)}")
    return result

