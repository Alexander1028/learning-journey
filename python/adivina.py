import tkinter as tk

ventana = tk.Tk()
ventana.title("Adivina el Número")
ventana.geometry("600x400")
ventana.configure(bg="#202020")
ventana.resizable(False, False)

titulo = tk.Label(
    ventana,
    text="¡Bienvenido al juego de adivinanza!", 
    font=("Arial", 20, "bold"), 
    bg="#202020", 
    fg="#FFFFFF"
)
titulo.pack(pady=20)

entrada_nombre = tk.Entry(
    ventana,
    font=("Arial", 12),
    width=30,
)    
entrada_nombre.pack(pady=10)
entrada_nombre.insert(0, "Escribe tu nombre")

def mostrar_nombre():
    nombre = entrada_nombre.get()
    
    resultado.config(
        text=f"¡Hola, {nombre}! ¡Buena suerte adivinando el número!"
    )

resultado = tk.Label(
    ventana,
    text="Aquí aparecerá tu nombre.",
    font=("Arial", 12),
    fg="00FF99",
    bg="#202020"
)


def limpiar():
        entrada_nombre.delete(0, tk.END)
        
boton = tk.Button(
    ventana,
    text="Limpiar campo",
    command=limpiar,
)
boton.pack(pady=15)
ventana.mainloop()











def saludar():
    mensaje.config(text="¡Hola! Bienvenido al juego de adivinanza.")
    
mensaje = tk.Label(
    ventana,
    text="Presiona el botón para comenzar el juego.",
    font=("Arial", 12), 
    fg="#FFFFFF",
    bg="#202020"
)
mensaje.pack(pady=30)

boton = tk.Button(
    ventana,
    text="Comenzar",
    command=saludar,
    font=("Arial", 12, "bold"),
    bg="#00FF99",
    fg="#202020",
)
boton.pack()



descripcion = tk.Label(
    ventana, 
    text="Estoy pensando en un número entre 1 y 100. ¿Puedes adivinar cuál es?", 
    font=("Arial", 12), 
    bg="#202020", 
    fg="#00FF99")

descripcion.pack()






























import random 

numero = random.randint(1, 100)
intentos = 0

print("¡Bienvenido al juego de adivinanza!")
print("Estoy pensando en un número entre 1 y 100. ¿Puedes adivinar cuál es?")

while True:
    intento = int(input("Adivina el número: "))
    intentos += 1

    if intento < numero:
        print("El número es mayor.")
    elif intento > numero:
        print("El número es menor.")
    else:
        print(f"¡Felicidades! Adivinaste el número en {intentos} intentos.")
        break