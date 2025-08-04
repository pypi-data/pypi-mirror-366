import os
from pathlib import Path

def collect_files(base_dir: str, extra_files: list[str]) -> list[Path]:
    base_path = Path(base_dir)
    py_files = list(base_path.rglob("*.md"))
    extra_paths = [Path(f).resolve() for f in extra_files if Path(f).exists()]
    return py_files + extra_paths

def generate_documentation_text(files: list[Path]) -> str:
    parts = []
    for file_path in sorted(files, key=str):
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin1")

        parts.append(
            "------------------------------------------------------------------------------------------\n"
            f"file: {file_path}\n"
            "------------------------------------------------------------------------------------------\n"
            f"{content}\n\n"
        )
    return "\n".join(parts)

def main():
    base_dir = "docs"
    extra_files = ["README.md", "mkdocs.yml", ".readthedocs.yml"]  # agregá más si querés

    files = collect_files(base_dir, extra_files)
    final_text = generate_documentation_text(files)

    with open("dump.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"Documento generado con {len(files)} archivos: dump.txt")

if __name__ == "__main__":
    main()
