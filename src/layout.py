# %%
import itertools


def layout(ns, ls, includingFrame):
    _ns, _ls = ([n for n in ns], [l for l in ls])
    _sls, _fcs, _t2fs, _f2ts = ([], {}, {}, {})

    def _em(obj):
        return enumerate(obj)

    def _n(idx):
        return _ns[idx]

    def _centering(shiftX, shiftY):
        for n in [n for n in _ns if not n[4] or len(_fcs[_ns.index(n)]) == 0]:
            n[0], n[1] = (n[0] - shiftX, n[1] - shiftY)

    def _leaves(f):
        if f not in _fcs:
            return (1, [f])
        depth, ret = (0, [])
        for cf in _fcs[f]:
            cd, cret = _leaves(cf)
            ret.extend(cret)
            depth = max(depth, cd)
        return (depth + 1, ret)

    def _bbox(idx):
        def __bboxIMP(depth, idxes):
            ns = [_n(idx) for idx in idxes]
            x, y = (min([n[0] for n in ns]), max([n[1] for n in ns]))
            w = max([n[0]+n[2] for n in ns])-x
            h = abs(min([n[1]-n[3] for n in ns])-y)
            return [x, y, w, h]

        if idx in _fcs and len(_fcs[idx]) > 0:
            return __bboxIMP(*_leaves(idx))
        return _n(idx)[0:4]

    def _layoutIMP(layers):
        def __move(dy, ly, i):
            for ci in (ly[(ly.index(i)):] if dy > 0 else []):
                if _n(ci)[4] and len(_fcs[ci]) > 0:
                    for cj in (_leaves(ci))[1]:
                        _n(cj)[1] -= dy
                else:
                    _n(ci)[1] -= dy

        def __moves(ly, ref):
            for i in [fi for fi in ly if fi in ref]:
                y1 = max([_n(c)[1] for n1 in ref[i] for c in _leaves(n1)[1]])
                y2 = max([_n(n2)[1] for n2 in _leaves(i)[1]])
                if y2 > y1:
                    __move(y2 - y1, ly, i)

        xpos, minY = (0, 0)
        for i in range(len(layers.keys())):
            ns = layers[i]
            ypos = 0
            bboxes = [_bbox(fn) for fn in ns]
            xpos -= max([bbox[2] for bbox in bboxes]) + 50
            for i, fn in _em(ns):
                bbox = bboxes[i]
                n = _n(fn)
                n[0], n[1] = (xpos, ypos)
                if n[4] and len(_fcs[fn]) > 0:
                    n[0], n[1] = (0, 0)
                    depth, leaves = _leaves(fn)
                    for leafIdx in leaves:
                        leaf = _n(leafIdx)
                        dx, dy = (leaf[0] - bbox[0], leaf[1] - bbox[1])
                        leaf[0], leaf[1] = (xpos + dx, ypos + dy)
                ypos -= bbox[3] + 10
            minY = min(minY, ypos)
        minX = xpos
        if len(layers.keys()) < 2:
            return (minX, minY)
        depth = max(layers.keys())
        adj = list(range(depth - 1))
        adj.extend(reversed(adj))
        for ly in [layers[i] for i in adj]:
            __moves(ly, _t2fs)
        __moves(layers[depth], _f2ts)

        return (min([n[0] for n in _ns]), min([n[1] for n in _ns]))

    def _layers(roots, limit):
        def __sortroots(layer):
            def ___treeleaves(t):
                ret = [t]
                if t in _t2fs:
                    for f in _t2fs[t]:
                        ret.extend(___treeleaves(f))
                return ret

            c = [(___treeleaves(tn), tn) for tn in layer]
            return [l[-1] for l in sorted(c, key=lambda x: -len(x[0]))]

        def __cross(es):
            def ___comp(e0, e1):
                return 1 if (e0[0] - e1[0])*(e0[1] - e1[1]) < 0 else 0

            c = [___comp(e0, e1) for i, e0 in _em(es[:-1]) for e1 in es[i+1:]]
            return sum(c)

        def __connects(tos, froms):
            ret = []
            for i, t in _em(tos):
                for j, f in _em(froms):
                    for l in [l for l in _sls if l[0] == f and l[2] == t]:
                        ret.append((j * 1000 + l[1], i * 1000 + l[3]))
            return ret

        def __issetlist(obj):
            return type(obj) is list or type(obj) is set

        def __flatten(ary):
            ret = []
            for elem in ary:
                if __issetlist(elem):
                    ret.extend(__flatten(elem))
                else:
                    ret.append(elem)
            return ret

        def __dictAppend(d, k, v):
            if k in d:
                d[k].extend(v)
            else:
                d[k] = v

        def _comp2(ret, pattern):
            f1 = __flatten(ret)
            f2 = __flatten(pattern)
            c = [i-j for i, j in zip(f1, f2) if i-j != 0]
            return False if len(c) == 0 else False if c[0] < 0 else True

        def __comp(tos, froms):
            ret, c0 = ([], 1E6)
            for pattern in list(itertools.permutations(froms, len(froms))):
                c1 = __cross(__connects(tos, __flatten(pattern)))
                if c0 > c1 or (c0 == c1 and _comp2(ret, pattern)):
                    ret, c0 = (pattern, c1)
            return list(ret)

        def __skipedlink(n1, n2):
            return n1 in n2ly and n2 in n2ly and abs(n2ly[n1]-n2ly[n2]) > 1

        lys = [roots]
        for i in range(limit):  # loop limitter
            nly = set()
            for tn in [tn for tn in lys[-1] if tn in _t2fs]:
                nly = nly.union(set(_t2fs[tn]))
            if len(nly) == 0:
                break
            lys.append(list(nly))
        n2ly = {n: i for i, fr in _em(lys) for n in fr}
        lys = {i: [n for n in fr if i == n2ly[n]] for i, fr in _em(lys)}
        for l in [l for l in _ls if __skipedlink(l[0], l[2])]:
            fr, to, tmp = (l[0], l[2], l[2])
            for j in list(range(n2ly[to]+1, n2ly[fr])):
                cnt = len(_ns)
                _ns.append([0, 0, 50, _n(to)[3]/2, False, None, cnt, 'd'])
                lys[j].append(cnt)
                _ls.append([cnt, 0, tmp, 0])
                __dictAppend(_t2fs, tmp, [cnt])
                tmp = cnt
            _ls.append([fr, 0, tmp, 0])
            __dictAppend(_t2fs, tmp, [fr])
            _ls.remove(l)
            _t2fs[to].remove(fr)

        lys[0] = __sortroots(lys[0])

        for idx in [i for i in range(len(lys) - 1) if len(lys[i+1]) > 1]:
            froms, tos, d = (lys[idx+1], lys[idx], {})
            for to in [to for to in tos if to in _t2fs]:
                ary = [f for f in _t2fs[to] if f in froms]
                for f in ary:
                    __dictAppend(_f2ts, f, [to])
                __dictAppend(d, to, ary)
            others = set([f for f, ts in _f2ts.items() if len(ts) > 1])
            us = [set(d[to]).difference(others) for to in d.keys()]
            us = [u for u in us if len(u) > 0]
            if len(others) > 0:
                us.extend(others)
            lys[idx + 1] = __flatten(us)
            if len(us) < 7:
                us = __comp(tos, us)
            ret = []
            for u in us:
                if __issetlist(u):
                    ret.extend(__comp(tos, u) if len(us) < 7 else [u])
                else:
                    ret.append(u)
            lys[idx + 1] = __flatten(ret)
        return lys

    def _roots(ns, curr):
        roots, fns = ([], [])
        for l in _ls:
            fn, fs, tn, ts = (l[0], l[1], l[2], l[3])
            if _n(fn)[5] is not None:
                while _n(fn)[5] is not None and _n(fn)[5] != curr:
                    fn = _n(fn)[5]
            if _n(tn)[5] is not None:
                while _n(tn)[5] is not None and _n(tn)[5] != curr:
                    tn = _n(tn)[5]
            if fn == tn or fn not in ns or tn not in ns:
                continue
            fns.append(fn)
            roots.append(tn)
            if tn in _t2fs:
                if fn not in _t2fs[tn]:
                    _t2fs[tn].append(fn)
            else:
                _t2fs[tn] = [fn]
            _sls.append([fn, fs, tn, ts])
        roots = list(set(roots))
        roots.extend([n for n in ns if n not in roots and _n(n)[5] == curr])
        for fn in [fn for fn in set(fns) if fn in roots]:
            roots.remove(fn)
        return (roots, len(ns))

    def _frames(ns):
        def __resetframelocation(frames):
            for n in [_n(f) for f in frames]:
                nx, ny = (n[0], n[1])
                n[0], n[1] = (0, 0)
                depth, leaves = _leaves(f)
                for cn in [_n(lf) for lf in leaves]:
                    cn[0], cn[1] = (cn[0] + nx, cn[1] + ny)

        frames = [_ns.index(n) for n in ns if n[4]]
        layers = [list(set(frames))]
        for i in range(len(frames)):
            fs = [f for f in layers[-1] if _n(f)[5] in layers[-1]]
            if len(fs) == 0:
                break
            layers.append(list(fs))
        exists = {f: i for i, fs in _em(layers) for f in fs}
        for i, fs in _em(layers):
            layers[i] = [f for f in fs if i == exists[f]]
        for f in frames:
            _fcs[f] = []
        for n in [n for n in ns if n[5] is not None]:
            _fcs[n[5]].append(_ns.index(n))
        frames = list(reversed(sum(layers, [])))
        __resetframelocation(frames)
        return (frames)

    for uniqIdx, n in _em(_ns):
        n.append(uniqIdx)
    for uniqIdx, l in _em(_ls):
        l.append(uniqIdx)
    frames = _frames(_ns)
    if includingFrame:
        for f in [f for f in frames if len(_fcs[f]) > 1]:
            _layoutIMP(_layers(*_roots(_fcs[f], f)))
    minX, minY = _layoutIMP(_layers(*_roots(range(len(_ns)), None)))
    _centering(minX * 0.5, minY * 0.5)
    for i in range(len(ns)):
        ns[i][0], ns[i][1] = (_n(i)[0], _n(i)[1])
    return (ns, ls)


