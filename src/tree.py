# %%
from prefs import _opdict, _ops, _fns


def parse(expression):
    _digit = list("0123456789.")

    def _lex(expression):
        ts = [["_HEAD_", "O"]]
        cs = list(expression.replace(" ", "").replace("**", "^"))
        while len(cs) > 0:
            c = cs.pop(0)
            tp = "O" if c in _ops else ("N" if c in _digit else "S")
            if tp != "O" and (ts[-1][1] == tp or ts[-1][1] == "S"):
                ts[-1] = [ts[-1][0] + c, tp]
            else:
                ts.append([c, tp])
        return [t[0] for t in ts[1:]]

    def _next():
        return len(_ts) > 0

    def _consume(opAry):
        if _next() and _ts[0] in _ops and _ts[0] in opAry:
            return _ts.pop(0)
        return None

    def _consumeloop(n, opAry, fn):
        while _next():
            op = _consume(opAry)
            if op is None:
                break
            n = [n, fn(), op]
        return n

    def _expect(t):
        if not _next() or _ts[0] != t or _ts[0] not in _ops:
            raise Exception(f"The '{t}' is not found.")
        _ts.pop(0)

    def _leaf():
        t = _ts.pop(0)
        t = t + (_ts.pop(0) if t == "-" and _next() else "")
        try:
            return int(t)
        except Exception:
            try:
                return float(t)
            except Exception:
                return t

    def _comma(func):
        n = [_expr()]
        while _next():
            if _consume([","]) is None:
                break
            n.append(_expr())
        n.append(func)
        return n

    def _prim():
        fname = _ts.pop(0) if _next() and _ts[0] in _fns else None
        if _consume(["("]) is not None:
            n = _expr() if fname == None else _comma(fname)
            _expect(")")
            return n
        elif fname is not None:
            raise Exception("The function arguments is not found.")
        return _leaf() if _next() else None

    def _power():
        return _consumeloop(_prim(), ["^"], _power)

    def _mul():
        return _consumeloop(_power(), ["*", "/"], _power)

    def _expr():
        if _next() and _ts[0] in _ops and _ts[0] not in ["-", "("]:
            raise Exception(f"The '{_ts[0]}' is wrong position")
        if _consume(["-"]) is None:
            n = _mul()
        else:
            n = _mul()
            n = -n if type(n) is int or type(n) is float else [-1, n, "*"]
        return _consumeloop(n, ["+", "-"], _mul)

    _ts = _lex(expression)
    n = _expr()
    if (_next()):
        raise Exception(f"The '{expression}' could not be parsed.")
    return n


def tree(expr):
    def _check(expr):
        if "=" in expr:
            raise Exception("Equal sign cannot be used")
        pos, depth, parts = (0, [], [])
        for idx, c in enumerate(expr):
            pos += 1 if c == "(" else (-1 if c == ")" else 0)
            depth.append(pos)
            if c not in ["<", ">"]:
                continue
            if pos != 0:
                msg = "The '<' and '>' cannot be used"
                raise Exception(msg+"inside parentheses")
            parts.append(idx)
        if depth[-1] != 0 or True in [x < 0 for x in depth]:
            raise Exception("The number of parentheses does not match")
        return parts

    parts, stacks, prevPos = (_check(expr), [], 0)
    for pos in parts:
        stacks.append(parse(expr[prevPos:pos]))
        prevPos = pos + 1
    stacks.append(parse(expr[prevPos:]))
    root = None if len(stacks) > 1 else stacks
    for idx, pos in enumerate(parts):
        n = [stacks[idx], stacks[idx + 1], expr[pos]]
        root = n if (root is None) else [root, n, "_NOP_"]
    return root


