import os
import random
import string

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .utils import ensure_folder

from .setup_logger import setup_logger 

logger = setup_logger(__name__) 


def _parse_size(size_str):
    size_str = size_str.lower().strip()
    if size_str.endswith("kb"):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith("mb"):
        return int(float(size_str[:-2]) * 1024 * 1024)
    else:
        return int(size_str)


def generate_random_text(paragraphs=10, max_line_length=80):
    lorem = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip."
    )
    return "\n".join([lorem[:random.randint(60, max_line_length)] for _ in range(paragraphs)])


def fetch_pdfs(config: dict, folder: str):
    """
    config = {
        "count": 3,
        "max_size": "5mb",
        "min_size": "100kb"
    }
    """
    ensure_folder(folder)

    count = config.get("count", 1)
    min_size = _parse_size(config.get("min_size", "0kb"))
    max_size = _parse_size(config.get("max_size", "5mb"))

    saved_paths = []
    attempts = 0

    while len(saved_paths) < count and attempts < count * 5:
        attempts += 1

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        text = c.beginText(50, 800)

        paragraph_count = random.randint(50, 500)
        for _ in range(paragraph_count):
            line = generate_random_text(paragraphs=1)
            text.textLine(line)

        c.drawText(text)
        c.showPage()
        c.save()

        content = buffer.getvalue()
        size = len(content)

        if min_size <= size <= max_size:
            file_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            filename = f"pdf_{len(saved_paths) + 1}_{file_id}.pdf"
            path = os.path.join(folder, filename)
            with open(path, "wb") as f:
                f.write(content)
            logger.info(f"Saved PDF: {path} ({round(size / 1024, 2)} KB)")
            saved_paths.append(path)
        else:
            logger.warning(f"Rejected PDF (size {size} bytes), please try reducing(preffered) or increasing size limits.")

    return saved_paths
