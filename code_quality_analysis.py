#!/usr/bin/env python3
"""
Code-Qualitäts-Analyse für Trading Tools
"""

import ast
import os

def analyze_code_quality(filename):
    """Analysiere Code-Qualität einer Python-Datei"""
    print(f"\n{'='*70}")
    print(f"📝 ANALYSE: {filename}")
    print(f"{'='*70}")

    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
        lines = code.split('\n')

    # Metriken
    total_lines = len(lines)
    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    comment_lines = len([l for l in lines if l.strip().startswith('#')])
    blank_lines = len([l for l in lines if not l.strip()])

    print(f"\n📊 CODE METRIKEN:")
    print(f"   Gesamt Zeilen: {total_lines}")
    print(f"   Code Zeilen: {code_lines}")
    print(f"   Kommentar Zeilen: {comment_lines}")
    print(f"   Leerzeilen: {blank_lines}")
    print(f"   Kommentar-Ratio: {(comment_lines/code_lines*100):.1f}%")

    # AST Analyse
    try:
        tree = ast.parse(code)

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        print(f"\n🏗️  STRUKTUR:")
        print(f"   Klassen: {len(classes)}")
        print(f"   Funktionen/Methoden: {len(functions)}")

        if classes:
            print(f"\n   📦 Klassen:")
            for cls in classes:
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
                print(f"      - {cls.name} ({len(methods)} Methoden)")

        # Docstrings prüfen
        docstring_count = 0
        for node in classes + functions:
            if ast.get_docstring(node):
                docstring_count += 1

        total_documented = len(classes) + len(functions)
        if total_documented > 0:
            print(f"\n📚 DOKUMENTATION:")
            print(f"   Dokumentierte Elemente: {docstring_count}/{total_documented}")
            print(f"   Dokumentations-Rate: {(docstring_count/total_documented*100):.1f}%")

    except SyntaxError as e:
        print(f"   ❌ Syntax-Fehler: {e}")
        return False

    # Potentielle Probleme finden
    print(f"\n🔍 CODE-ANALYSE:")

    issues = []
    warnings = []

    # Check für hardcoded values
    if 'password' in code.lower() or 'api_key' in code.lower():
        issues.append("⚠️ Potentielle hardcoded credentials gefunden")

    # Check für Exception handling
    try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
    if try_blocks:
        print(f"   ✅ Exception Handling vorhanden ({len(try_blocks)} try/except)")
    else:
        warnings.append("⚠️ Kein Exception Handling gefunden")

    # Check für Type Hints
    functions_with_hints = 0
    for func in functions:
        if func.returns or any(arg.annotation for arg in func.args.args):
            functions_with_hints += 1

    if len(functions) > 0:
        hint_ratio = (functions_with_hints / len(functions)) * 100
        if hint_ratio > 50:
            print(f"   ✅ Type Hints: {functions_with_hints}/{len(functions)} ({hint_ratio:.1f}%)")
        else:
            warnings.append(f"⚠️ Wenige Type Hints: {functions_with_hints}/{len(functions)}")

    # Check für Magic Numbers
    magic_numbers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Num):
            if node.n not in [0, 1, 2, 100] and abs(node.n) > 1:
                magic_numbers.append(node.n)

    if len(magic_numbers) < 10:
        print(f"   ✅ Wenige Magic Numbers ({len(set(magic_numbers))} unique)")
    else:
        warnings.append(f"⚠️ Viele Magic Numbers gefunden ({len(set(magic_numbers))} unique)")

    # Ausgabe
    if issues:
        print(f"\n❌ KRITISCHE PROBLEME:")
        for issue in issues:
            print(f"   {issue}")

    if warnings:
        print(f"\n⚠️  WARNUNGEN:")
        for warning in warnings:
            print(f"   {warning}")

    if not issues and not warnings:
        print(f"   ✅ Keine Probleme gefunden!")

    return True

def check_security_issues(filename):
    """Prüfe auf Sicherheitsprobleme"""
    print(f"\n🔒 SICHERHEITS-CHECK:")

    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    security_issues = []

    # SQL Injection Check
    if 'execute(' in code and '%s' in code:
        security_issues.append("⚠️ Potentielle SQL-Injection möglich")

    # eval/exec Check
    if 'eval(' in code or 'exec(' in code:
        security_issues.append("❌ eval() oder exec() verwendet - Sicherheitsrisiko!")

    # pickle Check
    if 'pickle.loads' in code:
        security_issues.append("⚠️ pickle.loads() - Vorsicht bei untrusted data!")

    # Shell injection
    if 'os.system(' in code or 'subprocess.call' in code:
        security_issues.append("⚠️ Shell commands - Input validation prüfen!")

    if security_issues:
        for issue in security_issues:
            print(f"   {issue}")
    else:
        print(f"   ✅ Keine offensichtlichen Sicherheitsprobleme")

def check_best_practices(filename):
    """Prüfe auf Best Practices"""
    print(f"\n⭐ BEST PRACTICES:")

    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
        lines = code.split('\n')

    checks = []

    # Shebang für executables
    if lines[0].startswith('#!/usr/bin/env python'):
        checks.append("✅ Shebang vorhanden")

    # Module docstring
    if '"""' in '\n'.join(lines[:20]):
        checks.append("✅ Module docstring vorhanden")

    # Import statements
    import_lines = [l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')]
    if import_lines:
        if all('import *' not in l for l in import_lines):
            checks.append("✅ Keine wildcard imports")

    # if __name__ == "__main__"
    if 'if __name__ == "__main__":' in code:
        checks.append("✅ Main guard vorhanden")

    # Line length
    long_lines = [i+1 for i, l in enumerate(lines) if len(l) > 120]
    if len(long_lines) < 5:
        checks.append("✅ Zeilen meist unter 120 Zeichen")
    else:
        checks.append(f"⚠️ {len(long_lines)} Zeilen über 120 Zeichen")

    for check in checks:
        print(f"   {check}")

# Main
if __name__ == "__main__":
    print("\n" + "🔍"*35)
    print("🎯 CODE-QUALITÄTS-ANALYSE")
    print("🔍"*35)

    files = [
        'position_size_calculator.py',
        'advanced_trading_app.py',
        'hebelprodukt_tool.py'
    ]

    for filename in files:
        if os.path.exists(filename):
            analyze_code_quality(filename)
            check_security_issues(filename)
            check_best_practices(filename)
        else:
            print(f"\n❌ Datei nicht gefunden: {filename}")

    print("\n" + "="*70)
    print("✅ CODE-QUALITÄTS-ANALYSE ABGESCHLOSSEN")
    print("="*70 + "\n")
