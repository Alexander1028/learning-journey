import random
import tkinter as tk


class JuegoAdivinaNumero:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Adivina el Número")
        self.root.geometry("540x480")
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

        self.nombre_jugador = ""
        self.numero_secreto = random.randint(1, 100)
        self.intentos = 0
        self.juego_activo = False

        self._construir_interfaz()

    def _construir_interfaz(self):
        header = tk.Frame(self.root, bg=self.bg_main)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            header,
            text="ADIVINA EL NÚMERO",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent_cyan,
        ).pack()

        tk.Label(
            header,
            text="Pienso un número del 1 al 100. ¿Lo logras en pocos intentos?",
            font=("Segoe UI", 11),
            bg=self.bg_main,
            fg=self.fg_muted,
        ).pack(pady=(4, 0))

        card_jugador = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_jugador.pack(fill="x", padx=24, pady=8)

        tk.Label(
            card_jugador,
            text="Jugador",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_card,
            fg=self.fg_muted,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        fila_nombre = tk.Frame(card_jugador, bg=self.bg_card)
        fila_nombre.pack(fill="x", padx=16, pady=(0, 10))

        self.entrada_nombre = tk.Entry(
            fila_nombre,
            font=("Segoe UI", 11),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.accent_cyan,
            relief="flat",
        )
        self.entrada_nombre.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
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
            pady=5,
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
            pady=5,
            command=self.limpiar_nombre,
        ).pack(side="left")

        self.lbl_saludo = tk.Label(
            card_jugador,
            text="Registra tu nombre para comenzar.",
            font=("Segoe UI", 10),
            bg=self.bg_card,
            fg=self.accent_green,
        )
        self.lbl_saludo.pack(anchor="w", padx=16, pady=(0, 12))

        card_juego = tk.Frame(
            self.root,
            bg=self.bg_card,
            highlightbackground="#2E354D",
            highlightthickness=1,
        )
        card_juego.pack(fill="both", expand=True, padx=24, pady=(6, 20))

        controles_inicio = tk.Frame(card_juego, bg=self.bg_card)
        controles_inicio.pack(fill="x", padx=16, pady=(14, 8))

        self.btn_comenzar = tk.Button(
            controles_inicio,
            text="Comenzar / Reiniciar partida",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_pink,
            fg="#FFFFFF",
            activebackground="#FF6AA6",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
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
        fila_intento.pack(fill="x", padx=16, pady=8)

        self.entrada_numero = tk.Entry(
            fila_intento,
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.accent_pink,
            relief="flat",
            state="disabled",
        )
        self.entrada_numero.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
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
            padx=16,
            pady=6,
            state="disabled",
            command=self.comprobar_intento,
        )
        self.btn_adivinar.pack(side="left")

        self.lbl_pista = tk.Label(
            card_juego,
            text="Pulsa 'Comenzar / Reiniciar partida' para generar el número secreto.",
            font=("Segoe UI", 11),
            bg=self.bg_card,
            fg=self.fg_text,
            wraplength=450,
            justify="center",
        )
        self.lbl_pista.pack(expand=True, padx=16, pady=(6, 16))

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