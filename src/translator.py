from pathlib import Path
from typing import Dict, List
import json


class Translator:

    def __init__(self, locales_dir: str):
        self.locales_dir: Path = Path(locales_dir)
        self.translations: Dict[str, str] = {}

    def load_language(self, lang: str) -> bool:
        file_path = self.locales_dir / f"{lang}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                    return True
            except Exception as e:
                self.translations = {}
        else:
            self.translations = {}
        return False

    def gettext(self, key: str) -> str:
        return self.translations.get(key, key)

    def get_available_languages(self) -> List[str]:
        return [p.stem for p in self.locales_dir.glob("*.json")]
