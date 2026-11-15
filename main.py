# main.py - Genera el HTML coloreado y la tabla de métricas
# Uso: python main.py [archivo.gd] [salida.html]
# Sin argumentos procesa los .gd de la carpeta pruebas

import sys
import os
import html
from lexer import tokenize

# tipos de token en el orden en que se muestran en la leyenda
TIPOS = (
    'GODOT_NODE', 'GODOT_ANNOTATION', 'KEYWORD', 'IDENTIFIER', 'NUMBER',
    'STRING', 'COMMENT', 'OPERATOR', 'PUNCTUATION', 'ERROR_LEXICO',
)

# estilos de la página, una clase por tipo de token
ESTILOS = '''
body { background: #1d2229; color: #cdcfd2; font-family: "Segoe UI", Roboto, Arial, sans-serif; margin: 30px; }
h1, h2 { color: #ffffff; }
pre { background: #262c35; padding: 16px; border-radius: 6px; overflow-x: auto;
      font-family: Consolas, "DejaVu Sans Mono", "Courier New", monospace;
      font-size: 15px; line-height: 1.45; tab-size: 4; counter-reset: linea; }
.linea::before { counter-increment: linea; content: counter(linea); display: inline-block;
                 width: 5ch; margin-right: 3ch; text-align: right; color: #5b6370; }
.keyword { color: #ff7085; font-weight: bold; }
.identifier { color: #6cb6ff; }
.number { color: #a1ffe0; }
.string { color: #ffeda1; }
.comment { color: #8b929c; font-style: italic; }
.operator { color: #c9a3ff; }
.punctuation { color: #ff9de2; }
.godot_node { color: #63c259; font-weight: bold; }
.godot_annotation { color: #ffb373; }
.error_lexico { background: #e0201b; color: #ffffff; font-weight: bold; border-radius: 2px; }
.leyenda { line-height: 2; }
.leyenda span { margin-right: 8px; padding: 2px 6px; white-space: nowrap; }
table { border-collapse: collapse; font-size: 15px; }
th, td { border: 1px solid #4a525e; padding: 8px 16px; text-align: left; }
th { background: #363d4a; color: #ffffff; }
td:last-child { text-align: right; font-weight: bold; }
'''


def codigo_a_html(codigo, toks):
    # cada token es (tipo, valor, linea, posicion)
    partes = []
    pos = 0
    for tipo, valor, linea, inicio in toks:
        # espacios, tabs y saltos de linea entre tokens se copian del texto original
        partes.append(html.escape(codigo[pos:inicio]))
        ayuda = ''
        if tipo == 'ERROR_LEXICO':
            # tooltip con la línea del error
            ayuda = f' title="Error l&eacute;xico: car&aacute;cter no v&aacute;lido (l&iacute;nea {linea})"'
        partes.append(f'<span class="{tipo.lower()}"{ayuda}>{html.escape(valor)}</span>')
        pos = inicio + len(valor)
    partes.append(html.escape(codigo[pos:]))
    lineas = ''.join(partes).split('\n')
    if lineas[-1] == '':
        lineas.pop()
    return '\n'.join(f'<span class="linea">{linea}</span>' for linea in lineas)


def calcular_metricas(toks):
    # se cuenta sobre la lista de tokens
    nodos = sum(1 for tok in toks if tok[0] == 'GODOT_NODE')
    variables = sum(1 for tok in toks if tok[0] == 'KEYWORD' and tok[1] == 'var')
    anotaciones = sum(1 for tok in toks if tok[0] == 'GODOT_ANNOTATION')
    errores = sum(1 for tok in toks if tok[0] == 'ERROR_LEXICO')
    return [
        ('Total de nodos referenciados (tokens $)', nodos),
        ('Total de variables declaradas (var)', variables),
        ('Total de anotaciones (@)', anotaciones),
        ('Total de variables/anotaciones detectadas', variables + anotaciones),
        ('Total de errores l&eacute;xicos encontrados', errores),
        ('Total de tokens', len(toks)),
    ]


def generar_html(nombre, codigo, toks):
    leyenda = ' '.join(f'<span class="{tipo.lower()}">{tipo}</span>' for tipo in TIPOS)
    filas = ''.join(f'<tr><td>{texto}</td><td>{valor}</td></tr>' for texto, valor in calcular_metricas(toks))
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Resultado - {html.escape(nombre)}</title>
<style>{ESTILOS}</style>
</head>
<body>
<h1>Analizador l&eacute;xico Mini-GDScript</h1>
<p>Archivo analizado: <b>{html.escape(nombre)}</b></p>
<p class="leyenda">{leyenda}</p>
<pre>{codigo_a_html(codigo, toks)}</pre>
<h2>Tabla de m&eacute;tricas l&eacute;xicas</h2>
<table>
<tr><th>M&eacute;trica</th><th>Cantidad</th></tr>
{filas}
</table>
</body>
</html>
'''


def procesar(ruta_gd, ruta_html):
    # utf-8-sig por si el archivo viene con BOM
    with open(ruta_gd, encoding='utf-8-sig', errors='replace') as archivo:
        codigo = archivo.read()
    toks = tokenize(codigo)
    for tok in toks:
        print(f'<{tok[0]}>: {tok[1]}')
    with open(ruta_html, 'w', encoding='utf-8') as archivo:
        archivo.write(generar_html(os.path.basename(ruta_gd), codigo, toks))
    print(f'HTML generado: {ruta_html}\n')


def main():
    # para que la consola de Windows no falle con ¡ o ¿
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    # con argumentos: python main.py archivo.gd [salida.html]
    if len(sys.argv) > 1:
        ruta_gd = sys.argv[1]
        if not os.path.isfile(ruta_gd):
            sys.exit(f'Error: no se encontró el archivo "{ruta_gd}".')
        ruta_html = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(ruta_gd)[0] + '.html'
        procesar(ruta_gd, ruta_html)
        return
    # sin argumentos procesa todos los .gd de la carpeta pruebas
    base = os.path.dirname(os.path.abspath(__file__))
    carpeta_pruebas = os.path.join(base, 'pruebas')
    carpeta_resultados = os.path.join(base, 'resultados')
    if not os.path.isdir(carpeta_pruebas):
        sys.exit('Error: no existe la carpeta "pruebas". Uso: python main.py archivo.gd [salida.html]')
    archivos = sorted(nombre for nombre in os.listdir(carpeta_pruebas) if nombre.endswith('.gd'))
    if not archivos:
        sys.exit('Error: la carpeta "pruebas" no contiene archivos .gd.')
    os.makedirs(carpeta_resultados, exist_ok=True)
    for nombre in archivos:
        ruta_html = os.path.join(carpeta_resultados, nombre[:-3] + '.html')
        procesar(os.path.join(carpeta_pruebas, nombre), ruta_html)


if __name__ == '__main__':
    main()
