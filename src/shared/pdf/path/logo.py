from pathlib import Path

from decouple import config

BASE_DIR = Path(config('PDF_PATH'))
ASSETS = BASE_DIR / 'assets'


class LogoPdfPath:
    @staticmethod
    def get_logo(filename: str):
        return str(ASSETS / filename)
