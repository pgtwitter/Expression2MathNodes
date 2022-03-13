# %%
from prefs import _opdict, _ops, _fns
import tree


def graph(tree):
    keyword = []
    keyword.extend(_ops)
    keyword.extend(_fns)

    def _encode(tree):
        r = [_encode(b) if type(b) is list else b for b in tree]
        return f"({r[0]}){r[2]}({r[1]})" if len(r) == 3 else f"{r[1]}({r[0]})"

    def _graphIMP(tree, cnt, p2i, ns, es):
        ret = []
        cnt = cnt + 1
        ownNum = cnt
        children = []
        cs = ["", ""]
        for idx, b in enumerate(tree):
            if type(b) is list:
                k = _encode(b)
                if str(k) in p2i:
                    children.append((idx, p2i[k]))
                else:
                    b, cnt, p2i, ns, es = _graphIMP(b, cnt, p2i, ns, es)
                    children.append((idx, cnt - 1))
                    p2i[k] = cnt - 1
                    ret.append(b)
            else:
                if str(b) not in keyword and str(b) in p2i:
                    children.append((idx, p2i[str(b)]))
                elif idx != 2:
                    try:
                        cs[idx] = int(b)
                    except ValueError as e1:
                        try:
                            cs[idx] = float(b)
                        except ValueError as e2:
                            cs[idx] = ""
                            ns.append([cnt, "", b, ""])
                            children.append((idx, cnt))
                            ownNum = cnt
                            p2i[str(b)] = cnt
                else:
                    ns.append([cnt, cs[0], b, cs[1]])
                    children.append((idx, cnt))
                    ownNum = cnt
                    p2i[str(b)] = cnt
                ret.append(b)
                cnt = cnt + 1
        for idx, i in children:
            if ownNum > i:
                pos = 0 if idx == 0 else 2
                es.append([ownNum, pos, i, 1])
        return (ret, cnt, p2i, ns, es)

    root, cnt, p2i, nodes, edges = _graphIMP(tree, 0, {}, [], [])
    nodes = [n for n in nodes if n[2] != "_NOP_"]
    nodeMap = dict([(n[0], idx) for idx, n in enumerate(nodes)])
    for n in nodes:
        n[0] = nodeMap[n[0]]
    ens = nodeMap.keys()
    edges = [e for e in edges if e[0] in ens and e[2] in ens]
    for e in edges:
        e[0] = nodeMap[e[0]]
        e[2] = nodeMap[e[2]]
    return (nodes, edges)


def test():

    def _gviz(tree, expr):
        _keyword = []
        _keyword.extend(_ops)
        _keyword.extend(_fns)

        def _node(n):
            m = "&gt;" if n[2] == ">" else ("&lt;" if n[2] == "<" else n[2])
            if n[2] in _keyword:
                return f'\tn{n[0]}[label="<f0>{n[1]}|<f1>{m}|<f2>{n[3]}"];'
            else:
                return f'\tn{n[0]}[label="<f1>{m}"];'

        nodes, edges = graph(tree)
        dots = ["digraph expr_graph {"]
        dots.append(f'\tgraph [label = "{expr}"]')
        dots.append("\tnode [shape = record]")
        dots.extend([_node(n) for n in nodes])
        dots.extend([f"\tn{e[0]}:f{e[1]}->n{e[2]}:f{e[3]};" for e in edges])
        dots.append("}")
        return "\n".join(dots)

    expr = 'x*t+y*(1-t)'
    if False:
        expr1 = "((x**2+y**2)**0.5-8-abs(((x**2-y**2)/(x**2+y**2))**2-1/2))**2+z**2"
        expr2 = "(2+3*abs( ((x**2-y**2)/(x**2+y**2))**2-(1/2) ))**2"
        expr = expr1 + "<" + expr2
    dots = _gviz(tree.tree(expr), expr)
    with open("./graph_test.dot", "w") as fileobj:
        fileobj.write(dots)
    print(dots)


if __name__ == "__main__":
    test()
