#!/usr/bin/env python3
# map_from_txt_leaflet.py
# Skaito .txt, randa koordinates, sugeneruoja Leaflet+OSM HTML,
# paleidžia lokalų HTTP serverį ir atidaro naršyklę. API rakto nereikia.

import re, tempfile, webbrowser, sys, os, socket, http.server, threading
from pathlib import Path

COORD_RE = re.compile(r"([-+]?\d{1,3}\.\d+)")
PAIR_RE = re.compile(r"([-+]?\d{1,3}\.\d+)\s*[,;\s]\s*([-+]?\d{1,3}\.\d+)")

def parse_coordinates(text: str):
    coords = []
    # 1) tiesioginės poros "lat, lon"
    for m in PAIR_RE.finditer(text):
        lat, lon = float(m.group(1)), float(m.group(2))
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            coords.append((lat, lon))
    # 2) "Latitude" / "Longitude"
    lat_vals = re.findall(r"Latitude[:=\s]*([-+]?\d{1,3}\.\d+)", text, flags=re.IGNORECASE)
    lon_vals = re.findall(r"Longitude[:=\s]*([-+]?\d{1,3}\.\d+)", text, flags=re.IGNORECASE)
    if len(lat_vals) == len(lon_vals) and len(lat_vals) > 0:
        for la, lo in zip(lat_vals, lon_vals):
            la_f, lo_f = float(la), float(lo)
            if -90 <= la_f <= 90 and -180 <= lo_f <= 180:
                coords.append((la_f, lo_f))
    # 3) seka: lat lon lat lon
    if not coords:
        nums = [float(n) for n in COORD_RE.findall(text)]
        for i in range(0, len(nums)-1, 2):
            lat, lon = nums[i], nums[i+1]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                coords.append((lat, lon))
    # dedup
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

def find_free_port():
    import socket
    s = socket.socket(); s.bind(('',0)); port = s.getsockname()[1]; s.close(); return port

def serve_file_and_open(html_path: Path):
    port = find_free_port()
    handler = http.server.SimpleHTTPRequestHandler
    cwd = html_path.parent
    os.chdir(str(cwd))
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    url = f'http://127.0.0.1:{port}/{html_path.name}'
    print("Atidaroma naršyklė:", url)
    threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()

def process_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    coords = parse_coordinates(text)
    if not coords:
        print("Nerasta koordinačių.")
        return
    html = make_leaflet_html(coords, title=path.name)
    out = Path(tempfile.gettempdir()) / f"leaflet_map_{os.getpid()}.html"
    out.write_text(html, encoding='utf-8')
    serve_file_and_open(out)

if __name__ == '__main__':
    if len(sys.argv)>1:
        p = Path(sys.argv[1])
        if not p.exists(): print("Failas nerastas:", p); sys.exit(1)
        process_file(p)
    else:
        # galima praplėsti su failo dialogu, bet kad EXE būtų be papildomų priklausomybių – paliekam paprastai
        print("Naudojimas: map_from_txt_leaflet.exe path\\to\\file.txt (arba python map_from_txt_leaflet.py path/to/file.txt)")
