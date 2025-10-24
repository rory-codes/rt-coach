# workout/services.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# === Heart-rate zones (Karvonen HRR) ===
ZONES_DEF = [
    ("Zone 1", 0.50, 0.60),
    ("Zone 2", 0.60, 0.70),
    ("Zone 3", 0.70, 0.80),
    ("Zone 4", 0.80, 0.90),
    ("Zone 5", 0.90, 1.00),
]

# Phase %1RM mid-points used for sets x reps prescriptions
PHASE_PCT_1RM = {
    "endurance": 0.50,
    "hypertrophy": 0.70,
    "strength": 0.85,
    "power": 0.62,  # explosive technique
}

# Default 10 exercises we’ve been using
DEFAULT_EXERCISES = [
    "Chest Press", "Shoulder Press", "Lat Pull Down", "Seated Row",
    "Leg Press", "Deadlift", "Squat", "Upright Row", "Bicep Curl", "Tricep Pushdown"
]

# Split exercises over 3 days (Push / Pull / Legs)
DAY_SPLIT = {
    1: ["Chest Press", "Shoulder Press", "Tricep Pushdown"],
    2: ["Lat Pull Down", "Seated Row", "Upright Row", "Bicep Curl"],
    3: ["Squat", "Deadlift", "Leg Press"],
}

# Per-phase prescriptions (sets, reps, RPE, rest, tempo)
PHASE_PRESCRIPTION = {
    "endurance": {"sets": 3, "reps": 15, "rpe": "6", "rest_s": 60,  "tempo": "2010"},
    "hypertrophy": {"sets": 4, "reps": 10, "rpe": "7–8", "rest_s": 90,  "tempo": "3010"},
    "strength": {"sets": 5, "reps": 5,  "rpe": "8–9", "rest_s": 180, "tempo": "20X0"},
    "power": {"sets": 6, "reps": 3,  "rpe": "7",   "rest_s": 120, "tempo": "X0X0"},
}

# Phase → warmup/mobility snippets
PHASE_WARMUPS = {
    "endurance": "5–7 min easy bike/row + dynamic full-body mobility",
    "hypertrophy": "5 min light cardio + joint circles + band activation",
    "strength": "RAMP warm-up (raise/activate/mobilize/potentiate) + barbell ramps",
    "power": "Dynamic plyos + 5 min spin + movement prep (jumps/med-ball)",
}
PHASE_MOBILITY = {
    "endurance": "Foam roll 5' + hip openers + T-spine rotations",
    "hypertrophy": "Foam roll 5' + pec/lat stretch + ankle mobility",
    "strength": "90/90 hip switches, hamstring flossing, T-spine openers",
    "power": "Ankles/calf mobility, hip airplanes, shoulder CARs",
}

@dataclass
class Metrics:
    age: Optional[int] = None
    rhr: Optional[int] = None
    # map exercise -> 10rm (kg)
    tenrm: Optional[Dict[str, float]] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None

def _clamp(v, lo, hi):
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, v))

def calc_max_hr(age: Optional[float]) -> Optional[int]:
    age = _clamp(age, 1, 120)
    if age is None:
        return None
    return int(round(220 - age))

def calc_zones(age: Optional[float], rhr: Optional[float]) -> List[Dict]:
    age = _clamp(age, 1, 120)
    rhr = _clamp(rhr, 20, 150)
    max_hr = calc_max_hr(age)
    if max_hr is None or rhr is None or rhr >= max_hr:
        return []
    hrr = max_hr - rhr
    out = []
    for name, lo, hi in ZONES_DEF:
        out.append({
            "name": name,
            "lo_pct": lo, "hi_pct": hi,
            "lo_bpm": int(round(rhr + hrr * lo)),
            "hi_bpm": int(round(rhr + hrr * hi)),
        })
    return out

def estimate_1rm_from_10rm(tenrm: Optional[float]) -> Optional[float]:
    if tenrm is None:
        return None
    try:
        tenrm = float(tenrm)
    except (TypeError, ValueError):
        return None
    if tenrm <= 0:
        return None
    # Epley for 10 reps: w * (1 + 10/30)
    return tenrm * (1 + 10.0 / 30.0)

def split_weeks_by_goal(goal: str) -> List[str]:
    """
    Returns a 12-element list of phase names (endurance/hypertrophy/strength/power).
    """
    g = (goal or "").lower()
    if g == "cardio":
        return ["endurance"] * 6 + ["hypertrophy"] * 3 + ["strength"] * 2 + ["power"]
    if g == "strength":
        return ["endurance"] * 2 + ["hypertrophy"] * 4 + ["strength"] * 4 + ["power"] * 2
    # balanced
    return ["endurance"] * 3 + ["hypertrophy"] * 3 + ["strength"] * 4 + ["power"] * 2

def weekly_cardio_sessions(experience: str) -> int:
    e = (experience or "").lower()
    return {"beginner": 2, "intermediate": 3, "experienced": 4}.get(e, 3)

def weekly_strength_sessions(experience: str) -> int:
    e = (experience or "").lower()
    return {"beginner": 2, "intermediate": 3, "experienced": 4}.get(e, 3)

