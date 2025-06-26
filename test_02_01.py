from pathlib import Path

import easyocr

from test_01 import IN_DIR  # 이전에 작성한 모듈을 불러옵니다.


def read_text(path: Path) -> list:
    reader = easyocr.Reader(["ko", "en"], verbose=False)
    return reader.readtext(path.read_bytes())

if __name__ == "__main__":
    path = IN_DIR / "engImg_01.png"
    reader = easyocr.Reader(["ko", "en"], verbose = False)
    parsed = reader.readtext(path.read_bytes())
    print(parsed)