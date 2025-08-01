class Config:
    def __init__(self, user_config=None):
        self._defaults = {
            "UPLOAD_DIR": "uploads",         # where to save uploaded files
            "DEBUG": False,                  # show internal stacktrace
            "LOGGING_ENABLED": False,        # enable logging (later)
        }
        self._overrides = user_config or {}

    def get(self, key, default=None):
        return self._overrides.get(key, self._defaults.get(key, default))

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self._overrides[key] = value

    def __contains__(self, key):
        return key in self._overrides or key in self._defaults

    def to_dict(self):
        data = self._defaults.copy()
        data.update(self._overrides)
        return data
