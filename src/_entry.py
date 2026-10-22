"""Entry point para el ejecutable standalone de SceneCutBatch.

Sin argumentos de línea de comandos, lanza la interfaz gráfica (GUI).
Con argumentos, lanza la CLI (mismo comportamiento que `scenecutbatch <args>`).

Al importar `scenecutbatch.cli` como paquete (en lugar de ejecutar cli.py
como script principal), las importaciones relativas (`from . import ...`)
funcionan correctamente.
"""

import sys

from scenecutbatch.cli import main as cli_main
from scenecutbatch.gui import main as gui_main


def main() -> None:
    # sys.argv[0] es el nombre del programa; si no hay más argumentos,
    # asumimos que el usuario hizo doble clic y lanzamos la GUI.
    if len(sys.argv) <= 1:
        gui_main()
    else:
        cli_main()


main()
