import datetime
import json
import os
from exceptions import *
from utils import *

class SharedPreferenceFlet:
    def __init__(self, name: str = "prefs.json", password: str = "defaultPassword"):
        self.file = name
        self.lock_file = self.file + ".lock"
        self.salt_file = self.file + ".salt"
        self.password = password
        self.encrypted = os.path.exists(self.lock_file)
        self._prefs = {}
        self._loaded = False

        self.key = self.derive_key(password)

        if not os.path.exists(self.file) and not self.encrypted:
            self._write_empty_file()
            self.encrypt_file()

        self.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()

    # ---------- Encryption ----------
    def derive_key(self, password: str) -> bytes:
        if not os.path.exists(self.salt_file):
            salt = os.urandom(16)
            with open(self.salt_file, "wb") as f:
                f.write(salt)
        else:
            with open(self.salt_file, "rb") as f:
                salt = f.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt_file(self):
        if os.path.exists(self.file):
            cryptographyJson.encrypt_file_advanced(self.file, self.key)
            self.encrypted = True

    def decrypt_if_needed(self):
        if not os.path.exists(self.file) and os.path.exists(self.lock_file):
            try:
                cryptographyJson.decrypt_file(self.lock_file, self.key)
                self.encrypted = False
            except Exception:
                raise DecryptionError("⚠️ Failed to decrypt. Please check the password or file integrity.")

    def _write_empty_file(self):
        with open(self.file, "w") as f:
            json.dump({}, f)

    # ---------- Load & Save ----------
    def load(self):
        if self._loaded:
            return
        self.decrypt_if_needed()
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                self._prefs = json.load(f)
        self._loaded = True

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self._prefs, f, indent=2)
        self.encrypt_file()

    def Close(self):
        self.save()

    # ---------- Tools ----------
    def _validate_type(self, val, expected, key):
        if not isinstance(val, expected):
           raise InvalidTypeError('This key does not exist.' if val is None else 'This key is not of the expected type.') 


    # ---------- Setter Methods ----------
    def setString(self, key: str, value: str):
        self._validate_type(value, str, key)
        self._prefs[key] = value
        return value

    def setBool(self, key: str, value: bool):
        self._validate_type(value, bool, key)
        self._prefs[key] = value
        return value

    def setInt(self, key: str, value: int):
        self._validate_type(value, int, key)
        self._prefs[key] = value
        return value

    def setDouble(self, key: str, value: float):
        self._validate_type(value, float, key)
        self._prefs[key] = value
        return value

    def setStringList(self, key: str, value: list[str]):
        self._validate_type(value, list, key)
        if not all(isinstance(v, str) for v in value):
            raise TypeError(f"All elements of '{key}' must be strings")
        self._prefs[key] = value
        return value

    def setList(self, key: str, value: list):
        self._validate_type(value, list, key)
        self._prefs[key] = value
        return value

    def setDateTime(self, key: str, value: datetime.datetime):
        self._prefs[key] = value.isoformat()

    # ---------- Getter Methods ----------
    def getString(self, key: str) -> str:
        val = self._prefs.get(key)
        self._validate_type(val, str, key)
        return val

    def getBool(self, key: str) -> bool:
        val = self._prefs.get(key)
        self._validate_type(val, bool, key)
        return val

    def getInt(self, key: str) -> int:
        val = self._prefs.get(key)
        self._validate_type(val, int, key)
        return val

    def getDouble(self, key: str) -> float:
        val = self._prefs.get(key)
        self._validate_type(val, float, key)
        return val

    def getStringList(self, key: str, default: list[str] = None):
        value = self._prefs.get(key, default if default is not None else [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise TypeError(f"Value for '{key}' is not a list of strings")
        return value


    def getList(self, key: str) -> list:
        val = self._prefs.get(key)
        self._validate_type(val, list, key)
        return val

    def getDateTime(self, key: str) -> datetime.datetime:
        val = self._prefs.get(key)
        return datetime.datetime.fromisoformat(val)

    def remove(self, key: str = None):
        if key:
            if key in self._prefs:
                del self._prefs[key]
        else:
            self._prefs.clear()
        self.save()



