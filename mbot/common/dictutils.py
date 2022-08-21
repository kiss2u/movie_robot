class DictUtils:
    @staticmethod
    def get_item_value(item, key, default_value):
        if not item:
            return default_value
        if key not in item:
            return default_value
        if item.get(key) is None:
            return default_value
        return item.get(key)

    @staticmethod
    def get_item_int_value(item, key, default_value):
        if not item:
            return default_value
        if key not in item:
            return default_value
        if item.get(key) is None:
            return default_value
        try:
            ss = str(item.get(key)).replace(',', '')
            return int(ss)
        except Exception as e:
            return default_value

    @staticmethod
    def get_item_float_value(item, key, default_value):
        if not item:
            return default_value
        if key not in item:
            return default_value
        if item.get(key) is None:
            return default_value
        try:
            ss = str(item.get(key)).replace(',', '')
            return float(ss)
        except Exception as e:
            return default_value