def cardio_minutes_by_phase(phase: str, experience: str) -> Tuple[int, int]:
    """(per-session minutes, target zone index 0..4)"""
    e = (experience or "").lower()
    if phase == "endurance":
        minutes = {"beginner": 25, "intermediate": 35, "experienced": 45}[e]
        zone = 1  # Zone 2
    elif phase == "hypertrophy":
        minutes = {"beginner": 20, "intermediate": 30, "experienced": 35}[e]
        zone = 2  # Zone 3
    elif phase == "strength":
        minutes = {"beginner": 15, "intermediate": 20, "experienced": 25}[e]
        zone = 2  # Zone 3 (shorter)
    else:  # power
        minutes = {"beginner": 15, "intermediate": 20, "experienced": 20}[e]
        zone = 3  # Zone 4 intervals
    return minutes, zone

def _compose_exercise_line(name: str, sets: int, reps: int, pct: float, rpe: str, rest_s: int, tempo: str, load_kg: Optional[float]) -> str:
    pct_str = f"{int(round(pct*100))}%"
    load_str = f"{load_kg:.1f}kg" if load_kg is not None else "—"
    return f"{name} — {sets}×{reps} @ {pct_str} 1RM ({load_str}), RPE {rpe}, rest {rest_s}s, tempo {tempo}"

def _exercise_rows_for_day(day_idx: int, phase: str, one_rm_map: Dict[str, Optional[float]]) -> List[Dict]:
    exs = DAY_SPLIT.get(day_idx, [])
    pres = PHASE_PRESCRIPTION[phase]
    pct = PHASE_PCT_1RM[phase]
    rows = []
    for ex in exs:
        one_rm = one_rm_map.get(ex)
        load = round(one_rm * pct, 1) if one_rm else None
        rows.append({
            "name": ex,
            "sets": pres["sets"],
            "reps": pres["reps"],
            "pct_1rm": pct,
            "load_kg": load,
            "rpe": pres["rpe"],
            "rest_s": pres["rest_s"],
            "tempo": pres["tempo"],
            "human": _compose_exercise_line(
                ex, pres["sets"], pres["reps"], pct, pres["rpe"], pres["rest_s"], pres["tempo"], load
            )
        })
    return rows

def build_plan(experience: str, goal: str, metrics: Metrics) -> Dict:
    """
    Returns structured plan with weeks and **days**:
    {
      meta: {...},
      zones: [...],
      weeks: [{
        week: 1,
        phase: "endurance",
        days: [{
          day: 1,
          warmup: "...",
          workout_rows: [ {name, sets, reps, pct_1rm, load_kg, rpe, rest_s, tempo, human}, ... ],
          workout_text: "Squat — 3×15 ... | Lat Pull Down — 3×15 ...",
          cardio: { minutes: 30, zone: "Zone 2", bpm: (128,142) },
          mobility: "..."
        }, ...]
      }, ...]
    }
    """
    zones = calc_zones(metrics.age, metrics.rhr)

    # TenRM → OneRM map
    tenrm_map = metrics.tenrm or {}
    one_rm_map = {ex: estimate_1rm_from_10rm(tenrm_map.get(ex)) for ex in DEFAULT_EXERCISES}

    weeks = split_weeks_by_goal(goal)
    out_weeks = []
    for w in range(12):
        phase = weeks[w]
        minutes, zone_idx = cardio_minutes_by_phase(phase, experience)
        zdef = zones[zone_idx] if zones and 0 <= zone_idx < len(zones) else None

        days = []
        for day_idx in (1, 2, 3):
            rows = _exercise_rows_for_day(day_idx, phase, one_rm_map)
            workout_text = " | ".join(r["human"] for r in rows)
            days.append({
                "day": day_idx,
                "warmup": PHASE_WARMUPS[phase],
                "workout_rows": rows,
                "workout_text": workout_text,
                "cardio": {
                    "minutes": minutes,
                    "zone": zdef["name"] if zdef else None,
                    "bpm": (zdef["lo_bpm"], zdef["hi_bpm"]) if zdef else None
                },
                "mobility": PHASE_MOBILITY[phase],
            })

        out_weeks.append({
            "week": w + 1,
            "phase": phase,
            "days": days,
        })

    return {
        "meta": {
            "experience": experience,
            "goal": goal,
            "age": metrics.age,
            "rhr": metrics.rhr,
        },
        "zones": zones,
        "weeks": out_weeks,
    }

# ---------- CSV export helper ----------

CSV_COLUMNS = ["Week", "Day", "Phase", "Warm-Up", "Workout", "Cardio", "Mobility"]

def plan_to_rows(plan_json: Dict) -> List[Dict[str, str]]:
    """
    Flattens plan to rows matching your CSV:
    Week, Day, Phase, Warm-Up, Workout, Cardio, Mobility
    """
    rows: List[Dict[str, str]] = []
    for wk in plan_json.get("weeks", []):
        week_label = f"Week {wk.get('week')}"
        phase = wk.get("phase", "").title()
        for d in wk.get("days", []):
            cardio = d.get("cardio", {})
            zone = cardio.get("zone")
            bpm = cardio.get("bpm")
            cardio_txt = ""
            if zone and bpm:
                cardio_txt = f"{zone} — {cardio.get('minutes')} mins ({bpm[0]}–{bpm[1]} bpm)"
            elif zone:
                cardio_txt = f"{zone} — {cardio.get('minutes')} mins"
            elif cardio.get("minutes"):
                cardio_txt = f"{cardio.get('minutes')} mins"

            rows.append({
                "Week": week_label,
                "Day": f"Day {d.get('day')}",
                "Phase": phase,
                "Warm-Up": d.get("warmup", ""),
                "Workout": d.get("workout_text", ""),
                "Cardio": cardio_txt,
                "Mobility": d.get("mobility", ""),
            })
    return rows
