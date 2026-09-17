"""Export the existing slide declaration without importing or running Dash."""
import ast
import json
from pathlib import Path
import sys


class Components:
    def __init__(self, namespace):
        self.namespace = namespace

    def __getattr__(self, name):
        def component(*args, **props):
            if args:
                if len(args) != 1:
                    raise ValueError(f"Unsupported positional arguments: {name}")
                props["children"] = args[0]
            return {"namespace": self.namespace, "type": name, "props": props}
        return component


def main():
    root = Path(__file__).resolve().parents[1]
    source = ast.parse((root / "app.py").read_text())
    declaration = next(node.value for node in source.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "slides" for target in node.targets))
    # The repo-owned slide expression contains only trusted html/dcc constructors.
    # Execute neither app.py imports nor its server/callbacks.
    slides = eval(compile(ast.Expression(declaration), "app.py:slides", "eval"),
                  {"__builtins__": {}, **{name: Components(name) for name in ("html", "dcc", "dash_katex")}})
    assert len(slides) == 16
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(slides, ensure_ascii=False))
    print(f"Exported {len(slides)} existing slides; original app.py unchanged.")


if __name__ == "__main__":
    main()
