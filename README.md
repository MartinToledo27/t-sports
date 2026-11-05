# T-Sports

Agenda deportiva para Argentina (hora UTC−3): NBA y F1 en una sola página, instalable en el celular.

- `index.html` portada: logo animado, selector NBA / F1 y botón de tema (automático / claro / oscuro).
- `tema.css` estilos y tipografía compartidos por las dos agendas.
- `nba/` y `f1/` cada agenda con su robot (`actualizar.py`) y sus datos (`data.json`).
- `manifest.webmanifest`, `sw.js`, `icon-*.png` para instalarla como app.
- `.github/workflows/` un robot por deporte: NBA cada 15 min, F1 cada 30 min (también a mano).
