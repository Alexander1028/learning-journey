import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path


NIVELES = {
    "Fácil": {"min": 1, "max": 50, "max_intentos": 10},
    "Medio": {"min": 1, "max": 100, "max_intentos": 7},
    "Difícil": {"min": 1, "max": 200, "max_intentos": 6},
}


class JuegoAdivinaNumero:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Adivina el Número")
        self.root.geometry("560x690")
        self.root.configure(bg="#12141D")
        self.root.resizable(False, False)

        self.bg_main = "#12141D"
        self.bg_card = "#1C2030"
        self.bg_input = "#262B40"
        self.fg_text = "#F4F6FB"
        self.fg_muted = "#9AA3B8"
        self.accent_cyan = "#00E5FF"
        self.accent_pink = "#FF3E8A"
        self.accent_green = "#00F59B"
        self.accent_purple = "#B366FF"

        self.ruta_historial = Path(__file__).resolve().parent / "historial_partidas.json"

        self.nombre_jugador = ""
        self.dificultad_actual = tk.StringVar(value="Medio")
        self.rango_min = NIVELES["Medio"]["min"]
        self.rango_max = NIVELES["Medio"]["max"]
        self.max_intentos = NIVELES["Medio"]["max_intentos"]
        self.numero_secreto = random.randint(self.rango_min, self.rango_max)
        self.intentos = 0
        self.juego_activo = False
        self.mejor_puntaje = None
        self.mejor_jugador = None
        self.historial_ganadas = []

        self._cargar_historial()
        self._construir_interfaz()
        self._actualizar_estadisticas_ui()
        self._aplicar_dificultad()

    def _cargar_historial(self):
        if not self.ruta_historial.exists():
            return
        try:
            data = json.loads(self.ruta_historial.read_text(encoding="utf-8"))
            self.historial_ganadas = data.get("ganadas", [])
            self._recalcular_mejor_puntaje()
        except (json.JSONDecodeError, OSError):
            self.historial_ganadas = []

    def _guardar_historial(self):
        payload = {"ganadas": self.historial_ganadas}
        try:
            self.ruta_historial.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _recalcular_mejor_puntaje(self):
        if not self.historial_ganadas:
            self.mejor_puntaje = None
            self.mejor_jugador = None
            return

        mejor = min(self.historial_ganadas, key=lambda item: item["intentos"])
        self.mejor_puntaje = mejor["intentos"]
        self.mejor_jugador = mejor["jugador"]

    def _construir_interfaz(self):
        header = tk.Frame(self.root, bg=self.bg_main)
        header.pack(fill="x", padx=24, pady=(14, 6))

        tk.Label(
            header,
            text="ADIVINA EL NÚMERO",
            font=("Segoe UI", 21, "bold"),
            bg=self.bg_main,
            fg=self.accent_cyan,
        ).pack()

        self.lbl_subtitulo = tk.Label(
            header,
            text="Elige una dificultad y adivina en el menor número de intentos.",
            font=("Segoe UI", 10),
            bg=self.bg_main,
            fg=self.fg_muted,
        ).pack(pady=(2, 0))

        card_jugador = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_jugador.pack(fill="x", padx=24, pady=5)

        fila_superior = tk.Frame(card_jugador, bg=self.bg_card)
        fila_superior.pack(fill="x", padx=16, pady=(9, 4))

        tk.Label(
            fila_superior,
            text="Jugador",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.fg_muted,
        ).pack(side="left")

        self.lbl_mejor_puntaje = tk.Label(
            fila_superior,
            text="Mejor puntaje: --",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.accent_purple,
        )
        self.lbl_mejor_puntaje.pack(side="right")

        fila_nombre = tk.Frame(card_jugador, bg=self.bg_card)
        fila_nombre.pack(fill="x", padx=16, pady=(0, 6))

        self.entrada_nombre = tk.Entry(
            fila_nombre,
            font=("Segoe UI", 11),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.accent_cyan,
            relief="flat",
        )
        self.entrada_nombre.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        self.entrada_nombre.insert(0, "Escribe tu nombre")
        self.entrada_nombre.bind("<FocusIn>", self._limpiar_placeholder_nombre)

        tk.Button(
            fila_nombre,
            text="Guardar",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_cyan,
            fg="#12141D",
            activebackground="#66EEFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.registrar_nombre,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            fila_nombre,
            text="Limpiar",
            font=("Segoe UI", 10),
            bg=self.bg_input,
            fg=self.fg_text,
            activebackground="#343B57",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.limpiar_nombre,
        ).pack(side="left")

        self.lbl_saludo = tk.Label(
            card_jugador,
            text="Registra tu nombre para comenzar.",
            font=("Segoe UI", 10),
            bg=self.bg_card,
            fg=self.accent_green,
        )
        self.lbl_saludo.pack(anchor="w", padx=16, pady=(0, 9))

        card_juego = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_juego.pack(fill="x", padx=24, pady=5)

        fila_dificultad = tk.Frame(card_juego, bg=self.bg_card)
        fila_dificultad.pack(fill="x", padx=16, pady=(10, 4))

        tk.Label(
            fila_dificultad,
            text="Dificultad:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.fg_muted,
        ).pack(side="left", padx=(0, 10))

        for nombre_nivel in NIVELES:
            tk.Radiobutton(
                fila_dificultad,
                text=nombre_nivel,
                variable=self.dificultad_actual,
                value=nombre_nivel,
                font=("Segoe UI", 10, "bold"),
                bg=self.bg_card,
                fg=self.fg_text,
                selectcolor=self.bg_input,
                activebackground=self.bg_card,
                activeforeground=self.accent_cyan,
                cursor="hand2",
                command=self._aplicar_dificultad,
            ).pack(side="left", padx=(0, 12))

        self.lbl_info_nivel = tk.Label(
            card_juego,
            text="Rango: 1 a 100 | Límite: 7 intentos",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_card,
            fg=self.accent_cyan,
        )
        self.lbl_info_nivel.pack(anchor="w", padx=16, pady=(0, 6))

        controles_inicio = tk.Frame(card_juego, bg=self.bg_card)
        controles_inicio.pack(fill="x", padx=16, pady=(2, 6))

        self.btn_comenzar = tk.Button(
            controles_inicio,
            text="Comenzar / Reiniciar partida",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_pink,
            fg="#FFFFFF",
            activebackground="#FF6AA6",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.iniciar_partida,
        )
        self.btn_comenzar.pack(side="left")

        self.lbl_intentos = tk.Label(
            controles_inicio,
            text="Intentos: 0 / 7",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.fg_muted,
        )
        self.lbl_intentos.pack(side="right")

        fila_intento = tk.Frame(card_juego, bg=self.bg_card)
        fila_intento.pack(fill="x", padx=16, pady=6)

        self.entrada_numero = tk.Entry(
            fila_intento,
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.accent_pink,
            relief="flat",
            state="disabled",
        )
        self.entrada_numero.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        self.entrada_numero.bind("<Return>", lambda _event: self.comprobar_intento())

        self.btn_adivinar = tk.Button(
            fila_intento,
            text="Adivinar",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_green,
            fg="#12141D",
            activebackground="#5CFFB8",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=5,
            state="disabled",
            command=self.comprobar_intento,
        )
        self.btn_adivinar.pack(side="left")

        self.lbl_pista = tk.Label(
            card_juego,
            text="Pulsa 'Comenzar / Reiniciar partida' para generar el número secreto.",
            font=("Segoe UI", 10),
            bg=self.bg_card,
            fg=self.fg_text,
            wraplength=460,
            justify="center",
        )
        self.lbl_pista.pack(padx=16, pady=(6, 10))

        card_historial = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_historial.pack(fill="both", expand=True, padx=24, pady=(5, 16))

        cabecera_hist = tk.Frame(card_historial, bg=self.bg_card)
        cabecera_hist.pack(fill="x", padx=16, pady=(9, 4))

        tk.Label(
            cabecera_hist,
            text="Historial de partidas ganadas",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.fg_text,
        ).pack(side="left")

        tk.Button(
            cabecera_hist,
            text="Borrar historial",
            font=("Segoe UI", 9),
            bg=self.bg_input,
            fg=self.fg_muted,
            activebackground="#343B57",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.borrar_historial,
        ).pack(side="right")

        marco_lista = tk.Frame(card_historial, bg=self.bg_input)
        marco_lista.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        scrollbar = tk.Scrollbar(marco_lista)
        scrollbar.pack(side="right", fill="y")

        self.lista_historial = tk.Listbox(
            marco_lista,
            font=("Consolas", 9),
            bg=self.bg_input,
            fg=self.fg_text,
            selectbackground="#343B57",
            highlightthickness=0,
            relief="flat",
            yscrollcommand=scrollbar.set,
            height=5,
        )
        self.lista_historial.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        scrollbar.config(command=self.lista_historial.yview)

    def _aplicar_dificultad(self):
        nivel = self.dificultad_actual.get()
        cfg = NIVELES[nivel]
        self.rango_min = cfg["min"]
        self.rango_max = cfg["max"]
        self.max_intentos = cfg["max_intentos"]

        self.lbl_info_nivel.config(
            text=f"Rango: {self.rango_min} a {self.rango_max} | Límite: {self.max_intentos} intentos"
        )

        if self.juego_activo:
            self.juego_activo = False
            self.entrada_numero.config(state="disabled")
            self.btn_adivinar.config(state="disabled")
            self.lbl_pista.config(
                text=f"Dificultad cambiada a {nivel}. Pulsa 'Comenzar / Reiniciar partida'.",
                fg=self.accent_cyan,
            )

        self.lbl_intentos.config(text=f"Intentos: 0 / {self.max_intentos}", fg=self.fg_muted)

    def _limpiar_placeholder_nombre(self, _event):
        if self.entrada_nombre.get() == "Escribe tu nombre":
            self.entrada_nombre.delete(0, tk.END)

    def registrar_nombre(self):
        texto = self.entrada_nombre.get().strip()
        if not texto or texto == "Escribe tu nombre":
            self.nombre_jugador = "Jugador"
        else:
            self.nombre_jugador = texto
        self.lbl_saludo.config(
            text=f"¡Listo, {self.nombre_jugador}! Ya puedes jugar.",
            fg=self.accent_green,
        )

    def limpiar_nombre(self):
        self.entrada_nombre.delete(0, tk.END)
        self.nombre_jugador = ""
        self.lbl_saludo.config(
            text="Campo limpiado. Escribe tu nombre si quieres.",
            fg=self.fg_muted,
        )

    def iniciar_partida(self):
        if not self.nombre_jugador:
            self.registrar_nombre()

        self._aplicar_dificultad()
        self.numero_secreto = random.randint(self.rango_min, self.rango_max)
        self.intentos = 0
        self.juego_activo = True

        self.entrada_numero.config(state="normal")
        self.entrada_numero.delete(0, tk.END)
        self.entrada_numero.focus()
        self.btn_adivinar.config(state="normal")

        self.lbl_intentos.config(
            text=f"Intentos: 0 / {self.max_intentos}",
            fg=self.accent_cyan,
        )
        self.lbl_pista.config(
            text=(
                f"{self.nombre_jugador} ({self.dificultad_actual.get()}): "
                f"pienso un número entre {self.rango_min} y {self.rango_max}. "
                f"Tienes {self.max_intentos} intentos."
            ),
            fg=self.fg_text,
        )

    def _registrar_victoria(self):
        registro = {
            "jugador": self.nombre_jugador,
            "dificultad": self.dificultad_actual.get(),
            "numero": self.numero_secreto,
            "intentos": self.intentos,
            "max_intentos": self.max_intentos,
            "hora": datetime.now().strftime("%H:%M"),
        }
        self.historial_ganadas.insert(0, registro)
        self._recalcular_mejor_puntaje()
        self._guardar_historial()
        self._actualizar_estadisticas_ui()

    def _actualizar_estadisticas_ui(self):
        if self.mejor_puntaje is None:
            self.lbl_mejor_puntaje.config(text="Mejor puntaje: --")
        else:
            unidad = "intento" if self.mejor_puntaje == 1 else "intentos"
            self.lbl_mejor_puntaje.config(
                text=f"Mejor puntaje: {self.mejor_puntaje} {unidad} ({self.mejor_jugador})"
            )

        self.lista_historial.delete(0, tk.END)
        if not self.historial_ganadas:
            self.lista_historial.insert(tk.END, "Aún no hay partidas ganadas.")
            return

        for idx, item in enumerate(self.historial_ganadas, start=1):
            nivel = item.get("dificultad", "Medio")
            linea = (
                f"#{idx:02d} | {item['hora']} | [{nivel}] {item['jugador']} -> "
                f"#{item['numero']} ({item['intentos']} int.)"
            )
            self.lista_historial.insert(tk.END, linea)

    def borrar_historial(self):
        self.historial_ganadas.clear()
        self.mejor_puntaje = None
        self.mejor_jugador = None
        if self.ruta_historial.exists():
            try:
                self.ruta_historial.unlink()
            except OSError:
                pass
        self._actualizar_estadisticas_ui()

    def _finalizar_partida(self):
        self.juego_activo = False
        self.entrada_numero.config(state="disabled")
        self.btn_adivinar.config(state="disabled")

    def comprobar_intento(self):
        if not self.juego_activo:
            return

        raw = self.entrada_numero.get().strip()
        self.entrada_numero.delete(0, tk.END)

        try:
            intento = int(raw)
        except ValueError:
            self.lbl_pista.config(
                text="Escribe un número entero válido.",
                fg=self.accent_pink,
            )
            return

        if intento < self.rango_min or intento > self.rango_max:
            self.lbl_pista.config(
                text=f"El número debe estar entre {self.rango_min} y {self.rango_max}.",
                fg=self.accent_pink,
            )
            return

        self.intentos += 1
        restantes = self.max_intentos - self.intentos
        self.lbl_intentos.config(text=f"Intentos: {self.intentos} / {self.max_intentos}")

        if intento == self.numero_secreto:
            self._finalizar_partida()
            self._registrar_victoria()
            self.lbl_pista.config(
                text=(
                    f"¡Felicidades, {self.nombre_jugador}! Adivinaste el "
                    f"{self.numero_secreto} en {self.intentos} de {self.max_intentos} intentos."
                ),
                fg=self.accent_green,
            )
            return

        if self.intentos >= self.max_intentos:
            self._finalizar_partida()
            self.lbl_pista.config(
                text=(
                    f"¡Se acabaron los {self.max_intentos} intentos! "
                    f"El número secreto era {self.numero_secreto}."
                ),
                fg=self.accent_pink,
            )
            return

        direccion = "MAYOR" if intento < self.numero_secreto else "MENOR"
        plural = "intento" if restantes == 1 else "intentos"
        self.lbl_pista.config(
            text=(
                f"El número secreto es {direccion} que {intento}. "
                f"Te quedan {restantes} {plural}."
            ),
            fg=self.accent_cyan,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = JuegoAdivinaNumero(root)
    root.mainloop()