import ast
import operator

import flet as ft

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluar_expresion(expresion: str) -> float:
    """Evalua una expresion aritmetica sin usar eval() ni exec()."""
    arbol = ast.parse(expresion, mode="eval")

    def recorrer(nodo):
        if isinstance(nodo, ast.Expression):
            return recorrer(nodo.body)
        if isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
                raise ValueError("Solo se permiten numeros")
            return nodo.value
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERADORES:
            return OPERADORES[type(nodo.op)](recorrer(nodo.left), recorrer(nodo.right))
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in OPERADORES:
            return OPERADORES[type(nodo.op)](recorrer(nodo.operand))
        raise ValueError("Operacion no permitida")

    return recorrer(arbol)


def main(page: ft.Page):
    page.title = "Pract 2 - Calculadora (Flet)"
    page.window.width = 420
    page.window.height = 680
    page.window.resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    historial_lista = []
    en_estado_error = False

    # Pantalla principal
    display = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        read_only=True,
        text_size=28,
        height=60,
        border=ft.OutlineInputBorder(side=ft.BorderSide(color=ft.Colors.BLUE_400)),
    )

    # Area de historial
    historial_text = ft.Text(
        value="Sin operaciones",
        size=12,
        color=ft.Colors.GREY_400,
    )

    def actualizar_historial(operacion):
        historial_lista.append(operacion)
        if len(historial_lista) > 5:
            historial_lista.pop(0)
        historial_text.value = "\n".join(historial_lista)
        page.update()

    def btn_click(e):
        nonlocal en_estado_error
        texto = e.control.data

        if texto == "C":
            display.value = ""
            display.read_only = True
            en_estado_error = False
        elif en_estado_error:
            # Obliga a presionar C si hay un error
            return
        elif texto == "CE":
            display.value = display.value[:-1]
        elif texto == "=":
            if not display.value:
                return
            try:
                res = evaluar_expresion(display.value)
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                res_str = str(res)
                actualizar_historial(f"{display.value} = {res_str}")
                display.value = res_str
            except Exception:
                display.value = "Error"
                en_estado_error = True
        elif texto == "Info":
            abrir_info()
        else:
            display.value += texto

        page.update()

    # Flet 1.0 apila los dialogos y solo los retira cuando el cliente confirma
    # el cierre; este flag evita apilar dos si se hace doble clic en "Info".
    dialogo_montado = False

    def cerrar_dialogo(e):
        page.pop_dialog()
        page.update()

    def abrir_info():
        nonlocal dialogo_montado
        if dialogo_montado:
            return
        dialogo_montado = True

        def al_cerrar(e):
            nonlocal dialogo_montado
            dialogo_montado = False

        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Información"),
            content=ft.Text("Calculadora v2.0\nAutor: Jaquelin Cielo V.\nLibrería: Flet"),
            actions=[ft.TextButton(content="Cerrar", on_click=cerrar_dialogo)],
            on_dismiss=al_cerrar,
        ))

    # Definicion de botones con colores diferenciados
    botones = [
        [("C", ft.Colors.RED_700), ("CE", ft.Colors.ORANGE_800), ("/", ft.Colors.BLUE_GREY_700), ("*", ft.Colors.BLUE_GREY_700)],
        [("7", None), ("8", None), ("9", None), ("-", ft.Colors.BLUE_GREY_700)],
        [("4", None), ("5", None), ("6", None), ("+", ft.Colors.BLUE_GREY_700)],
        [("1", None), ("2", None), ("3", None), ("=", ft.Colors.BLUE_700)],
        [("0", None), (".", None), ("Info", ft.Colors.PURPLE_800)],
    ]

    grid_botones = []
    for fila in botones:
        controles_fila = []
        for texto, color in fila:
            # Ajustar expansion especial para botones en la ultima fila
            exp = 2 if texto in ["0", "."] else 1
            btn = ft.Button(
                content=texto,
                data=texto,
                on_click=btn_click,
                height=55,
                bgcolor=color,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                ),
                expand=exp,
            )
            controles_fila.append(btn)
        grid_botones.append(ft.Row(controls=controles_fila, spacing=8))

    # Estructura contenida dentro de una tarjeta fija
    tarjeta_calculadora = ft.Container(
        width=360,
        padding=15,
        border_radius=12,
        bgcolor=ft.Colors.GREY_900,
        content=ft.Column(
            controls=[
                ft.Text("Calculadora con Historial", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                display,
                ft.Text("Últimas 5 operaciones:", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300),
                ft.Container(
                    content=historial_text,
                    padding=8,
                    border=ft.Border.all(1, ft.Colors.GREY_700),
                    border_radius=6,
                    height=80,
                    width=330,
                    bgcolor=ft.Colors.BLACK,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                *grid_botones,
            ],
            spacing=8,
        ),
    )

    page.add(tarjeta_calculadora)


if __name__ == "__main__":
    ft.run(main)
