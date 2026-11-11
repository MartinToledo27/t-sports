"""Baja de ESPN los promedios de la temporada (equipos y jugadores) y los guarda en estadisticas.json."""
import json, sys, time, urllib.request
from datetime import datetime, timezone

B = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
BA = ["https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete",
      "https://site.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete"]
TID = {"ATL": 1, "BOS": 2, "BKN": 17, "CHA": 30, "CHI": 4, "CLE": 5, "DAL": 6, "DEN": 7, "DET": 8, "GSW": 9,
       "HOU": 10, "IND": 11, "LAC": 12, "LAL": 13, "MEM": 29, "MIA": 14, "MIL": 15, "MIN": 16, "NOP": 3,
       "NYK": 18, "OKC": 25, "ORL": 19, "PHI": 20, "PHX": 21, "POR": 22, "SAC": 23, "SAS": 24, "TOR": 28,
       "UTA": 26, "WAS": 27}
CLAVES = ["avgPoints", "fieldGoalPct", "threePointFieldGoalPct", "freeThrowPct", "avgRebounds", "avgAssists",
          "avgSteals", "avgBlocks", "avgTurnovers", "avgOffensiveRebounds", "gamesPlayed"]
CLAVES_OV = ["avgPointsAgainst", "differential", "streak"]
ARCHIVO = "estadisticas.json"


def get(url):
    ultimo = None
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            ultimo = e
            time.sleep(2 + i * 2)
    raise ultimo


def r2(v):
    return round(v, 2) if isinstance(v, (int, float)) else v


def parse_equipo(j1, j2):
    st = {}
    for c in ((j1.get("results") or {}).get("stats") or {}).get("categories") or []:
        for x in c.get("stats") or []:
            st.setdefault(x.get("name"), x.get("value"))
    team = j2.get("team") or {}
    items = (team.get("record") or {}).get("items") or []

    def pick(tipo):
        return next((x for x in items if x.get("type") == tipo), {})

    tot = pick("total")
    ov = {s.get("name"): s.get("value") for s in tot.get("stats") or []}
    return {"st": {k: r2(st.get(k)) for k in CLAVES if st.get(k) is not None},
            "ov": {k: r2(ov.get(k)) for k in CLAVES_OV if ov.get(k) is not None},
            "sum": {"t": tot.get("summary", ""), "h": pick("home").get("summary", ""), "a": pick("road").get("summary", "")},
            "stand": team.get("standingSummary", "")}


def parse_jugadores(j, out):
    nombres = [c.get("names") or [] for c in j.get("categories") or []]
    for a in j.get("athletes") or []:
        m = {}
        for i, c in enumerate(a.get("categories") or []):
            nm = nombres[i] if i < len(nombres) else []
            for k, v in enumerate(c.get("values") or []):
                if k < len(nm) and nm[k] and nm[k] not in m:
                    m[nm[k]] = v
        gp = m.get("gamesPlayed") or 0
        if not gp:
            continue
        at = a.get("athlete") or {}
        t = str(a.get("teamId") or at.get("teamId") or "")
        if not t:
            continue
        out.setdefault(t, []).append({
            "n": at.get("shortName") or at.get("displayName") or "?",
            "pos": (at.get("position") or {}).get("abbreviation", ""),
            "gp": gp, "mpg": r2(m.get("avgMinutes")), "pts": r2(m.get("avgPoints")),
            "reb": r2(m.get("avgRebounds")), "ast": r2(m.get("avgAssists")), "stl": r2(m.get("avgSteals")),
            "blk": r2(m.get("avgBlocks")), "to": r2(m.get("avgTurnovers")),
            "fg": r2(m.get("fieldGoalPct")) if m.get("avgFieldGoalsAttempted") else None,
            "tp": r2(m.get("threePointFieldGoalPct")) if m.get("avgThreePointFieldGoalsAttempted") else None,
            "ft": r2(m.get("freeThrowPct")) if m.get("avgFreeThrowsAttempted") else None})


def pagina_jugadores(temp, p):
    q = ("?region=us&lang=en&contentorigin=espn&isqualified=false&limit=50&sort=offensive.avgPoints%3Adesc"
         "&season=" + str(temp) + "&seasontype=2&page=" + str(p))
    ultimo = None
    for base in BA:
        try:
            return get(base + q)
        except Exception as e:
            ultimo = e
    raise ultimo


def main():
    try:
        viejo = json.load(open(ARCHIVO, encoding="utf-8"))
    except Exception:
        viejo = {}
    ahora = datetime.now(timezone.utc)
    temp = ahora.year + 1 if ahora.month >= 9 else ahora.year
    equipos, temporada = dict(viejo.get("equipos") or {}), viejo.get("temporada", "")
    for cod, tid in TID.items():
        try:
            j1, j2 = get(f"{B}/teams/{tid}/statistics"), get(f"{B}/teams/{tid}")
            equipos[cod] = parse_equipo(j1, j2)
            temporada = (j1.get("season") or {}).get("displayName") or temporada
        except Exception as e:
            print("Equipo salteado", cod, e)
        time.sleep(0.3)
    jugadores = {}
    try:
        j1 = pagina_jugadores(temp, 1)
        parse_jugadores(j1, jugadores)
        for p in range(2, min(((j1.get("pagination") or {}).get("pages")) or 1, 20) + 1):
            parse_jugadores(pagina_jugadores(temp, p), jugadores)
            time.sleep(0.3)
        for lista in jugadores.values():
            lista.sort(key=lambda x: -(x["pts"] or 0))
    except Exception as e:
        print("Jugadores: error", e)
        jugadores = viejo.get("jugadores") or {}
    if not equipos and not jugadores:
        print("Sin datos; no se escribe nada")
        sys.exit(1)
    nuevo = {"temporada": temporada, "equipos": equipos, "jugadores": jugadores}
    if nuevo == {k: v for k, v in viejo.items() if k != "actualizado"}:
        print("Sin cambios")
        return
    nuevo["actualizado"] = ahora.strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(nuevo, f, ensure_ascii=False, separators=(",", ":"))
    print("estadisticas.json:", len(equipos), "equipos,", sum(len(v) for v in jugadores.values()), "jugadores")


if __name__ == "__main__":
    main()
