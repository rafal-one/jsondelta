#!/usr/bin/env python3
"""jsondelta: semantic diff of two JSON files (key order ignored, paths reported).

Exit codes: 0 identical, 1 differences found, 2 bad input.
"""
import argparse
import json
import sys

__version__ = "0.1.0"


def _path(base, key):
    if isinstance(key, int):
        return "%s[%d]" % (base, key)
    return "%s.%s" % (base, key) if base else str(key)


def _canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def diff(a, b, path="", unordered=False, ignore=()):
    """Yield (op, path, old, new); op is '+', '-' or '~'."""
    if path in ignore:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            p = _path(path, k)
            if k not in b:
                if p not in ignore:
                    yield ("-", p, a[k], None)
            elif k not in a:
                if p not in ignore:
                    yield ("+", p, None, b[k])
            else:
                yield from diff(a[k], b[k], p, unordered, ignore)
    elif isinstance(a, list) and isinstance(b, list):
        if unordered:
            rest = [_canon(x) for x in b]
            bmap = list(b)
            for i, x in enumerate(a):
                c = _canon(x)
                if c in rest:
                    j = rest.index(c)
                    del rest[j], bmap[j]
                else:
                    yield ("-", _path(path, i), x, None)
            for y in bmap:
                yield ("+", path + "[]", None, y)
        else:
            for i in range(max(len(a), len(b))):
                p = _path(path, i)
                if i >= len(b):
                    yield ("-", p, a[i], None)
                elif i >= len(a):
                    yield ("+", p, None, b[i])
                else:
                    yield from diff(a[i], b[i], p, unordered, ignore)
    else:
        if type(a) is not type(b) or a != b:
            yield ("~", path or "$", a, b)


def _fmt(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def render(changes):
    out = []
    for op, p, old, new in changes:
        p = p or "$"
        if op == "-":
            out.append("- %s: %s" % (p, _fmt(old)))
        elif op == "+":
            out.append("+ %s: %s" % (p, _fmt(new)))
        else:
            out.append("~ %s: %s -> %s" % (p, _fmt(old), _fmt(new)))
    return out


def _load(name):
    try:
        with (sys.stdin if name == "-" else open(name, encoding="utf-8")) as f:
            return json.load(f)
    except OSError as e:
        sys.exit("jsondelta: cannot read %s: %s" % (name, e.strerror))
    except ValueError as e:
        sys.exit("jsondelta: invalid JSON in %s: %s" % (name, e))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jsondelta", description=__doc__.split("\n")[0])
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--unordered", action="store_true", help="treat arrays as multisets")
    ap.add_argument("--ignore", action="append", default=[], metavar="PATH",
                    help="skip this path, e.g. meta.updated (repeatable)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("-q", "--quiet", action="store_true", help="no output, exit code only")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)
    if args.old == "-" and args.new == "-":
        sys.exit("jsondelta: only one input can be '-'")
    a, b = _load(args.old), _load(args.new)
    changes = list(diff(a, b, "", args.unordered, set(args.ignore)))
    if not args.quiet:
        if args.json:
            print(json.dumps([{"op": o, "path": p or "$", "old": x, "new": y}
                              for o, p, x, y in changes], ensure_ascii=False, indent=2))
        else:
            for line in render(changes):
                print(line)
    return 1 if changes else 0


if __name__ == "__main__":
    sys.exit(main())