def bpyLayout(nodelist, linklist, includingFrame):
    def _wh(n):
        return (max(n.width, n.dimensions[0]/2),
                max(n.height, n.dimensions[1]/2))

    def _bpyNode2node(nodelist, linklist):
        return (
            [[
                *n.location, *_wh(n), isinstance(n, bpy.types.NodeFrame),
                nodelist.index(n.parent) if n.parent in nodelist else None
            ] for idx, n in enumerate(nodelist)],
            [[
                nodelist.index(l.from_node),
                l.from_node.outputs.values().index(l.from_socket),
                nodelist.index(l.to_node),
                l.to_node.inputs.values().index(l.to_socket)
            ] for l in linklist])

    _ns, _ls = layout(*_bpyNode2node(nodelist, linklist), includingFrame)
    for i, n in enumerate(nodelist):
        n.location = (_ns[i][0], _ns[i][1])


def test():
    def _bbox(ns):
        x, y = (min([n[0] for n in ns]), max([n[1] for n in ns]))
        w, h = (max([n[0]+n[2] for n in ns])-x, abs(min([n[1]-n[3] for n in ns])-y))
        return [x, y, w, h]

    def _svg(ns, ls, testname):
        x, y, w, h = _bbox(ns)
        m = 10
        svgns = 'http://www.w3.org/2000/svg'
        svg = f'<svg xmlns="{svgns}" style="border:solid black 1px;"'
        svg += f' width="640" height="640" viewBox="{x-m},{y-h-m},{w+2*m},{h+2*m}">'
        arrow = '\t<marker id="pointer" markerWidth="10" markerHeight="10"'
        arrow += ' refX="5" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        arrow += '<polyline points="1,1 10,5 1,10" /></marker>'
        axis = f'\t<line stroke="#aaa" x1="{x-m}" y1="0" x2="{x+w+m}" y2="0"/>'
        axis += f'<line stroke="#aaa" x1="0" y1="{y-m}" x2="0" y2="{y+h+m}"/>'
        title = f'\t<text stroke="#0f0" x="{x-m}" y="{y-h+72}" font-size="72pt">{testname}</text>'
        dots = [svg, arrow, axis, title]
        for l in ls:
            n1, n2 = (ns[l[0]], ns[l[2]])
            sx, sy = (n1[0]+n1[2], n1[1]-n1[3]/2)
            ex, ey = (n2[0], n2[1]-n2[3]/2)
            ps = f'M {sx},{sy} L {ex},{ey}'
            p = '\t<path fill="none" stroke="#000" stroke-width="2"'
            p += f' marker-end="url(#pointer)" d="{ps}"/>'
            dots.append(p)
        for idx, n in enumerate(ns):
            c = "#f00" if n[4] else "#00f" if n[-1] != 'd' else "#0f0"

            def __diggin(m):
                if m[4]:
                    depth, ret = (-1, [])
                    for cm in [n for n in ns if n[5] == ns.index(m)]:
                        cdepth, cret = __diggin(cm)
                        ret.extend(cret)
                        depth = max(depth, cdepth)
                    return (depth+1, ret)
                else:
                    return (0, [m])

            depth, targets = __diggin(n)
            if len(targets) > 1:
                b = _bbox(targets)
                b[0] -= 2 * depth
                b[1] += 2 * depth
                b[2] += 4*depth
                b[3] += 4*depth
            else:
                b = n
            r = f'\t<rect fill="{c}1" stroke="{c}" x="{b[0]}" y="{b[1]-b[3]}"'
            r += f' width="{b[2]}" height="{b[3]}"/>'
            r += f'\t<text stroke="{c}" x="{b[0]}" y="{b[1]}">{idx}</text>'
            dots.append(r)
        dots.append("</svg>")
        return "\n".join(dots)

    gs = {'t1': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, None],  # 1
            [50, 50, 50, 50, False, None],  # 2
            [50, 50, 50, 50, False, None],  # 3
        ],
        'ls': [
            [0, 0, 1, 0],
            [1, 0, 2, 0],
            [2, 0, 3, 0],
        ]},
        't2': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, None],  # 1
            [50, 50, 50, 50, False, None],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, False, None],  # 4
            [50, 50, 50, 50, False, None],  # 5
        ],
        'ls': [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [1, 0, 3, 0],
            [2, 0, 3, 0],
            [4, 0, 5, 0],
        ]},
        't3': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, 4],  # 1
            [50, 50, 50, 50, False, 4],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, True, None],  # 4(frame)
        ],
        'ls': [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [1, 0, 3, 0],
            [2, 0, 3, 0],
            [1, 0, 2, 0],
        ]},
        't4': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, 4],  # 1
            [50, 50, 50, 50, False, 4],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, True, None],  # 4(frame)
        ],
        'ls': [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [1, 0, 3, 0],
            [2, 0, 3, 0],
        ]},
        't5': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, 4],  # 1
            [50, 50, 50, 50, False, 4],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, True, None],  # 4(frame)
            [50, 50, 50, 50, False, 4],  # 5
        ],
        'ls': [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [1, 0, 3, 0],
            [2, 0, 3, 0],
            [5, 0, 2, 0],
        ]},
        't6': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, 4],  # 1
            [50, 50, 50, 50, False, 4],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, True, None],  # 4(frame)
            [50, 50, 50, 50, False, 4],  # 5
            [50, 50, 50, 50, False, None],  # 0
            [50, 50, 50, 50, False, 10],  # 1
            [50, 50, 50, 50, False, 10],  # 2
            [50, 50, 50, 50, False, None],  # 3
            [50, 50, 50, 50, True, None],  # 4(frame)
            [50, 50, 50, 50, False, 10],  # 5
        ],
        'ls': [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [1, 0, 3, 0],
            [2, 0, 3, 0],
            [5, 0, 2, 0],
            [6, 0, 7, 0],
            [6, 0, 8, 0],
            [7, 0, 9, 0],
            [8, 0, 9, 0],
            [11, 0, 8, 0],
        ]},
        't7': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0x(in)
            [50, 50, 50, 50, False, None],  # 1t(in)
            [50, 50, 50, 50, False, 20],  # 2*
            [50, 50, 50, 50, False, 20],  # 31-
            [50, 50, 50, 50, False, None],  # 4y(in)
            [50, 50, 50, 50, False, 20],  # 5*
            [50, 50, 50, 50, False, 20],  # 6+
            [50, 50, 50, 50, False, None],  # 7(out)
            [50, 50, 50, 50, True, None],  # 8tmpdummy(frame)
            [50, 50, 50, 50, False, None],  # 9material
            [50, 50, 50, 50, False, None],  # 10x(in)
            [50, 50, 50, 50, False, None],  # 11t(in)
            [50, 50, 50, 50, False, 18],  # 12*
            [50, 50, 50, 50, False, 18],  # 131-
            [50, 50, 50, 50, False, None],  # 14y(in)
            [50, 50, 60, 100, False, 18],  # 15*
            [50, 50, 50, 50, False, 18],  # 16+
            [50, 50, 50, 50, False, None],  # 17(out)
            [50, 50, 50, 50, True, None],  # 18(frame)
            [50, 50, 50, 150, False, None],  # 19BSDF
            [50, 50, 50, 50, True, None],  # 20(frame)
            [50, 50, 50, 50, False, None],  # 21BSDF
            [50, 50, 50, 50, False, None],  # 22
            [50, 50, 50, 50, False, None],  # 23x(in)
            [50, 50, 50, 50, False, None],  # 24t(in)
            [50, 50, 50, 50, False, 31],  # 25*
            [50, 50, 50, 50, False, 31],  # 261-
            [50, 50, 50, 50, False, None],  # 27y(in)
            [50, 50, 50, 50, False, 31],  # 28*
            [50, 50, 50, 50, False, 31],  # 29+
            [50, 50, 50, 50, False, None],  # 30(out)
            [50, 50, 50, 50, True, None],  # 31(frame)
        ],
        'ls': [
            [0, 0, 2, 0],
            [1, 0, 2, 0],
            [1, 0, 3, 0],
            [3, 0, 5, 0],
            [4, 0, 5, 0],
            [2, 0, 6, 0],
            [5, 0, 6, 0],
            [6, 0, 7, 0],
            [10, 0, 12, 0],
            [11, 0, 12, 0],
            [11, 0, 13, 0],
            [13, 0, 15, 0],
            [14, 0, 15, 0],
            [12, 0, 16, 0],
            [15, 0, 16, 0],
            [16, 0, 17, 0],
            [19, 0, 9, 0],
            [21, 0, 9, 0],
            [22, 0, 15, 0],
            [0+23, 0, 2+23, 0],
            [1+23, 0, 2+23, 0],
            [1+23, 0, 3+23, 0],
            [3+23, 0, 5+23, 0],
            [4+23, 0, 5+23, 0],
            [2+23, 0, 6+23, 0],
            [5+23, 0, 6+23, 0],
            [6+23, 0, 7+23, 0],
        ]},
        't8': {
        'ns': [
            [50, 50, 50, 50, False, None],  # 0
            [0, 0, 50, 50, False, 12],  # 1
            [0, 50, 50, 50, False, 12],  # 2
            [50, 200, 50, 150, False, None],  # 3
            [50, 100, 50, 100, True, None],  # 4
            [200, 50, 50, 50, False, None],  # 5
            [200, 100, 50, 50, False, None],  # 6
            [200, 150, 50, 50, False, None],  # 7
            [50, 50, 50, 50, False, None],  # 8
            [50, 50, 50, 50, False, 13],  # 9
            [50, 50, 50, 50, False, 13],  # 10
            [50, 50, 50, 50, False, 4],  # 11
            [50, 50, 50, 50, True, 4],  # 12
            [50, 50, 50, 50, True, 4],  # 13
            [50, 50, 50, 50, False, None],  # 14
            [50, 50, 50, 50, False, None],  # 15
        ],
        'ls': [
            [0, 0, 1, 0],
            [1, 0, 2, 0],
            [2, 0, 3, 1],
            [0, 0, 5, 0],
            [5, 0, 6, 0],
            [6, 0, 7, 0],
            [7, 0, 3, 0],
            [6, 0, 9, 0],
            [9, 0, 10, 0],
            [10, 0, 3, 0],
            [5, 0, 14, 0],
            [14, 0, 7, 0],
            [5, 2, 3, 0],
            [15, 0, 7, 0],
            [15, 0, 9, 0],
        ]}
    }
    for idx, key in enumerate(gs.keys()):
        filename = f"./layout{idx}_test.svg"
        g = gs[key]
        print(key)
        if (key == 't7'):
            for n in g['ns']:
                n[4] = False
                n[5] = None
        svg = _svg(*layout(g['ns'], g['ls'], True), key)
        try:
            svg = _svg(*layout(g['ns'], g['ls'], True), key)
        except Exception as e:
            svgns = 'http://www.w3.org/2000/svg'
            svg = f'<svg xmlns="{svgns}">'
            svg += f'<text stroke="#f00" fill="#00f" x="10" y="20">{e}</text>'
            svg += '</svg>'
        with open(filename, "w") as fileobj:
            fileobj.write(svg)


if __name__ == "__main__":
    test()

# %%
