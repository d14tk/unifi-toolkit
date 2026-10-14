import sys, re, json, os
from html.parser import HTMLParser

root = sys.argv[1]
out = sys.argv[2]
strings = {}
BS = chr(92)


def add(s, src, code=False):
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.lstrip('.,;:)–— ')
    if not s or not re.search(r'[A-Za-z]{2}', s):
        return
    if ' ' not in s and re.fullmatch(r'[\w\-\.#:/]+', s) and not re.fullmatch(r'[A-Z][a-z]+:?', s):
        return
    if s.startswith(('http', '/', '#', '.', 'data:')) or '{%' in s:
        return
    if code and '${' not in s and re.search(r'[;{}=]|=>|\(\)|\.\w+\(', s):
        return
    if len(s) > 400:
        return
    strings.setdefault(s, set()).add(src)


ATTRS = {'title', 'placeholder', 'aria-label', 'alt', 'data-tooltip', 'label'}


class P(HTMLParser):
    def __init__(s, src):
        super().__init__(convert_charrefs=True)
        s.src = src
        s.skip = 0
        s.scripts = []
        s.cur = None

    def handle_starttag(s, tag, attrs):
        if tag == 'style':
            s.skip += 1
        if tag == 'script':
            s.cur = []
        for k, v in attrs:
            if v is None:
                continue
            if k in ATTRS:
                add(v, s.src)
            if k in ('x-text', ':title', ':placeholder', 'x-html', ':aria-label'):
                for m in re.finditer(r"'([^']*)'|`([^`]*)`", v):
                    add(m.group(1) or m.group(2) or '', s.src)

    def handle_endtag(s, tag):
        if tag == 'style':
            s.skip -= 1
        if tag == 'script' and s.cur is not None:
            s.scripts.append(''.join(s.cur))
            s.cur = None

    def handle_data(s, d):
        if s.cur is not None:
            s.cur.append(d)
            return
        if s.skip:
            return
        for part in re.split(r'\{\{.*?\}\}|\{%.*?%\}', d):
            add(part, s.src)


def literals(text):
    """Yield JS string literal contents (', ", `) with a small scanner."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            j = text.find('\n', i)
            i = n if j < 0 else j
            continue
        if c == '/' and i + 1 < n and text[i + 1] == '*':
            j = text.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "'\"`":
            q = c
            j = i + 1
            buf = []
            while j < n and text[j] != q:
                if text[j] == BS:
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                if q != '`' and text[j] == '\n':
                    break
                buf.append(text[j])
                j += 1
            yield ''.join(buf)
            i = j + 1
            continue
        i += 1


def js(text, src):
    for lit in literals(text):
        if '<' in lit and '>' in lit:
            p = P(src)
            p.feed(lit)
        else:
            if not re.search(r'[A-Za-z]{3}', lit):
                continue
            if re.fullmatch(r'[a-z_\-\.]+', lit):
                continue
            add(lit, src, code=True)


for dp, dn, fn in os.walk(root):
    if 'tests' in dp or '.git' in dp:
        continue
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, root)
        if f.endswith('.html') and 'templates' in dp:
            h = P(rel)
            h.feed(open(p, encoding='utf-8').read())
            for sc in h.scripts:
                js(sc, rel)
        elif f.endswith('.js') and 'static' in dp and not f.endswith('.min.js'):
            js(open(p, encoding='utf-8').read(), rel)

import ast


def pystrings(path, rel):
    tree = ast.parse(open(path, encoding='utf-8').read())
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], 'value', None), ast.Constant):
                docs.add(id(node.body[0].value))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ('debug', 'info', 'warning', 'error', 'exception', 'critical'):
            for a in ast.walk(node):
                docs.add(id(a))
    for node in ast.walk(tree):
        if id(node) in docs:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for v in node.values:
                parts.append(v.value if isinstance(v, ast.Constant) else '${' + ast.unparse(v.value) + '}')
            s = ''.join(parts)
        else:
            continue
        if ' ' in s.strip() and re.search(r'[A-Za-z]{3}', s) and not re.search(r'SELECT |INSERT |CREATE |sqlite|/api/|%\(|\{\}', s):
            add(s, rel, code=True if '${' not in s and re.search(r'[{}=]|=>', s) else False)


for dp, dn, fn in os.walk(root):
    if 'tests' in dp or '.git' in dp or 'alembic' in dp:
        continue
    for f in fn:
        if f.endswith('.py') and (dp.startswith(os.path.join(root, 'tools')) or dp.startswith(os.path.join(root, 'app'))):
            pystrings(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), root))

json.dump({k: sorted(v) for k, v in sorted(strings.items())}, open(out, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)
print(len(strings))
