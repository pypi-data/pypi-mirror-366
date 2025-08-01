import os
import random
import string
import json
import uuid
from datetime import datetime, timedelta

from .utils import ensure_folder

from .setup_logger import setup_logger

logger = setup_logger(__name__) 


def fetch_json(config: dict, folder: str):
    """
    config = {
        "schema": { ... },
        "min_data_per_file": 5,
        "max_data_per_file": 15,
        "count": 5
    }
    Returns list of saved .json file paths
    """
    ensure_folder(folder)

    count = config.get("count", 1)
    min_data = config.get("min_data_per_file", 1)
    max_data = config.get("max_data_per_file", min_data)

    if max_data < min_data:
        logger.warning("max_data_per_file < min_data_per_file. Adjusting...")
        max_data = min_data

    schema = config.get("schema", {
        "id": "uuid",
        "username": "str",
        "email": "email",
        "verified": "bool"
    })

    def generate_value(type_str):
        if type_str == "int":
            return random.randint(1, 100)
        elif type_str == "float":
            return round(random.uniform(0, 100), 2)
        elif type_str == "str":
            return ''.join(random.choices(string.ascii_letters, k=8))
        elif type_str == "bool":
            return random.choice([True, False])
        elif type_str == "email":
            name = ''.join(random.choices(string.ascii_lowercase, k=6))
            return f"{name}@example.com"
        elif type_str == "uuid":
            return str(uuid.uuid4())
        elif type_str == "date":
            start = datetime(2020, 1, 1)
            rand_date = start + timedelta(days=random.randint(0, 1500))
            return rand_date.strftime("%Y-%m-%d")
        else:
            logger.warning(f"Unsupported type: {type_str}")
            return f"Unsupported({type_str})"

    saved_paths = []

    for i in range(count):
        num_records = random.randint(min_data, max_data)
        records = []

        for _ in range(num_records):
            record = {field: generate_value(dtype) for field, dtype in schema.items()}
            records.append(record)

        filename = f"data_{i+1}.json"
        dest = os.path.join(folder, filename)

        try:
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4)
            logger.info(f"Saved {num_records} records to {dest}")
            saved_paths.append(dest)
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")

    return saved_paths
