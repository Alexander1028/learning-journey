import tkinter as tk
from tkinter import messagebox

BG_COLOR = "#000000"
NUM_BG = "#333333"
NUM_ACTIVE = "#737373"
FUNC_BG = "#A5A5A5"
FUNC_ACTIVE = "#E5E5EA"
OP_BG = "#FF9500"
OP_ACTIVE = "#FFB143"
OP_SELECTED_BG = "#FFFFFF"
OP_SELECTED_FG = "#FF9500"
TEXT_WHITE = "#FFFFFF"
TEXT_DIM = "#6E6E73"
TEXT_DARK = "#000000"
FLASH_RESULT = "#FFD60A"
FLASH_CLEAR = "#8E8E93"

root = tk.Tk()
root.title("Calculadora")
root.geometry("360x620")
root.resizable(False, False)
root.configure(bg=BG_COLOR)

expression = ""
just_evaluated = False
active_op_btn = None
display_anim_job = None
transition_anim_job = None
last_displayed_text = "0"


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    r, g, b = [max(0, min(255, int(round(c)))) for c in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"


def lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def animate_display_flash(accent_hex: str):
    global display_anim_job, transition_anim_job
    if transition_anim_job is not None:
        root.after_cancel(transition_anim_job)
        transition_anim_job = None
    if display_anim_job is not None:
        root.after_cancel(display_anim_job)
        display_anim_job = None

    steps = 14
    half = steps // 2

    def step(i):
        global display_anim_job
        if i <= half:
            t = i / half
            color = lerp_color(TEXT_WHITE, accent_hex, t)
        else:
            t = (i - half) / half
            color = lerp_color(accent_hex, TEXT_WHITE, t)
        screen_label.config(fg=color)
        if i < steps:
            display_anim_job = root.after(16, lambda: step(i + 1))
        else:
            screen_label.config(fg=TEXT_WHITE)
            display_anim_job = None

    step(0)


def animate_text_transition(new_text: str, font_size: int):
    global transition_anim_job, last_displayed_text
    if transition_anim_job is not None:
        root.after_cancel(transition_anim_job)
        transition_anim_job = None

    if new_text == last_displayed_text:
        screen_label.config(text=new_text, font=("Helvetica Neue", font_size, "normal"), fg=TEXT_WHITE, padx=0)
        return

    last_displayed_text = new_text
    screen_label.config(text=new_text, font=("Helvetica Neue", font_size, "normal"))

    steps = 8

    def step(i):
        global transition_anim_job
        t = i / steps
        ease = 1 - (1 - t) ** 2
        fg_color = lerp_color(TEXT_DIM, TEXT_WHITE, ease)
        pad_x = int(round(12 * (1 - ease)))
        screen_label.config(fg=fg_color, padx=pad_x)
        if i < steps:
            transition_anim_job = root.after(15, lambda: step(i + 1))
        else:
            screen_label.config(fg=TEXT_WHITE, padx=0)
            transition_anim_job = None

    step(0)


def clear_op_highlight():
    global active_op_btn
    if active_op_btn is not None:
        active_op_btn.set_latched(False)
        active_op_btn = None


def format_display(value: str) -> str:
    if len(value) > 10:
        try:
            num = float(value)
            if abs(num) >= 1e9 or (0 < abs(num) < 1e-6):
                return f"{num:.4e}"
            return f"{num:.6g}"
        except ValueError:
            return value[:10]
    return value


def update_screen(text: str, animate: bool = True):
    display_str = format_display(text) if text else "0"
    font_size = 52 if len(display_str) <= 6 else (40 if len(display_str) <= 9 else 30)
    if animate:
        animate_text_transition(display_str, font_size)
    else:
        screen_label.config(text=display_str, font=("Helvetica Neue", font_size, "normal"), fg=TEXT_WHITE, padx=0)
    clear_btn.set_label("C" if expression else "AC")


def press_num(val: str):
    global expression, just_evaluated
    clear_op_highlight()

    if just_evaluated:
        expression = "" if val != "." else "0"
        just_evaluated = False

    if val == ".":
        current_part = expression.split("+")[-1].split("-")[-1].split("*")[-1].split("/")[-1]
        if "." in current_part:
            return
        if not current_part:
            expression += "0"

    if expression == "0" and val != ".":
        expression = val
    else:
        expression += val
    update_screen(expression)


def press_op(op_symbol: str, btn=None):
    global expression, just_evaluated, active_op_btn
    op_map = {"÷": "/", "×": "*", "−": "-", "+": "+"}
    op = op_map.get(op_symbol, op_symbol)

    just_evaluated = False
    if not expression:
        if op == "-":
            expression = "-"
        return

    if expression[-1] in "+-*/":
        expression = expression[:-1] + op
    else:
        expression += op

    clear_op_highlight()
    if btn is not None:
        btn.set_latched(True)
        active_op_btn = btn

    update_screen(expression)


def clear_all():
    global expression, just_evaluated
    clear_op_highlight()
    had_content = bool(expression) and expression != "0"
    expression = ""
    just_evaluated = False
    update_screen("0", animate=not had_content)
    if had_content:
        animate_display_flash(FLASH_CLEAR)


def toggle_sign():
    global expression, just_evaluated
    if not expression:
        return
    try:
        val = eval(expression)
        val = -val
        expression = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
        just_evaluated = False
        update_screen(expression)
    except Exception:
        pass


def percent():
    global expression, just_evaluated
    if not expression:
        return
    try:
        val = eval(expression) / 100
        expression = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
        just_evaluated = False
        update_screen(expression)
    except Exception:
        pass


def equal_press():
    global expression, just_evaluated
    clear_op_highlight()
    if not expression:
        return
    try:
        clean_expr = expression.rstrip("+-*/")
        if not clean_expr:
            return
        result = eval(clean_expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        else:
            result = round(result, 8)
        expression = str(result)
        just_evaluated = True
        update_screen(expression, animate=False)
        animate_display_flash(FLASH_RESULT)
    except ZeroDivisionError:
        messagebox.showerror("Error", "No se puede dividir entre cero")
        clear_all()
    except Exception:
        messagebox.showerror("Error", "Expresión inválida")
        clear_all()


class AppleButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        bg_color,
        active_color,
        fg_color,
        command,
        pill=False,
        latched_bg=None,
        latched_fg=None,
        **kwargs,
    ):
        super().__init__(parent, bg=BG_COLOR, highlightthickness=0, bd=0, **kwargs)
        self.text = text
        self.base_bg = bg_color
        self.base_active_bg = active_color
        self.base_fg = fg_color
        self.latched_bg = latched_bg
        self.latched_fg = latched_fg
        self.command = command
        self.pill = pill

        self._latched = False
        self._pressed = False
        self._scale = 1.0
        self._target_scale = 1.0
        self._current_bg = bg_color
        self._target_bg = bg_color
        self._anim_job = None

        self.bind("<Configure>", self._draw)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _effective_bg(self):
        if self._latched and self.latched_bg:
            return self.latched_bg
        return self.base_bg

    def _effective_fg(self):
        if self._latched and self.latched_fg:
            return self.latched_fg
        return self.base_fg

    def set_label(self, new_text: str):
        self.text = new_text
        self._draw()

    def set_latched(self, state: bool):
        self._latched = state
        if not self._pressed:
            self._target_bg = self._effective_bg()
            self._start_anim()
        else:
            self._draw()

    def _start_anim(self):
        if self._anim_job is not None:
            root.after_cancel(self._anim_job)
            self._anim_job = None

        def tick():
            self._anim_job = None
            ds = self._target_scale - self._scale
            self._scale += ds * 0.45
            self._current_bg = lerp_color(self._current_bg, self._target_bg, 0.45)
            self._draw()

            if abs(ds) > 0.004 or self._current_bg.lower() != self._target_bg.lower():
                self._anim_job = root.after(15, tick)
            else:
                self._scale = self._target_scale
                self._current_bg = self._target_bg
                self._draw()

        self._anim_job = root.after(15, tick)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        r = max(2, min(r, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        pad = 4
        fg = self._effective_fg()

        if self.pill:
            base_x1, base_y1 = pad, pad
            base_x2, base_y2 = w - pad, h - pad
            cx = (base_x1 + base_x2) / 2
            cy = (base_y1 + base_y2) / 2
            bw = (base_x2 - base_x1) * self._scale
            bh = (base_y2 - base_y1) * self._scale
            x1, y1 = cx - bw / 2, cy - bh / 2
            x2, y2 = cx + bw / 2, cy + bh / 2
            radius = bh / 2
            self._round_rect(x1, y1, x2, y2, radius, fill=self._current_bg, outline="")
            self.create_text(
                (h - 2 * pad) / 2 + pad + 20,
                h / 2,
                text=self.text,
                fill=fg,
                font=("Helvetica Neue", 24, "normal"),
            )
        else:
            base_size = min(w, h) - 2 * pad
            size = base_size * self._scale
            x1 = (w - size) / 2
            y1 = (h - size) / 2
            x2 = x1 + size
            y2 = y1 + size
            self.create_oval(x1, y1, x2, y2, fill=self._current_bg, outline="")
            self.create_text(
                w / 2,
                h / 2,
                text=self.text,
                fill=fg,
                font=("Helvetica Neue", 24, "normal"),
            )

    def _on_press(self, event):
        self._pressed = True
        self._target_scale = 0.91
        self._target_bg = self.base_active_bg
        self._start_anim()

    def _on_release(self, event):
        self._pressed = False
        self._target_scale = 1.0
        self._target_bg = self._effective_bg()
        self._start_anim()
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.command()


display_frame = tk.Frame(root, bg=BG_COLOR, height=130)
display_frame.pack(fill="x", padx=18, pady=(24, 6))
display_frame.pack_propagate(False)

screen_label = tk.Label(
    display_frame,
    text="0",
    font=("Helvetica Neue", 52, "normal"),
    bg=BG_COLOR,
    fg=TEXT_WHITE,
    anchor="se",
)
screen_label.pack(fill="both", expand=True)

grid_frame = tk.Frame(root, bg=BG_COLOR, padx=10, pady=8)
grid_frame.pack(fill="both", expand=True)

for r in range(5):
    grid_frame.grid_rowconfigure(r, weight=1, uniform="row")
for c in range(4):
    grid_frame.grid_columnconfigure(c, weight=1, uniform="col")

clear_btn = AppleButton(grid_frame, "AC", FUNC_BG, FUNC_ACTIVE, TEXT_DARK, clear_all)
clear_btn.grid(row=0, column=0, sticky="nsew")

sign_btn = AppleButton(grid_frame, "+/-", FUNC_BG, FUNC_ACTIVE, TEXT_DARK, toggle_sign)
sign_btn.grid(row=0, column=1, sticky="nsew")

pct_btn = AppleButton(grid_frame, "%", FUNC_BG, FUNC_ACTIVE, TEXT_DARK, percent)
pct_btn.grid(row=0, column=2, sticky="nsew")

div_btn = AppleButton(
    grid_frame,
    "÷",
    OP_BG,
    OP_ACTIVE,
    TEXT_WHITE,
    None,
    latched_bg=OP_SELECTED_BG,
    latched_fg=OP_SELECTED_FG,
)
div_btn.command = lambda b=div_btn: press_op("÷", b)
div_btn.grid(row=0, column=3, sticky="nsew")

rows_data = [
    [("7", "num"), ("8", "num"), ("9", "num"), ("×", "op")],
    [("4", "num"), ("5", "num"), ("6", "num"), ("−", "op")],
    [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
]

for r_idx, row_items in enumerate(rows_data, start=1):
    for c_idx, (label, kind) in enumerate(row_items):
        if kind == "num":
            btn = AppleButton(
                grid_frame,
                label,
                NUM_BG,
                NUM_ACTIVE,
                TEXT_WHITE,
                lambda v=label: press_num(v),
            )
        else:
            btn = AppleButton(
                grid_frame,
                label,
                OP_BG,
                OP_ACTIVE,
                TEXT_WHITE,
                None,
                latched_bg=OP_SELECTED_BG,
                latched_fg=OP_SELECTED_FG,
            )
            btn.command = lambda op=label, b=btn: press_op(op, b)
        btn.grid(row=r_idx, column=c_idx, sticky="nsew")

zero_btn = AppleButton(
    grid_frame,
    "0",
    NUM_BG,
    NUM_ACTIVE,
    TEXT_WHITE,
    lambda: press_num("0"),
    pill=True,
)
zero_btn.grid(row=4, column=0, columnspan=2, sticky="nsew")

dot_btn = AppleButton(grid_frame, ".", NUM_BG, NUM_ACTIVE, TEXT_WHITE, lambda: press_num("."))
dot_btn.grid(row=4, column=2, sticky="nsew")

eq_btn = AppleButton(grid_frame, "=", OP_BG, OP_ACTIVE, TEXT_WHITE, equal_press)
eq_btn.grid(row=4, column=3, sticky="nsew")


def on_key(event):
    key = event.keysym
    char = event.char
    if char in "0123456789.":
        press_num(char)
    elif char in "+-*/":
        symbol_map = {"/": "÷", "*": "×", "-": "−", "+": "+"}
        press_op(symbol_map[char])
    elif key in ("Return", "KP_Enter") or char == "=":
        equal_press()
    elif key == "Escape":
        clear_all()
    elif key == "BackSpace":
        global expression
        expression = expression[:-1]
        update_screen(expression)


root.bind("<Key>", on_key)
root.mainloop()