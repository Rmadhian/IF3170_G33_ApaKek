from typing import Any, Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# warna tiap paket
PACKAGE_PALETTE = [
    "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899",
    "#06b6d4", "#84cc16", "#f97316", "#6366f1", "#14b8a6",
    "#eab308", "#a855f7", "#fb7185", "#38bdf8", "#4ade80",
]


# ubah paket jadi dict
def _extract_package_dict(pkg: Any) -> Dict[str, Any]:
    if isinstance(pkg, dict):
        return pkg
    return {
        "id": getattr(pkg, "id", "Unknown"),
        "x": getattr(pkg, "x", None),
        "y": getattr(pkg, "y", None),
        "z": getattr(pkg, "z", None),
        "w": getattr(pkg, "w", getattr(pkg, "width", 1)),
        "l": getattr(pkg, "l", getattr(pkg, "length", 1)),
        "h": getattr(pkg, "h", getattr(pkg, "height", 1)),
        "value": getattr(pkg, "value", 0),
        "weight": getattr(pkg, "weight", 0),
        "is_fragile": getattr(pkg, "is_fragile", getattr(pkg, "IsFragile", False)),
        "eta": getattr(pkg, "eta", getattr(pkg, "ETA", 0)),
        "in_truck": getattr(pkg, "in_truck", getattr(pkg, "x", None) is not None),
    }


# balok 3d
def _create_cuboid_mesh(
    x: float, y: float, z: float, w: float, l: float, h: float,
    color: str, name: str, hover_text: str, opacity: float = 0.75
) -> go.Mesh3d:
    vx = [x, x + w, x + w, x, x, x + w, x + w, x]
    vy = [y, y, y + l, y + l, y, y, y + l, y + l]
    vz = [z, z, z, z, z + h, z + h, z + h, z + h]

    # segitiga 6 sisi
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name,
        hoverinfo="text",
        text=hover_text,
        showlegend=True,
        flatshading=True,
    )


# garis rusuk balok
def _create_wireframe_edges(
    x: float, y: float, z: float, w: float, l: float, h: float,
    line_color: str = "#1e293b", line_width: int = 3, name: str = "Wireframe", showlegend: bool = False
) -> go.Scatter3d:
    edges_x, edges_y, edges_z = [], [], []
    corners = [
        (x, y, z), (x + w, y, z), (x + w, y + l, z), (x, y + l, z),
        (x, y, z + h), (x + w, y, z + h), (x + w, y + l, z + h), (x, y + l, z + h)
    ]
    edge_pairs = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # alas
        (4, 5), (5, 6), (6, 7), (7, 4),  # atap
        (0, 4), (1, 5), (2, 6), (3, 7),  # tiang
    ]
    for p1, p2 in edge_pairs:
        edges_x.extend([corners[p1][0], corners[p2][0], None])
        edges_y.extend([corners[p1][1], corners[p2][1], None])
        edges_z.extend([corners[p1][2], corners[p2][2], None])

    return go.Scatter3d(
        x=edges_x, y=edges_y, z=edges_z,
        mode="lines",
        line=dict(color=line_color, width=line_width),
        name=name,
        showlegend=showlegend,
        hoverinfo="skip",
    )


