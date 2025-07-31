import os
import random
import string


from .utils import ensure_folder

from .setup_logger import setup_logger  # <- import once

logger = setup_logger(__name__) 

LANG_EXT = {
    "python": "py",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "javascript": "js",
    "typescript": "ts"
}


def generate_code(lang: str, index: int, uniq: str) -> str:
    if lang == "python":
        return f"name_{index} = '{uniq}'\nprint('Hello from Python:', name_{index})"

    elif lang == "java":
        return (
            f"public class Code_{index} {{\n"
            f"  public static void main(String[] args) {{\n"
            f"    String name = \"{uniq}\";\n"
            f"    System.out.println(\"Hello from Java: \" + name);\n"
            f"  }}\n}}"
        )

    elif lang == "cpp":
        return (
            f"#include <bits/stdc++.h>\nusing namespace std;\n\n"
            f"int main() {{\n"
            f"    string name = \"{uniq}\";\n"
            f"    cout << \"Hello from C++: \" << name << endl;\n"
            f"    return 0;\n}}"
        )

    elif lang == "c":
        return (
            f"#include <stdio.h>\n\n"
            f"int main() {{\n"
            f"    char name[] = \"{uniq}\";\n"
            f"    printf(\"Hello from C: %s\\n\", name);\n"
            f"    return 0;\n}}"
        )

    elif lang == "javascript":
        return f"let name_{index} = '{uniq}';\nconsole.log('Hello from JavaScript:', name_{index});"

    elif lang == "typescript":
        return f"let name_{index}: string = '{uniq}';\nconsole.log('Hello from TypeScript:', name_{index});"

    else:
        return f"// Unsupported language: {lang}"


def fetch_code(config: dict, folder: str):
    """
    config = {
        "python": 2,
        "java": 3,
        "cpp": 1,
        "c": 2,
        "javascript": 1,
        "typescript": 2
    }
    Returns: list of saved file paths
    """
    ensure_folder(folder)
    saved_paths = []

    for lang, count in config.items():
        if lang not in LANG_EXT:
            logger.warning(f"Unsupported language: {lang}")
            continue

        ext = LANG_EXT[lang]
        for i in range(count):
            uniq = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            filename = f"code_{lang}_{i+1}_{uniq}.{ext}"
            path = os.path.join(folder, filename)
            try:
                code = generate_code(lang, i, uniq)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                logger.info(f"Saved: {path}")
                saved_paths.append(path)
            except Exception as e:
                logger.error(f"Failed to save {lang} file: {e}")

    return saved_paths
