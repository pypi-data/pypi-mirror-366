from pathlib import Path


class Helper:
    @staticmethod
    def available_filename(path: Path):
        stem = path.stem
        i = 0
        while path.exists():
            i += 1
            path = path.with_stem(f'{stem}-{i}')
        return path
