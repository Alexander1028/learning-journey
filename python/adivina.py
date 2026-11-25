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