"""Хранилище трат: JSON -> zlib (уровень 9) -> один маленький файл."""
import json
import os
import zlib

CATS = [
    ("eda", "Еда"),
    ("zhkh.musor", "ЖКХ · Мусор"),
    ("zhkh.gaz", "ЖКХ · Газ"),
    ("zhkh.svet", "ЖКХ · Свет"),
    ("zhkh.voda", "ЖКХ · Вода"),
    ("zhkh.otoplenie", "ЖКХ · Отопление"),
    ("zhkh.internet", "ЖКХ · Интернет"),
    ("zhkh.domofon", "ЖКХ · Домофон"),
    ("zhkh.drugoe", "ЖКХ · Другое"),
    ("transport", "Транспорт"),
    ("apteka", "Лекарства"),
    ("prochee", "Прочее"),
]
LABEL = dict(CATS)
GROUPS = [("eda", "Еда"), ("zhkh", "ЖКХ"), ("transport", "Транспорт"),
          ("apteka", "Лекарства"), ("prochee", "Прочее")]


def group_of(cat_id):
    return cat_id.split(".")[0]


class Store:
    # data: {"2026-10-25": [[cat_id, копейки, "заметка"], ...]}
    def __init__(self, path):
        self.path = path
        self.data = {}
        self.load()

    def load(self):
        try:
            with open(self.path, "rb") as f:
                self.data = json.loads(zlib.decompress(f.read()).decode("utf-8"))
        except Exception:
            self.data = {}

    def save(self):
        raw = json.dumps(self.data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        tmp = self.path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(zlib.compress(raw, 9))
        os.replace(tmp, self.path)

    def add(self, day, cat_id, cents, note=""):
        self.data.setdefault(day, []).append([cat_id, int(cents), note])
        self.save()

    def delete(self, day, idx):
        items = self.data.get(day, [])
        if 0 <= idx < len(items):
            items.pop(idx)
            if not items:
                self.data.pop(day, None)
            self.save()

    def day_items(self, day):
        return self.data.get(day, [])

    def day_total(self, day):
        return sum(i[1] for i in self.data.get(day, []))

    def _month_days(self, y, m):
        prefix = "%04d-%02d-" % (y, m)
        return {k: v for k, v in self.data.items() if k.startswith(prefix)}

    def month_total(self, y, m):
        return sum(i[1] for v in self._month_days(y, m).values() for i in v)

    def month_day_totals(self, y, m):
        return {int(k[-2:]): sum(i[1] for i in v) for k, v in self._month_days(y, m).items()}

    def month_by_cat(self, y, m):
        out = {}
        for v in self._month_days(y, m).values():
            for cat, cents, _ in v:
                out[cat] = out.get(cat, 0) + cents
        return out
