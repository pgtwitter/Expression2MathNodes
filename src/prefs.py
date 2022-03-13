_opdict = {
    "+": "ADD",
    "-": "SUBTRACT",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "^": "POWER",
    "<": "LESS_THAN",
    ">": "GREATER_THAN",
    "abs": "ABSOLUTE",
    "sin": "SINE",
    "cos": "COSINE",
    "tan": "TANGENT",
    "atan": "ARCTANGENT",
    "atan2": "ARCTAN2",
}
_ops = ["(", ")", ",", "+", "-", "*", "/", "^"]
_fns = [k for k in _opdict.keys() if k not in _ops]
