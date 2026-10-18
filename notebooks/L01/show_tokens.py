import tokenize
import io
import keyword


def show_tokens(code):
    code_bytes = io.BytesIO(code.encode('utf-8'))
    tokens = tokenize.tokenize(code_bytes.readline)

    print(f"{'Token-Typ':<15} | {'Wert im Code':<15}")
    print("-" * 35)

    for t in tokens:
        if t.type in (tokenize.ENCODING, tokenize.ENDMARKER):
            continue

        typ_name = tokenize.tok_name[t.type]
        value = t.string
        if typ_name == 'NAME' and keyword.iskeyword(t.string):
            typ_name = 'KEYWORD'
        if typ_name == 'OP' and t.string in '()[]{}:;,':
            typ_name = 'PUNCTUATOR'
        if typ_name in ('NEWLINE', 'NL', 'INDENT', 'DEDENT'):
            value = repr(value)
        print(f"{typ_name:<15}| {value}")

