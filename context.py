# context.py

from typing import Dict, Any, Optional


class Context:
    """
        A context object that holds key-value data used for token resolution.
        Supports nested access, namespacing, and serialization.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
            Retrieve a value using dot-notation keys (e.g., 'shot.name').
            If the key does not exist, return the default value.

            :param key: The key to retrieve, using dot-notation for nested keys.
            :param default: The default value to return if the key does not exist.
            :return: The value associated with the key, or the default value.

        """
        parts = key.split(".")
        val = self._data
        try:
            for part in parts:
                val = val[part]
            return val
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
            Set a value using dot-notation (e.g., 'asset.type').
            If the key does not exist, it will be created.

            :param key: The key to set, using dot-notation for nested keys.
            :param value: The value to set for the key.
        """
        parts = key.split(".")
        d = self._data
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    def update(self, other: Dict[str, Any]) -> None:
        """
            Merge in another dictionary of context values.
            Existing keys will be overwritten.

            :param other: A dictionary of key-value pairs to merge into the context.
        """
        for k, v in other.items():
            self.set(k, v)

    def as_dict(self) -> Dict[str, Any]:
        """
            Return full context as a dict.
            This is useful for serialization or inspection.

            :return: The context data as a dictionary.
        """
        return self._data

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, item):
        return self.get(item) is not None

    def __repr__(self):
        return f"<Context {self._data}>"
