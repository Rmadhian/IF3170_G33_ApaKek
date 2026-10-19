import json

from core.models import Package, State, Truck


# baca truk dan paket dari file json
def load_input(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    t = data["truck"]
    truck = Truck(t["w"], t["l"], t["h"], t["max_capacity"])
    packages = [Package(p["id"], p["w"], p["l"], p["h"], p["value"], p["weight"],
        p.get("fragile", False), p.get("eta", 0)) for p in data["packages"]]
    return packages, truck


# state ke list dict untuk visualisasi dan json
def snapshot(state: State, packages):
    rows = []
    for i, pkg in enumerate(packages):
        p = state.placements[i]
        w, l, h = state.dims(i, packages)
        rows.append({
            "id": pkg.id,
            "in_truck": p.inside,
            "x": p.x if p.inside else None,
            "y": p.y if p.inside else None,
            "z": p.z if p.inside else None,
            "w": w, "l": l, "h": h,
            "value": pkg.value,
            "weight": pkg.weight,
            "is_fragile": pkg.fragile,
            "eta": pkg.eta,
        })
    return rows