def test():
    tests = {
        '1': 1,
        '1.5': 1.5,
        '-21.1': -21.1,
        '(-12.1)': -12.1,
        'x2': 'x2',
        '1 + 1': [1, 1, '+'],
        '-1 + 1': [-1, 1, '+'],
        '1 - x': [1, 'x', '-'],
        '1 + 1 + 1': [[1, 1, '+'], 1, '+'],
        '1 - 1 + 1': [[1, 1, '-'], 1, '+'],
        '1 + 2 * 3': [1, [2, 3, '*'], '+'],
        '1 * 2 + ( 3 + 4 )': [[1, 2, '*'], [3, 4, '+'], '+'],
        '1 * 2': [1, 2, '*'],
        '1 * 2 - 1': [[1, 2, '*'], 1, '-'],
        '1 + 2 * 1': [1, [2, 1, '*'], '+'],
        '1 / 2 + 1': [[1, 2, '/'], 1, '+'],
        '1 - 2 / 1': [1, [2, 1, '/'], '-'],
        '1+(2+3)': [1, [2, 3, '+'], '+'],
        '(1+2)+3': [[1, 2, '+'], 3, '+'],
        '1+(-2+3)': [1, [-2, 3, '+'], '+'],
        '2 ** 3': [2, 3, '^'],
        '2 ** -3': [2, -3, '^'],
        '2 ** (-3)': [2, -3, '^'],
        '2 * 3 ** 4': [2, [3, 4, '^'], '*'],
        '2 ** 3 * 3 ** 4': [[2, 3, '^'], [3, 4, '^'], '*'],
        '12 - 34 - 5': [[12, 34, '-'], 5, '-'],
        '2+(x^2+2)': [2, [['x', 2, '^'], 2, '+'], '+'],
        '(x^2+2)*2': [[['x', 2, '^'], 2, '+'], 2, '*'],
        '(x^2+2)^2': [[['x', 2, '^'], 2, '+'], 2, '^'],
        '10-3 ** 2': [10, [3, 2, '^'], '-'],
        '(-3) ** 2': [-3, 2, '^'],
        'x ** 2': ['x', 2, '^'],
        '2 ** 3 ** 4': [2, [3, 4, '^'], '^'],
        '4^3.1415^2': [4, [3.1415, 2, '^'], '^'],
        '4^3.1415^2+(x^2+2)^2': [[4, [3.1415, 2, '^'], '^'], [[['x', 2, '^'], 2, '+'], 2, '^'], '+'],
        'abs(x)': ['x', 'abs'],
        'sin(x)': ['x', 'sin'],
        'cos(x)^2+sin(x)^2': [[['x', 'cos'], 2, '^'], [['x', 'sin'], 2, '^'], '+'],
        '-3 ** 2': [-1, [3, 2, '^'], '*'],
        '-x ** 2': [-1, ['x', 2, '^'], '*'],
        '1+(-2^3)': [1, [-1, [2, 3, '^'], '*'], '+'],
        '1-sin(x)': [1, ['x', 'sin'], '-'],
        '-abs(x)': [-1, ['x', 'abs'], '*'],
        '-sin(x)': [-1, ['x', 'sin'], '*'],
        'atan(1)': [1, 'atan'],
        'atan2(-1,2)': [-1, 2, 'atan2'],
        'atan2(1,-2)': [1, -2, 'atan2'],
        'atan2(-1,-2)': [-1, -2, 'atan2'],
        'atan2(x+y,z-w)': [['x', 'y', '+'], ['z', 'w', '-'], 'atan2'],
        'atan2(1,2,3)': [1, 2, 3, 'atan2'],
        'abc+def': ['abc', 'def', '+'],
        'ab2+de40': ['ab2', 'de40', '+'],
        '+1': "The '+' is wrong position",
        'atan2+': "The function arguments is not found.",
        'atan2(': "The ')' is not found.",
        'abc(1)': "The 'abc(1)' could not be parsed.",
        '1,1,1': "The '1,1,1' could not be parsed.",
    }

    for k, v in tests.items():
        try:
            r = parse(k)
        except Exception as e:
            assert v == str(e)
            print(f'{k.ljust(20, " ")} -> Exception: {e}')
            continue
        print(f'{k.ljust(20, " ")} -> {str(r).replace(" ", "")}')
        assert str(r) == str(v), f'\nexpr:\t{k}\nresult:\t{r}\nanswer:\t{v}'


if __name__ == "__main__":
    test()
