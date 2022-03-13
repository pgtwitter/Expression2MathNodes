# %%
import bpy
import itertools
bl_info = {
    "name": "Expression to Math Nodes",
    "author": "p_g_",
    "version": (0, 2),
    "blender": (3, 0, 0),
    "location": "Node Editor > Tool(Sidebar)",
    "description": "Create math nodes from a Expression",
    "warning": "",
    "doc_url": "https://gist.github.com/pgtwitter/bb5a55a623e9532ac57bdda839dcf249",
    "category": "Node",
}


class E2MN_Panel(bpy.types.Panel):
    bl_label = "Expression2MathNodes Panel"
    bl_idname = f"NODE_PT_{__name__}"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__name__].preferences
        box = layout.box()
        box.label(text="Expression To Math Nodes")
        row = box.row()
        row.prop(prefs, "expr")
        row = box.row()
        row.prop(prefs, "form", text="Style"),
        row = box.row()
        row.operator("node.expression2mathnodes", text="Create", icon="NODE")
        box = layout.box()
        box.label(text="Rearrange Whole Nodes")
        row = box.row()
        row.prop(prefs, "includingFrame")
        row = box.row()
        row.operator("node.rearrangenodes", text="Rearrange", icon="NODE")


class E2MN_Expression2MathNodesPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    includingFrame: bpy.props.BoolProperty(
        name="including the nodes in the frames", default=True)
    expr: bpy.props.StringProperty(
        name="Expression", default="t*x+(1-t)*y", maxlen=1024)
    form: bpy.props.EnumProperty(
        name="Style of Result Nodes", default="Frame",
        items=[(s, s, '') for s in ["Plane", "Frame", "Group"]])

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Expression To Math Nodes")
        row = box.row()
        row.prop(self, "form", text="Style of Result Nodes"),
        row = box.row()
        row.prop(self, "expr")
        box = layout.box()
        box.label(text="Rearrange Whole Nodes")
        row = box.row()
        row.prop(self, "includingFrame")

# _lib_


def showErrorMessageDialog(context):
    def _msg(self, context):
        msg = "The 'node_tree' or 'node_tree.nodes'"
        self.layout.label(text=msg+" not found in current context.")

    context.window_manager.popup_menu(_msg, title="Error", icon="ERROR")


def createMathNodesFromExpression(operator, context):
    def _select(ns):
        for n in ns:
            n.select = True

    def _join(nodes, ins, outs):
        bpy.ops.node.select_all(action="DESELECT")
        _select([n for n in nodes if not (n in ins or n in outs)])
        bpy.ops.node.join()
        bpyLayout(nodes, links, True)
        _select(nodes)

    def _group(nodes, ins, outs, context):
        bpy.ops.node.select_all(action="DESELECT")
        _select([n for n in nodes if not (n in ins or n in outs)])
        bpy.ops.node.group_make()
        bpy.ops.node.tree_path_parent()
        _select([n for n in nodes if n in ins or n in outs])
        tns = [n for n in context.selected_nodes]
        links = context.space_data.edit_tree.links
        tls = [l for l in links if l.from_node in tns and l.to_node in tns]
        bpyLayout(tns, tls, False)

    def _main(context):
        prefs = context.preferences.addons[__name__].preferences
        nodes, links, ins, outs = shader(*graph(tree(prefs.expr)), context)
        bpyLayout(nodes, links, True)
        _select(nodes)
        if prefs.form == "Frame":
            _join(nodes, ins, outs)
        elif prefs.form == "Group":
            _group(nodes, ins, outs, context)

    if context.space_data.edit_tree is None:
        showErrorMessageDialog(context)
        return
    _main(context)


def rearrangeWholeNodes(operator, context):
    def _main(context):
        prefs = context.preferences.addons[__name__].preferences
        nodelist = [n for n in node_tree.nodes]
        bpyLayout(nodelist, node_tree.links, prefs.includingFrame)

    node_tree = context.space_data.edit_tree
    if node_tree is None:
        showErrorMessageDialog(context)
        return
    _main(context)


class E2MN_NodeOperator_Expression2MathNodes(bpy.types.Operator):
    bl_idname = "node.expression2mathnodes"
    bl_label = "Create Math Nodes From Expression"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == "NODE_EDITOR"

    def execute(self, context):
        createMathNodesFromExpression(self, context)
        return {"FINISHED"}


class E2MN_NodeOperator_RearrangeWholeNodes(bpy.types.Operator):
    bl_idname = "node.rearrangenodes"
    bl_label = "Rearrange Whole Nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == "NODE_EDITOR"

    def execute(self, context):
        rearrangeWholeNodes(self, context)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(E2MN_NodeOperator_Expression2MathNodes)
    bpy.utils.register_class(E2MN_NodeOperator_RearrangeWholeNodes)
    bpy.utils.register_class(E2MN_Panel)
    bpy.utils.register_class(E2MN_Expression2MathNodesPreferences)


def unregister():
    bpy.utils.unregister_class(E2MN_Expression2MathNodesPreferences)
    bpy.utils.unregister_class(E2MN_Panel)
    bpy.utils.unregister_class(E2MN_NodeOperator_RearrangeWholeNodes)
    bpy.utils.unregister_class(E2MN_NodeOperator_Expression2MathNodes)


if __name__ == "__main__":
    register()
