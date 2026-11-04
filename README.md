# T-Sports

Agenda deportiva para Argentina (hora UTC−3): NBA y F1 en una sola página.

- `index.html` portada con el logo y el selector NBA / F1 (carga cada agenda en su carpeta).
- `nba/` agenda NBA: `index.html`, `actualizar.py` (robot), `data.json`, `plataformas.json`.
- `f1/` agenda F1: `index.html`, `actualizar.py` (robot), `data.json`.
- `.github/workflows/` un robot por deporte: NBA cada 15 min, F1 cada 30 min (también a mano).

Cada agenda también funciona sola en `/nba/` y `/f1/`.
