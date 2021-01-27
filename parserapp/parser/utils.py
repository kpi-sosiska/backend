import json
import re
from pathlib import Path


class GroupCode:
    _fac_to_prefix = json.load((Path(__file__).parent / 'fac2prefix.json').open())

    def __init__(self, group):
        self.group = group               # ik-ф72мп (асоиу)
        w = list(re.search(r'(.*-)'         # ik-
                           r'(.*)'          # ф 
                           r'(\d)'          # 7
                           r'(\d)'          # 2
                           r'((?:мп|мн)?)'  # мп
                           r'(.*)',         # (асоиу)
                 group).groups())

        w[3] = '*'  # тут то, что обычно номер группы в потоке
        self.potok = ''.join(w)

        w[2] = '*'  # тут то, что обычно год группы в потоке
        self.potoki = ''.join(w)

        w[1:5] = '', '*', '*', ''
        self.metapotoki = ''.join(w)

        self.faculty = self._get_faculty(self.metapotoki)

    @classmethod
    def _get_faculty(cls, group):
        for fac, prefixes in cls._fac_to_prefix.items():
            for prefix in prefixes:
                if group.startswith(prefix):
                    return fac
        return None
