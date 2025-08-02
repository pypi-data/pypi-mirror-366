from .Cur import cursos  # cursos es la lista


def duracion():
    suma = int(0)
    for i in cursos:
        suma += i.duracion
    return suma
