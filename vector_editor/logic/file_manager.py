import json
import os


class FileManager:
    @staticmethod
    def save_to_file(filename: str, data: dict):
        """
        Сохраняет словарь данных в JSON файл.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"File saved: {filename}")
        except OSError as e:
            raise IOError(f"Ошибка записи файла: {e}")

    @staticmethod
    def load_from_file(filename: str) -> dict:
        """
        Читает JSON файл и возвращает словарь.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл не найден: {filename}")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Файл поврежден (некорректный JSON)")
        except OSError as e:
            raise IOError(f"Ошибка чтения файла: {e}")
