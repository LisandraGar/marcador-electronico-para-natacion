from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
import displayio
import terminalio

# Configurar la pantalla
matrix = Matrix(width=64, height=32)
display = matrix.display

# Función para mostrar texto en la matriz
def show_text(texto, x=0, y=8, color=0xFFFFFF, escala=2):
    # Crear grupo y texto
    grupo = displayio.Group()
    texto_label = label.Label(
        terminalio.FONT,
        text=texto,
        color=color,
        scale=escala
    )
    texto_label.x = x
    texto_label.y = y
    grupo.append(texto_label)

    # Mostrar en pantalla
    display.root_group = grupo