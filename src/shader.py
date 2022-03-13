from prefs import _opdict, _ops, _fns


def shader(nodes, links, context):
    _node_tree = context.space_data.edit_tree
    _bpyLinks = _node_tree.links
    _bpyNodes = _node_tree.nodes

    def _create():
        bpy.ops.node.add_node(type="ShaderNodeMath")
        t = context.active_node
        t.width, t.height = (140, 170)
        return context.active_node

    def _math(n):
        t = _create()
        t.operation = _opdict[n[2]] if n[2] in _opdict else n[2]
        if type(n[1]) is not str:
            t.inputs[0].default_value = n[1]
        if type(n[3]) is not str:
            t.inputs[1].default_value = n[3]
        else:
            t.height = 145
        return t

    def _input(n):
        t = _create()
        t.label = f"Input '{n[2]}'"
        t.operation = "ADD"
        t.inputs[0].default_value = 0
        t.inputs[1].default_value = 0
        return t

    def _output(n):
        t = _create()
        t.label = f"Output '{n[2]}'"
        t.operation = "ADD"
        t.inputs[0].default_value = 0
        t.inputs[1].default_value = 0
        return t

    def _link(fn, tn, port):
        return _bpyLinks.new(
            fn.outputs["Value"],
            tn.inputs[(0 if port == 0 else 1)],)

    ops = _opdict.keys()
    fns, tns = ([l[2] for l in links], [l[0] for l in links])
    leafs = [n[0] for n in nodes if n[0] not in tns and n[2] not in ops]
    roots = [n[0] for n in nodes if n[0] not in fns]
    sns, ons, ins, ses = ([], [], [], [])
    for n in nodes:
        sns.append(_input(n) if n[0] in leafs else _math(n))
        if n[0] in leafs:
            ins.append(sns[-1])
        elif n[0] in roots:
            ons.append(_output(n))
            ses.append(_link(sns[-1], ons[-1], 0))
    sns.extend(ons)
    ses.extend([_link(sns[l[2]], sns[l[0]], l[1]) for l in links])
    return (sns, ses, ins, ons)
