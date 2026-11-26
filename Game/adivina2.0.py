import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path


class JuegoAdivinaNumero:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Adivina el Número")
        self.root.geometry("560x640")
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
        self.numero_secreto = random.randint(1, 100)
        self.intentos = 0
        self.juego_activo = False
        self.mejor_puntaje = None
        self.mejor_jugador = None
        self.historial_ganadas = []

        self._cargar_historial()
        self._construir_interfaz()
        self._actualizar_estadisticas_ui()

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
        header.pack(fill="x", padx=24, pady=(16, 8))

        tk.Label(
            header,
            text="ADIVINA EL NÚMERO",
            font=("Segoe UI", 21, "bold"),
            bg=self.bg_main,
            fg=self.accent_cyan,
        ).pack()

        tk.Label(
            header,
            text="Pienso un número del 1 al 100. Menos intentos = mejor puntaje.",
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
        card_jugador.pack(fill="x", padx=24, pady=6)

        fila_superior = tk.Frame(card_jugador, bg=self.bg_card)
        fila_superior.pack(fill="x", padx=16, pady=(10, 4))

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
        fila_nombre.pack(fill="x", padx=16, pady=(0, 8))

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
        self.lbl_saludo.pack(anchor="w", padx=16, pady=(0, 10))

        card_juego = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_juego.pack(fill="x", padx=24, pady=6)

        controles_inicio = tk.Frame(card_juego, bg=self.bg_card)
        controles_inicio.pack(fill="x", padx=16, pady=(12, 6))

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
            text="Intentos: 0",
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
        self.lbl_pista.pack(padx=16, pady=(6, 12))

        card_historial = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_historial.pack(fill="both", expand=True, padx=24, pady=(6, 18))

        cabecera_hist = tk.Frame(card_historial, bg=self.bg_card)
        cabecera_hist.pack(fill="x", padx=16, pady=(10, 6))

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
        marco_lista.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        scrollbar = tk.Scrollbar(marco_lista)
        scrollbar.pack(side="right", fill="y")

        self.lista_historial = tk.Listbox(
            marco_lista,
            font=("Consolas", 10),
            bg=self.bg_input,
            fg=self.fg_text,
            selectbackground="#343B57",
            highlightthickness=0,
            relief="flat",
            yscrollcommand=scrollbar.set,
            height=6,
        )
        self.lista_historial.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        scrollbar.config(command=self.lista_historial.yview)

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

        self.numero_secreto = random.randint(1, 100)
        self.intentos = 0
        self.juego_activo = True

        self.entrada_numero.config(state="normal")
        self.entrada_numero.delete(0, tk.END)
        self.entrada_numero.focus()
        self.btn_adivinar.config(state="normal")

        self.lbl_intentos.config(text="Intentos: 0", fg=self.accent_cyan)
        self.lbl_pista.config(
            text=f"{self.nombre_jugador}, ya pensé un número entre 1 y 100. ¡Adivina!",
            fg=self.fg_text,
        )

    def _registrar_victoria(self):
        registro = {
            "jugador": self.nombre_jugador,
            "numero": self.numero_secreto,
            "intentos": self.intentos,
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
            unidad = "int." if item["intentos"] == 1 else "ints."
            linea = (
                f"#{idx:02d} | {item['hora']} | {item['jugador']} -> "
                f"#{item['numero']} en {item['intentos']} {unidad}"
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

    def comprobar_intento(self):
        if not self.juego_activo:
            return

        raw = self.entrada_numero.get().strip()
        self.entrada_numero.delete(0, tk.END)

        try:
            intento = int(raw)
        except ValueError:
            self.lbl_pista.config(
                text="Escribe un número entero válido (por ejemplo, 42).",
                fg=self.accent_pink,
            )
            return

        if intento < 1 or intento > 100:
            self.lbl_pista.config(
                text="El número debe estar entre 1 y 100.",
                fg=self.accent_pink,
            )
            return

        self.intentos += 1
        self.lbl_intentos.config(text=f"Intentos: {self.intentos}")

        if intento < self.numero_secreto:
            self.lbl_pista.config(
                text=f"El número secreto es MAYOR que {intento}.",
                fg=self.accent_cyan,
            )
        elif intento > self.numero_secreto:
            self.lbl_pista.config(
                text=f"El número secreto es MENOR que {intento}.",
                fg=self.accent_cyan,
            )
        else:
            self.juego_activo = False
            self.entrada_numero.config(state="disabled")
            self.btn_adivinar.config(state="disabled")
            self._registrar_victoria()
            self.lbl_pista.config(
                text=(
                    f"¡Felicidades, {self.nombre_jugador}! Adivinaste el "
                    f"{self.numero_secreto} en {self.intentos} intentos."
                ),
                fg=self.accent_green,
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = JuegoAdivinaNumero(root)
    root.mainloop()