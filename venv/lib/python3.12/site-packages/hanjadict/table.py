import json
from pathlib import Path


def load_table(filename: Path) -> dict:
    table: dict = json.loads(Path(filename).read_text(encoding="utf-8"))
    return table


basepath = Path(__file__).parent.absolute()
table_data = load_table(basepath / "table.json")
