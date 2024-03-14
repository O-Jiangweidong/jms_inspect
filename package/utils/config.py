import os


class Config(object):
    def __init__(self, config_path, config_prefix=None):
        self._config_path = config_path
        self._config_mapping = None
        self._prefix = config_prefix

        self.pre_check()

    def pre_check(self):
        if self._config_path is None or \
                not os.path.exists(self._config_path) or \
                not os.path.isfile(self._config_path):
            self._config_mapping = {}

    def get_config_mapping(self):
        cf_mapping = {}
        with open(self._config_path) as f_reader:
            config_list = f_reader.readlines()
            for cf in config_list:
                real_cf = cf.strip()
                if not real_cf or real_cf.startswith('#') \
                        or self._prefix and not real_cf.startswith(self._prefix):
                    continue
                try:
                    key, value = real_cf.split('=', 1)
                    cf_mapping[key.strip()] = value.strip()
                except ValueError:
                    pass
        return cf_mapping

    @property
    def config_mapping(self):
        if self._config_mapping is None:
            self._config_mapping = self.get_config_mapping()
        return self._config_mapping

    def get(self, name, default=None):
        if self._prefix:
            key = self._prefix + name
        else:
            key = name
        return self.config_mapping.get(key, default)
