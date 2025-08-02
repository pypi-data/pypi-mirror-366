from collections import defaultdict

from oarepo_runtime.records.systemfields import PathSelector


class KeywordsFieldSelector(PathSelector):
    def select(self, record):
        ret = super().select(record)
        by_language = defaultdict(list)
        for r in ret:
            lang = r.get("lang", "en")
            value = r.get("value")
            if not value:
                continue
            by_language[lang].append(value)
        return [by_language]