# visualisasi 3d isi truk
def visualize_container_state(
    truck_dims: Tuple[int, int, int],
    max_capacity: float,
    packages: List[Any],
    state_score: float,
    title: str = "Visualisasi 3D Konfigurasi Peti Kemas — Mejiro Express",
    save_html_path: Optional[str] = None,
) -> go.Figure:
    truck_w, truck_l, truck_h = truck_dims
    parsed_packages = [_extract_package_dict(p) for p in packages]

    inside_pkgs = [p for p in parsed_packages if p.get("in_truck") and p.get("x") is not None]
    outside_pkgs = [p for p in parsed_packages if not p.get("in_truck") or p.get("x") is None]

    total_weight_in = sum(p["weight"] for p in inside_pkgs)
    total_value_in = sum(p["value"] for p in inside_pkgs)

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.68, 0.32],
        specs=[[{"type": "scene"}, {"type": "table"}]],
        subplot_titles=(
            f"Peti Kemas 3D ({truck_w}×{truck_l}×{truck_h}) | Value: {total_value_in} | Berat: {total_weight_in}/{max_capacity}",
            f"Daftar Paket di Luar Peti ({len(outside_pkgs)} Paket)"
        ),
    )

    # dinding truk
    container_wireframe = _create_wireframe_edges(
        0, 0, 0, truck_w, truck_l, truck_h,
        line_color="#0f172a", line_width=5, name="Batas Peti Kemas", showlegend=True
    )
    fig.add_trace(container_wireframe, row=1, col=1)

    # paket di dalam
    fragile_markers_x, fragile_markers_y, fragile_markers_z, fragile_texts = [], [], [], []

    for idx, pkg in enumerate(inside_pkgs):
        color = PACKAGE_PALETTE[idx % len(PACKAGE_PALETTE)]
        x, y, z = pkg["x"], pkg["y"], pkg["z"]
        w, l, h = pkg["w"], pkg["l"], pkg["h"]
        is_fragile = pkg["is_fragile"]

        fragile_tag = " [FRAGILE ⚠️]" if is_fragile else ""
        legend_name = f"{pkg['id']}{fragile_tag} ({w}×{l}×{h})"

        hover_info = (
            f"<b>ID: {pkg['id']}</b>{fragile_tag}<br>"
            f"Koordinat (x,y,z): ({x}, {y}, {z})<br>"
            f"Dimensi/Orientasi (w,l,h): ({w}, {l}, {h})<br>"
            f"Value: {pkg['value']} | Weight: {pkg['weight']}<br>"
            f"ETA: {pkg['eta']} hari"
        )

        # balok
        fig.add_trace(
            _create_cuboid_mesh(x, y, z, w, l, h, color=color, name=legend_name, hover_text=hover_info),
            row=1, col=1,
        )

        # tepi merah kalau fragile
        edge_color = "#dc2626" if is_fragile else "#334155"
        edge_width = 5 if is_fragile else 2
        fig.add_trace(
            _create_wireframe_edges(x, y, z, w, l, h, line_color=edge_color, line_width=edge_width),
            row=1, col=1,
        )

        # penanda fragile
        if is_fragile:
            fragile_markers_x.append(x + w / 2.0)
            fragile_markers_y.append(y + l / 2.0)
            fragile_markers_z.append(z + h + 0.15)
            fragile_texts.append(f"⚠️ {pkg['id']} (Fragile)")

    # legenda fragile
    if fragile_markers_x:
        fig.add_trace(
            go.Scatter3d(
                x=fragile_markers_x,
                y=fragile_markers_y,
                z=fragile_markers_z,
                mode="markers+text",
                marker=dict(size=7, color="#dc2626", symbol="diamond"),
                text=fragile_texts,
                textposition="top center",
                name="Penanda Fragile ⚠️",
                showlegend=True,
            ),
            row=1, col=1,
        )

    # tabel paket di luar
    if outside_pkgs:
        out_ids = [p["id"] for p in outside_pkgs]
        out_dims = [f"{p['w']}×{p['l']}×{p['h']}" for p in outside_pkgs]
        out_vals = [p["value"] for p in outside_pkgs]
        out_wgts = [p["weight"] for p in outside_pkgs]
        out_frag = ["Ya ⚠️" if p["is_fragile"] else "Tidak" for p in outside_pkgs]
    else:
        out_ids, out_dims, out_vals, out_wgts, out_frag = ["(Semua paket masuk)"], ["-"], ["-"], ["-"], ["-"]

    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>ID Paket</b>", "<b>Dimensi</b>", "<b>Value</b>", "<b>Weight</b>", "<b>Fragile</b>"],
                fill_color="#1e293b",
                font=dict(color="white", size=12),
                align="center",
            ),
            cells=dict(
                values=[out_ids, out_dims, out_vals, out_wgts, out_frag],
                fill_color="#f8fafc",
                font=dict(color="#0f172a", size=11),
                align="center",
                height=26,
            ),
        ),
        row=1, col=2,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><sup>Objective Score: {state_score:.2f} | Paket Masuk: {len(inside_pkgs)}/{len(parsed_packages)}</sup>",
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(title="Width (X)", range=[0, max(truck_w, 1)]),
            yaxis=dict(title="Length (Y)", range=[0, max(truck_l, 1)]),
            zaxis=dict(title="Height (Z)", range=[0, max(truck_h + 1, 1)]),
            aspectmode="data",
        ),
        legend=dict(
            title="<b>Legenda Paket (Di Dalam Peti)</b>",
            yanchor="top", y=0.95,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.85)",
        ),
        margin=dict(l=10, r=10, b=10, t=80),
        height=720,
    )

    if save_html_path:
        import os
        os.makedirs(os.path.dirname(save_html_path) or ".", exist_ok=True)
        fig.write_html(save_html_path)

    return fig