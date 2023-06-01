from collections import (
    namedtuple,
)
from math import (
    log10,
)
from random import (
    random,
    choice,
)
from tkinter import (
    Entry,
    Frame,
    Label,
    RIGHT,
    StringVar,
    Tk,
)
from tkinter.messagebox import (
    showerror,
)


DIGIT_COLOR = (
    "black",
    "brown",
    "red",
    "orange",
    "yellow",
    "green",
    "cyan",
    "violet",
    "grey",
    "white",
)

MULTIPLER_COLOR = (
    "silver",  # 0.01
    "gold",
    "black",
    "brown",
    "red",
    "orange",
    "yellow",
    "green",
    "cyan",
    "violet",
    "grey",
)

TOLERANCES = {
    0.05 : "grey",
    0.10 : "violet",
    0.25 : "cyan",
    0.5  : "green",
    1.   : "brown",
    2.   : "red",
    5.   : "gold",
    10.  : "silver",
}

MULTIPLERS = {
    "u": 0.000001,
    "m": 0.001,
    "k": 1000.,
    "M": 1000000.,
    "G": 1000000000.,
}



class ResistorSpec(namedtuple("_ResistorSpec",
    "resistance tolerance lines"
)):

    def iter_colors_reversed(self):
        yield TOLERANCES[self.tolerance]
        total_digits = int(log10(self.resistance)) + 1
        signif_digits = self.lines - 2
        multipler_digits = total_digits - signif_digits
        yield MULTIPLER_COLOR[multipler_digits + 2]
        signif_value = self.resistance / (10. ** multipler_digits)
        for _ in range(signif_digits):
            yield DIGIT_COLOR[int(signif_value % 10.)]
            signif_value /= 10.

    def __str__(self):
        return str(self.resistance) + "+" + str(self.tolerance)


class ForwardStream():

    def __init__(self, data):
        self._data = data
        self._offset = 0

    def peek(self, s = None, e = None):
        o = self._offset
        if s is None:
            s = o
        else:
            s = s + o
        if e is None:
            e = s + 1
        else:
            e += o
        return self._data[s:e]

    def __next__(self):
        o = self._offset
        n = o + 1
        self._offset = n
        return self._data[o:n]

    def skip(self, c = 1):
        self._offset += c


def parse_resistor_spec(s):
    resistance, sig = parse_resistor_value(s)
    return ResistorSpec(
        resistance,
        parse_resistor_tolerance_opt(s),
        max(sig + 2, 4),
    )


def parse_resistor_value(s):
    r = 0
    sd = 0  # significant digits
    while True:
        d = s.peek()
        if not d:
            return r, sd
        elif d in ".,":
            break
        elif d in "0123456789":
            s.skip()
            r = r * 10 + int(d)
            sd += 1
        elif d in MULTIPLERS:
            s.skip()
            r *= MULTIPLERS[d]
            return r, sd
        else:
            return r, sd
    s.skip()  # .,
    m = 1.
    while True:
        d = s.peek()
        if not d:
            return r, sd
        elif d in "0123456789":
            s.skip()
            m /= 10
            r += m * int(d)
            sd += 1
        elif d in MULTIPLERS:
            s.skip()
            r *= MULTIPLERS[d]
            return r, sd
        else:
            return r, sd


def parse_resistor_tolerance_opt(s):
    d = s.peek()
    if not d:
        return 5.
    if d not in "+-":
        raise ValueError("tolerance must start from + or -")
    s.skip()
    t = 0
    while True:
        d = s.peek()
        if not d:
            return t
        elif d in ".," :
            break
        elif d in "0123456789":
            s.skip()
            t = t * 10 + int(d)
        else:
            raise ValueError("incorrect tolerance")
    s.skip()  # .,
    m = 1.
    while True:
        d = s.peek()
        if not d:
            return t
        elif d in "0123456789":
            s.skip()
            m /= 10
            t += m * int(d)
        else:
            raise ValueError("incorrect tolerance")


class GENERATE_COLORS: pass
class ASK_VALUE: pass


def main():
    tk = Tk()
    tk.title("Resistor Color Training")

    f_colors = Frame(tk)
    f_colors.pack()

    def set_colors(rs):
        for f in f_colors.winfo_children():
            f.destroy()
        for c in rs.iter_colors_reversed():
            f = Frame(f_colors,
                background = c,
                width = 10,
                height = 50,
            )
            f.pack(side = RIGHT, padx = 5)

    v_value = StringVar(tk)
    e_value = Entry(tk, textvariable = v_value)
    e_value.pack()

    mode = ASK_VALUE

    if mode is GENERATE_COLORS:
        def _on_e_value_return(e):
            value = e_value.get()
            try:
                rs = parse_resistor_spec(ForwardStream(value))
            except ValueError as e:
                showerror(type(e), str(e))
            else:
                set_colors(rs)
    elif mode is ASK_VALUE:
        context = {}

        _TOLERANCES = tuple(TOLERANCES)

        def ask():
            rs = ResistorSpec(
                int(random() * 1000.) * (10. ** int(random() * 6)),
                choice(_TOLERANCES),
                4 + int(random() * 2)
            )
            context["rs"] = rs
            set_colors(rs)

        l_res = Label(tk)
        l_res.pack()

        def _on_e_value_return(e):
            value = v_value.get()
            try:
                rs = parse_resistor_spec(ForwardStream(value))
            except ValueError as e:
                showerror(type(e), str(e))
            else:
                rsr = context["rs"]
                rs = ResistorSpec(
                    rs.resistance,
                    rs.tolerance,
                    rsr.lines
                )
                try:
                    rsc = tuple(rs.iter_colors_reversed())
                except:
                    # user may input non-standard tolerance
                    rsc = None
                rscr = tuple(rsr.iter_colors_reversed())
                if rsc != rscr:
                    showerror(
                        title = "Incorrect",
                        message = (
                            "Entered: " + str(rs)
                          + "\nRequired: " + str(context["rs"])
                        ),
                    )
                ask()
                v_value.set("")
                e_value.focus()

        ask()

    e_value.bind("<Return>", _on_e_value_return)
    e_value.bind("<KP_Enter>", _on_e_value_return)

    e_value.focus()

    tk.mainloop()
