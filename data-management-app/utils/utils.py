
from dateutil.parser import parse
import re

class Utils:

    def keys_to_snakecase(self, list_of_dicts):
        """
        Converts a list of dictionary keys to snakecase.
        @param name: The string to convert.
        """

        lod = [{self.spacecase_to_snakecase(str(k)) if ' ' in k
                else str(k).lower() if '_' in k
                else self.camelcase_to_snakecase(str(k)): v for k, v in x.items()} for x in list_of_dicts]

        return lod

    @staticmethod
    def camelcase_to_snakecase(name):
        """
        Converts camelcase string to snakecase.
        @param name: The string to convert.
        """
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)).lower()

    @staticmethod
    def spacecase_to_snakecase(name):
        """
        Converts spacecase string to snakecase.
        @param name: The string to convert.
        """

        return '_'.join(n.lower() for n in name.split())

    @staticmethod
    def add_missing_keys(list_of_dicts):
        """
        Iterates over a list of dictionaries, and adds missing keys.
        """

        key_list = []
        for x in list_of_dicts:
            for k, v in x.items():
                if k not in key_list:
                    key_list.append(k)

        for x in list_of_dicts:                                      # Creating missing keys
            for key in key_list:
                if key not in x:
                    x[key] = None

        return list_of_dicts, key_list

    def match_key_types(self, list_of_dicts, keys):
        """
        Iterates over a list of dicts and returns a separate dictionary with column: data-type matches.
        """

        matched = {}

        for x in keys:

            if all(self.is_int(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'INTEGER'})

            elif all(self.is_bool(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'BOOLEAN'})

            elif all(self.is_float(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'NUMERIC'})

            elif all(self.is_dict(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'JSONB'})

            elif all(self.is_list(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: '_VARCHAR'})

            elif all(self.is_date(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'TIMESTAMP'})

            elif all(self.is_str(j[x]) == True for j in list_of_dicts if j[x]):

                matched.update({x: 'VARCHAR'})

            else:
                matched.update({x: '_VARCHAR'})

        return matched

    @staticmethod
    def is_date(val):
        try:
            parse(val)
            return True
        except (ValueError, OverflowError, TypeError): return False

    @staticmethod
    def is_int(val):
        try:
            int(val)

            if '.' not in str(val) and val != True and val != False:
                return True
            else:
                return False
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_float(val):
        try:
            int(val)
            return True
        except (ValueError, TypeError): return False

    @staticmethod
    def is_bool(val):
        if isinstance(val, bool):
            return True
        else: return False

    @staticmethod
    def is_str(val):
        if isinstance(val, str):
            return True
        else: return False

    @staticmethod
    def is_dict(val):
        try:
            dict(val)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_list(val):
        if isinstance(val, list):
            return True
        else: return False
