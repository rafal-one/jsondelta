# jsondelta

Semantic diff of two JSON files. Key order is ignored, changes are reported by path, and
exit codes make it CI-friendly. Python 3.9+, stdlib only.

```
$ jsondelta old.json new.json
~ server.port: 80 -> 8080
- features[2]: "beta"
+ owner: "ops"
$ jsondelta a.json b.json --unordered --ignore meta.updated
$ cat new.json | jsondelta old.json - --json
```

Options: `--unordered` (arrays as multisets), `--ignore PATH` (repeatable), `--json`, `-q`.
Exit codes: 0 identical, 1 differences, 2 bad input (invalid JSON, unreadable file).
Types matter: `true` vs `1` is a change.

Install: `pip install jsondelta-cli` (command: `jsondelta`) or copy `jsondelta.py`.

## Tests
`pytest` (11 tests; Python 3.9 and 3.14).

## Support
If this saves you time, you can donate via [PayPal](https://paypal.me/RafalBaranowski). MIT license.
