# 🗺️ map-from-txt-leaflet

**Be API rakto.** Programa perskaito `.txt` failą, randa `Latitude/Longitude` ir parodo žemėlapyje su **Leaflet + OpenStreetMap** (atidaroma naršyklėje per `http://localhost`).

## Naudojimas
```bash
python map_from_txt_leaflet.py path/to/koordinates.txt
```
Arba su EXE (Windows):
```cmd
map_from_txt_leaflet.exe path\to\koordinates.txt
```

## Palaikomi formatai `.txt` faile
- `54.6872, 25.2797`
- `Latitude: 54.6872` + `Longitude: 25.2797`
- Sekos: `54.9 23.9 55.7 21.1 ...` (interpretuojama poromis lat lon)

## EXE kūrimas (Windows)
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name map_from_txt_leaflet map_from_txt_leaflet.py
```
Rezultatas: `dist/map_from_txt_leaflet.exe`

## GitHub Actions (automatinis EXE)
Workflows failas: `/.github/workflows/build-exe.yml`. Po kiekvieno `push` sukuria `.exe` ir prideda kaip **Artifacts**.

## Pastabos dėl OpenStreetMap
Naudojami vieši OSM plytelių serveriai (`tile.openstreetmap.org`) – smulkiam naudojimui tinka. Masiniam srautui naudok savo tile paslaugą arba MapTiler/Thunderforest (gali reikėti rakto).
