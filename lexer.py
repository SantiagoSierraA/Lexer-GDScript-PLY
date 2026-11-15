# lexer.py - Analizador léxico de Mini-GDScript con PLY
# Entrada : texto (el contenido de un .gd)
# Salida  : tokenize(texto) -> lista de tuplas (tipo, valor, linea, posicion)

try:
    import ply.lex as lex   # módulo de PLY
except ImportError:
    raise SystemExit("Falta la librería PLY. Instálela con:  pip install ply")


# PALABRAS RESERVADAS
RESERVED = {
    # las que pide el taller
    "var", "func", "if", "elif", "else", "for", "while",
    "pass", "return", "extends", "class_name",
    # literales
    "true", "false", "null",
    # otras de GDScript
    "in", "and", "or", "not", "is", "as", "break", "continue", "match",
    "const", "enum", "signal", "static", "class", "self", "super",
    "await", "void",
}

# LISTA DE TOKENS
tokens = (
    "GODOT_NODE",
    "GODOT_ANNOTATION",
    "KEYWORD",
    "IDENTIFIER",
    "NUMBER",
    "STRING",
    "COMMENT",
    "OPERATOR",
    "PUNCTUATION",
    "ERROR_LEXICO",
)

# REGLAS
# En cada regex la alternativa más larga va primero (decimal antes que
# entero, == antes que =), porque se toma la primera que calza.

def t_COMMENT(t):
    r"\#[^\n]*"          # '#' + todo, menos salto de línea
    return t


def t_STRING(t):
    r"\"([^\"\\\n]|\\.)*\"|'([^'\\\n]|\\.)*'"
    # "xyz" o 'xyz' en una sola línea y cerrado, puede traer escapes (\")
    return t


def t_GODOT_NODE(t):
    r"\$[A-Za-z0-9_/]+"  # '$' + 1 o más letras, dígitos, _ o /
    return t


def t_GODOT_ANNOTATION(t):
    r"@[A-Za-z0-9_]+"    # '@' + 1 o más letras, dígitos o _
    return t


def t_NUMBER(t):
    r"\d+\.\d+|\d+"      # decimal primero, si no, entero (42)
    return t


def t_IDENTIFIER(t):
    r"[A-Za-z_][A-Za-z0-9_]*"   # una palabra (empieza con letra o _)
    # Si la palabra está en RESERVED, cambiamos el tipo a KEYWORD.
    if t.value in RESERVED:
        t.type = "KEYWORD"
    return t


# Los operadores de 2 caracteres van antes que los de 1
def t_OPERATOR(t):
    r"->|==|!=|<=|>=|\+=|-=|\*=|/=|%=|&&|\|\||\+|-|\*|/|%|=|<|>|!"
    return t


def t_PUNCTUATION(t):
    r"[:,.()\[\]{}]"     # un carácter de la lista
    return t


# salto de línea: solo suma al contador de líneas
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# caracteres que se saltan en silencio entre tokens,
# los espacios y tabs no aparecen como tokens.
t_ignore = " \t\r"


# cuando NINGUNA regla calza en la posición
# actual. Para evitar que el programa se detenga en el fallo.
def t_error(t):
    t.type = "ERROR_LEXICO"
    # Al llamarse t_error, PLY pone en t.value TODO el texto que falta por
    # leer. Nos quedamos solo con el primer carácter (el inválido).
    t.value = t.value[0]
    # Avanzar un carácter es OBLIGATORIO: si no, PLY queda atascado en el
    # mismo punto y lanza error.
    t.lexer.skip(1)
    return t             # lo devolvemos para que salga en el HTML en rojo


# CONSTRUIR EL LEXER
# lex.lex() revisa este archivo, junta todas las reglas t_ en ese orden en una
# sola expresión regular grande y devuelve el lexer ya armado.
lexer = lex.lex()


# Función publica

def tokenize(texto):
    lexer.input(texto)    # carga el texto en el lexer y parte desde el inicio
    lexer.lineno = 1      # vuelve a contar las líneas desde 1
    # Por cada token, mandamos una tupla con sus 4 respectivos datos
    resultado = []
    for tok in lexer:
        resultado.append((tok.type, tok.value, tok.lineno, tok.lexpos))
    return resultado
