class Cursos:
    def __init__(self, name, duracion, link) -> None:
        self.name = name
        self.duracion = duracion
        self.link = link
        pass

    def __str__(self) -> str:
        return f"Curso: {self.name}, Duracion: {self.duracion}, Link: {self.link}"

    def __repr__(self) -> str:
        return f"Curso: {self.name}, Duracion: {self.duracion}, Link: {self.link}"


cursos = [
    Cursos("Linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/11149/"),
    Cursos("Python", 35, "https://hack4u.io/cursos/python-ofensivo/"),
    Cursos("Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/"),
]


def listar():
    for i in cursos:
        print(i)


def serch(nombre):
    bandera = False
    for i in cursos:
        if nombre == i.name:
            bandera = True
            return f"El curso de {i.name}, dura: {i.duracion}, y el link es: {i.link}"
            break

    if bandera == False:
        return f"Curso no registrado"
