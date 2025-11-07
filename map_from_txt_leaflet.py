#!/usr/bin/env python3
# map_from_txt_leaflet_fileurl_gui.py
# Be API rakto. Paprastesnis variantas: nenaudoja vietinio serverio – atidaro HTML per file://

import re, tempfile, webbrowser, sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk = None

COORD_RE = re.compile(r"([-+]?\d{1,3}\.\d+)")
PAIR_RE = re.compile(r"([-+]?\d{1,3}\.\d+)\s*[,;\s]\s*([-+]?\d{1,3}\.\d+)")

def parse_coordinates(text: str):
    coords = []
    for m in PAIR_RE.finditer(text):
        lat, lon = float(m.group(1)), float(m.group(2))
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            coords.append((lat, lon))
    lat_vals = re.findall(r"Latitude[:=\s]*([-+]?\d{1,3}\.\d+)", text, flags=re.IGNORECASE)
    lon_vals = re.findall(r"Longitude[:=\s]*([-+]?\d{1,3}\.\d+)", text, flags=re.IGNORECASE)
    if len(lat_vals) == len(lon_vals) and len(lat_vals) > 0:
        for la, lo in zip(lat_vals, lon_vals):
            la_f, lo_f = float(la), float(lo)
            if -90 <= la_f <= 90 and -180 <= lo_f <= 180:
                coords.append((la_f, lo_f))
    if not coords:
        nums = [float(n) for n in COORD_RE.findall(text)]
        for i in range(0, len(nums)-1, 2):
            lat, lon = nums[i], nums[i+1]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                coords.append((lat, lon))
    seen = set(); uniq = []
    for c in coords:
        if c not in seen:
            seen.add(c); uniq.append(c)
    return uniq

def make_leaflet_html(coords, title="Žemėlapis"):
    center = coords[0] if coords else (0,0)
    markers = "\n".join([f"L.marker([{lat},{lon}]).addTo(map).bindPopup('{lat}, {lon}');" for lat,lon in coords])
    if len(coords) > 1:
        bounds = ",\n        ".join([f"[{lat},{lon}]" for lat,lon in coords])
        fit = f"""var bounds = L.latLngBounds([{bounds}]);\n    map.fitBounds(bounds);"""
    else:
        fit = f"map.setView([{center[0]}, {center[1]}], 12);"
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>html,body,#map{{height:100%;margin:0;padding:0}}#map{{height:100vh}}</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('map');
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}}).addTo(map);
{markers}
{fit}
</script>
</body>
</html>
"""
    return html

def choose_file_dialog():
    if tk is None:
        return None
    root = tk.Tk(); root.withdraw()
    path = filedialog.askopenfilename(
        title="Pasirink .txt failą su koordinatėmis",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    return path

def show_error(msg: str):
    if tk is not None:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Klaida", msg)
        root.destroy()
    else:
        print(msg)

def process_file(path: Path):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        show_error(f"Nepavyko perskaityti failo:\n{e}")
        return
    coords = parse_coordinates(text)
    if not coords:
        show_error("Nerasta koordinačių šiame faile.")
        return
    html = make_leaflet_html(coords, title=path.name)
    out = Path(tempfile.gettempdir()) / "leaflet_map_fileurl.html"
    out.write_text(html, encoding='utf-8')
    webbrowser.open(out.as_uri())  # file://
    # programa gali baigtis – naršyklė vis tiek atidarys failą

if __name__ == '__main__':
    if len(sys.argv)>1:
        p = Path(sys.argv[1])
        if not p.exists():
            show_error(f"Failas nerastas:\n{p}")
            sys.exit(1)
        process_file(p)
    else:
        chosen = choose_file_dialog()
        if chosen:
            process_file(Path(chosen))
        else:
            show_error("Failas nepasirinktas.")
