# herzensgedanken-pins

Pin-Bilder für [johannesfies.de](https://johannesfies.de) – „Herzensgedanken“ auf Pinterest.
Erzeugt von der Herzensgedanken-Crew (Claude), veröffentlicht über Buffer.

## Aufbau

- `render.py` – baut einen Pin (1000 × 1500 px). Variante `a` = Unsplash-Foto mit weißer Schrift, Variante `b` = Typografie auf Cremegrund mit Spirale.
- `fonts/` – Cormorant Garamond (SIL Open Font License, siehe `fonts/OFL.txt`)
- `assets/spirale.png` – Johannes' Spirale
- `pins/` – fertige Pins, Dateiname `JJJJ-MM-TT-<Zitat-ID>-<a|b>.jpg`

## Ablauf in der Cloud

```bash
git clone --depth 1 https://github.com/levatc/herzensgedanken-pins
cd herzensgedanken-pins
python3 render.py --variant a --photo "<Unsplash-URL aus download_asset>&w=1400" \
  --text "Zeile 1|Zeile 2|Zeile 3" --out pins/2026-12-01-Z02-a.jpg
python3 render.py --variant b --text "Zitat" --out pins/2026-12-02-Z14-b.jpg
git add pins && git commit -m "Pins KW 49" && git -c push.negotiate=true push origin main
```

Öffentliche Bild-URL für Buffer:
`https://raw.githubusercontent.com/levatc/herzensgedanken-pins/main/pins/<datei>.jpg`

Vor dem Einplanen jedes Bild ansehen: Text lesbar, kein Wort allein in einer Zeile, Fußzeile unten.

Fotos: Unsplash, immer über `download_asset` (Unsplash-Lizenz, kein Unsplash+).
