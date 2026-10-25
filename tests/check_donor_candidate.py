"""Validate an offline candidate against its exact donor, not hardware compatibility."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fdt_inventory import parse

a = parse(Path(sys.argv[1]).read_bytes())
b = parse(Path(sys.argv[2]).read_bytes())
expected = {
    "/": {"model": b"H20 Pro LP3 EXPERIMENTAL INCOMPLETE\0"},
    "/soc@3000000/sdmmc@4022000": {"status": b"okay\0", "max-frequency": struct.pack(">I", 50000000)},
    "/soc@3000000/nand0@4011000": {"status": b"disabled\0"},
    "/soc@3000000/rfkill/bt": {"status": b"disabled\0"},
    "/soc@3000000/btlpm": {"status": b"disabled\0"},
}
assert set(a) == set(b), "Nodes were added or removed"
changed = {path: {key: value for key, value in props.items() if a[path].get(key) != value}
           for path, props in b.items() if props != a[path]}
assert changed == expected, "Unexpected property changes"
for path in a:
    assert set(a[path]) <= set(b[path]), "Property removed"
print("PASS: exact intended changes; all other DT properties preserved. Hardware untested.")
