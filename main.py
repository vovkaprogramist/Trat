import calendar
import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from store import CATS, GROUPS, LABEL, Store, group_of

MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль",
          "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
              "августа", "сентября", "октября", "ноября", "декабря"]
WEEK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

BG = (0.98, 0.98, 0.97, 1)
FG = (0.12, 0.12, 0.12, 1)
GREY = (0.55, 0.55, 0.55, 1)
GOLD = (0.96, 0.74, 0.16, 1)
GOLD_LIGHT = (0.99, 0.93, 0.74, 1)
CELL = (0.94, 0.94, 0.92, 1)


def fmt(cents):
    if cents % 100 == 0:
        s = "{:,}".format(cents // 100).replace(",", " ")
    else:
        s = "{:,.2f}".format(cents / 100).replace(",", " ")
    return s + " руб"


def short(cents):
    r = cents / 100
    if r >= 1000:
        return ("%.1f" % (r / 1000)).rstrip("0").rstrip(".") + "к"
    return str(int(round(r)))


def flat(text, bg=CELL, fg=FG, **kw):
    return Button(text=text, background_normal="", background_down="",
                  background_color=bg, color=fg, **kw)


def label(text, size=16, color=FG, halign="left", **kw):
    lb = Label(text=text, font_size=sp(size), color=color, halign=halign,
               valign="middle", **kw)
    lb.bind(size=lambda i, v: setattr(i, "text_size", v))
    return lb


class TratApp(App):
    title = "Счётчик трат"

    def build(self):
        Window.clearcolor = BG
        Window.softinput_mode = "pan"
        self.store = Store(os.path.join(self.user_data_dir, "data.bin"))
        today = datetime.date.today()
        self.year, self.month, self.sel = today.year, today.month, today

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))

        head = BoxLayout(size_hint_y=None, height=dp(46))
        prev = flat("<", bg=BG, font_size=sp(24), size_hint_x=None, width=dp(56))
        nxt = flat(">", bg=BG, font_size=sp(24), size_hint_x=None, width=dp(56))
        prev.bind(on_release=lambda *_: self.shift(-1))
        nxt.bind(on_release=lambda *_: self.shift(1))
        self.title_lb = label("", 22, halign="center")
        head.add_widget(prev)
        head.add_widget(self.title_lb)
        head.add_widget(nxt)
        root.add_widget(head)

        self.total_lb = label("", 34, GOLD, halign="center",
                              size_hint_y=None, height=dp(56))
        self.total_lb.bold = True
        root.add_widget(self.total_lb)

        wk = GridLayout(cols=7, size_hint_y=None, height=dp(22))
        for w in WEEK:
            wk.add_widget(label(w, 13, GREY, halign="center"))
        root.add_widget(wk)

        self.cal = GridLayout(cols=7, spacing=dp(3), size_hint_y=None,
                              row_default_height=dp(48), row_force_default=True)
        root.add_widget(self.cal)

        self.day_lb = label("", 17, size_hint_y=None, height=dp(34))
        self.day_lb.bold = True
        root.add_widget(self.day_lb)

        sv = ScrollView()
        self.items = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.items.bind(minimum_height=self.items.setter("height"))
        sv.add_widget(self.items)
        root.add_widget(sv)

        bar = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        add = flat("+ Трата", bg=GOLD, fg=(1, 1, 1, 1), font_size=sp(18))
        add.bind(on_release=self.open_add)
        summ = flat("Итоги месяца", font_size=sp(16))
        summ.bind(on_release=self.open_summary)
        bar.add_widget(add)
        bar.add_widget(summ)
        root.add_widget(bar)

        self.refresh()
        return root

    # ---------- навигация ----------
    def shift(self, d):
        m = self.month + d
        y = self.year
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        self.year, self.month = y, m
        today = datetime.date.today()
        day = today.day if (today.year, today.month) == (y, m) else 1
        self.sel = datetime.date(y, m, day)
        self.refresh()

    def select(self, date):
        self.sel = date
        self.refresh()

    # ---------- отрисовка ----------
    def refresh(self):
        y, m = self.year, self.month
        self.title_lb.text = "%s %d" % (MONTHS[m - 1], y)
        self.total_lb.text = fmt(self.store.month_total(y, m))
        totals = self.store.month_day_totals(y, m)
        today = datetime.date.today()
        first_wd, ndays = calendar.monthrange(y, m)

        self.cal.clear_widgets()
        for _ in range(first_wd):
            self.cal.add_widget(Widget())
        for d in range(1, ndays + 1):
            date = datetime.date(y, m, d)
            t = totals.get(d, 0)
            txt = str(d)
            if t:
                txt += "\n[size=%dsp]%s[/size]" % (10, short(t))
            if date == self.sel:
                bg, fg = GOLD, (1, 1, 1, 1)
            elif t:
                bg, fg = GOLD_LIGHT, FG
            elif date == today:
                bg, fg = (0.86, 0.86, 0.84, 1), FG
            else:
                bg, fg = CELL, FG
            b = flat(txt, bg=bg, fg=fg, markup=True, halign="center",
                     font_size=sp(15))
            b.bind(on_release=lambda _b, dt=date: self.select(dt))
            self.cal.add_widget(b)
        rows = (first_wd + ndays + 6) // 7
        self.cal.height = rows * dp(48) + (rows - 1) * dp(3)
        self.refresh_day()

    def refresh_day(self):
        key = self.sel.isoformat()
        self.day_lb.text = "%d %s  ·  %s" % (
            self.sel.day, MONTHS_GEN[self.sel.month - 1],
            fmt(self.store.day_total(key)))
        self.items.clear_widgets()
        items = self.store.day_items(key)
        if not items:
            self.items.add_widget(label("Трат нет", 15, GREY,
                                        size_hint_y=None, height=dp(40)))
        for idx, (cat, cents, note) in enumerate(items):
            row = BoxLayout(size_hint_y=None, height=dp(44))
            name = LABEL.get(cat, cat) + (("  (%s)" % note) if note else "")
            row.add_widget(label(name, 15))
            row.add_widget(label(fmt(cents), 15, halign="right",
                                 size_hint_x=None, width=dp(100)))
            x = flat("x", bg=BG, fg=GREY, font_size=sp(18),
                     size_hint_x=None, width=dp(40))
            x.bind(on_release=lambda _b, i=idx: self.ask_delete(key, i))
            row.add_widget(x)
            self.items.add_widget(row)

    # ---------- окна ----------
    def open_add(self, *_):
        box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        labels = [c[1] for c in CATS]
        cat = Spinner(text=labels[0], values=labels, size_hint_y=None,
                      height=dp(48), background_normal="",
                      background_color=GOLD_LIGHT, color=FG, font_size=sp(17))
        amount = TextInput(hint_text="Сумма, руб", multiline=False,
                           input_type="number", font_size=sp(20),
                           size_hint_y=None, height=dp(50))
        note = TextInput(hint_text="Заметка (необязательно)", multiline=False,
                         font_size=sp(16), size_hint_y=None, height=dp(46))
        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        cancel = flat("Отмена", font_size=sp(16))
        save = flat("Сохранить", bg=GOLD, fg=(1, 1, 1, 1), font_size=sp(16))
        btns.add_widget(cancel)
        btns.add_widget(save)
        for w in (cat, amount, note, btns):
            box.add_widget(w)
        pop = Popup(title="Трата · %d %s" % (self.sel.day,
                    MONTHS_GEN[self.sel.month - 1]), content=box,
                    size_hint=(0.92, None), height=dp(310),
                    pos_hint={"center_x": 0.5, "top": 0.9})

        def do_save(*_):
            try:
                val = float(amount.text.replace(",", ".").replace(" ", ""))
            except ValueError:
                amount.hint_text = "Введите сумму"
                return
            if val <= 0:
                return
            cat_id = CATS[labels.index(cat.text)][0]
            self.store.add(self.sel.isoformat(), cat_id,
                           int(round(val * 100)), note.text.strip())
            pop.dismiss()
            self.refresh()

        cancel.bind(on_release=pop.dismiss)
        save.bind(on_release=do_save)
        pop.open()
        Clock.schedule_once(lambda dt: setattr(amount, "focus", True), 0.3)

    def ask_delete(self, key, idx):
        box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        box.add_widget(label("Удалить эту трату?", 17, (1, 1, 1, 1),
                             halign="center"))
        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        no = flat("Нет", font_size=sp(16))
        yes = flat("Удалить", bg=(0.85, 0.3, 0.25, 1), fg=(1, 1, 1, 1),
                   font_size=sp(16))
        btns.add_widget(no)
        btns.add_widget(yes)
        box.add_widget(btns)
        pop = Popup(title="", content=box, size_hint=(0.8, None),
                    height=dp(160), separator_height=0)

        def do(*_):
            self.store.delete(key, idx)
            pop.dismiss()
            self.refresh()

        no.bind(on_release=pop.dismiss)
        yes.bind(on_release=do)
        pop.open()

    def open_summary(self, *_):
        y, m = self.year, self.month
        by = self.store.month_by_cat(y, m)
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(2),
                          padding=dp(6))
        grid.bind(minimum_height=grid.setter("height"))
        white = (1, 1, 1, 1)
        if not by:
            grid.add_widget(label("В этом месяце трат нет", 16, white,
                                  size_hint_y=None, height=dp(40)))
        for gid, gname in GROUPS:
            subs = [(c, v) for c, v in by.items() if group_of(c) == gid]
            if not subs:
                continue
            total = sum(v for _, v in subs)
            row = BoxLayout(size_hint_y=None, height=dp(40))
            lb = label(gname, 17, GOLD)
            lb.bold = True
            row.add_widget(lb)
            row.add_widget(label(fmt(total), 17, GOLD, halign="right",
                                 size_hint_x=None, width=dp(130)))
            grid.add_widget(row)
            if gid == "zhkh":
                for c, v in sorted(subs):
                    r = BoxLayout(size_hint_y=None, height=dp(32))
                    r.add_widget(label("    " + LABEL.get(c, c).split("· ")[-1],
                                       15, white))
                    r.add_widget(label(fmt(v), 15, white, halign="right",
                                       size_hint_x=None, width=dp(130)))
                    grid.add_widget(r)
        sv = ScrollView()
        sv.add_widget(grid)
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        box.add_widget(sv)
        box.add_widget(label("Всего: " + fmt(sum(by.values())), 19, white,
                             halign="center", size_hint_y=None, height=dp(40)))
        close = flat("Закрыть", font_size=sp(16), size_hint_y=None,
                     height=dp(46))
        box.add_widget(close)
        pop = Popup(title="%s %d" % (MONTHS[m - 1], y), content=box,
                    size_hint=(0.92, 0.8))
        close.bind(on_release=pop.dismiss)
        pop.open()


if __name__ == "__main__":
    TratApp().run()
