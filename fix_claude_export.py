import re
import shutil
from pathlib import Path

ROOT = Path(".").resolve()

# 1) Переименовываем файлы типа "main.py - ..." -> "main.py"
def fix_names(base: Path):
    for p in list(base.rglob("*")):
        if not p.is_file():
            continue
        m = re.match(r"^(.*?\.(py|txt|md|yml|yaml|js|jsx|ts|tsx|css|html))\s+-\s+.+$", p.name)
        if m:
            new_name = m.group(1)
            new_path = p.with_name(new_name)
            if new_path.exists():
                # если уже есть такой файл — оставим существующий, а этот добавим суффикс
                new_path = p.with_name(new_name.replace(".", f"__dup__."))
            print(f"RENAME: {p} -> {new_path}")
            p.rename(new_path)

# 2) Переносим ключевые файлы из docs/Create_security_protocols в правильные места
def move_known_docs():
    docs_dir = ROOT / "docs" / "Create_security_protocols"
    if not docs_dir.exists():
        return

    mapping = {
        "requirements.txt": ROOT / "backend" / "requirements.txt",
        ".env.example": ROOT / ".env.example",
        "docker-compose.yml": ROOT / "docker-compose.yml",
        "README.md": ROOT / "README.md",
        "QUICKSTART.md": ROOT / "QUICKSTART.md",
        "DEPLOYMENT.md": ROOT / "DEPLOYMENT.md",
    }

    for src in docs_dir.iterdir():
        if not src.is_file():
            continue
        # после rename у нас будут "requirements.txt", ".env.example", ...
        if src.name in mapping:
            dst = mapping[src.name]
            dst.parent.mkdir(parents=True, exist_ok=True)
            print(f"MOVE: {src} -> {dst}")
            shutil.copy2(src, dst)

# 3) Создаём нужные __init__.py
def ensure_inits():
    init_targets = [
        ROOT / "backend" / "app" / "__init__.py",
        ROOT / "backend" / "app" / "models" / "__init__.py",
        ROOT / "backend" / "app" / "schemas" / "__init__.py",
        ROOT / "backend" / "app" / "api" / "__init__.py",
        ROOT / "backend" / "app" / "services" / "__init__.py",
        ROOT / "backend" / "app" / "utils" / "__init__.py",
    ]
    for t in init_targets:
        t.parent.mkdir(parents=True, exist_ok=True)
        if not t.exists():
            print(f"CREATE: {t}")
            t.write_text("", encoding="utf-8")

def main():
    # фиксим имена в backend и docs
    fix_names(ROOT / "backend")
    fix_names(ROOT / "docs")

    # переносим ключевые файлы из docs
    move_known_docs()

    # создаём __init__.py
    ensure_inits()

    print("\nDONE. Теперь проверь backend/app/*.py и запуск docker compose.")

if __name__ == "__main__":
    main()
