# app.py - ACEest Fitness & Gym REST API v3.0
# Assignment 2 - Version 3.0 (Latest)
from flask import Flask, jsonify, request

app = Flask(__name__)

# ── In-memory store ──────────────────────────────────────────
members = {}

PROGRAMS = {
    "Fat Loss": {
        "short_code": "FL",
        "calorie_factor": 22,
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "nutrition": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal"
    },
    "Muscle Gain": {
        "short_code": "MG",
        "calorie_factor": 35,
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "nutrition": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal"
    },
    "Beginner Gym": {
        "short_code": "BG",
        "calorie_factor": 26,
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
        "nutrition": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day"
    }
}

APP_VERSION = "3.0.0"

# ── Helper ───────────────────────────────────────────────────
def find_program(name):
    name_lower = name.lower()
    for prog_name, prog_data in PROGRAMS.items():
        if (prog_name.lower() == name_lower or
                prog_data["short_code"].lower() == name_lower):
            return prog_name, prog_data
    return None, None

# ── Routes ───────────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "service": "ACEest Fitness & Gym API",
        "version": APP_VERSION,
        "status": "running",
        "endpoints": [
            "GET /health",
            "GET /version",
            "GET /programs",
            "GET /programs/<name>",
            "GET /calories/<program>/<weight>",
            "POST /members",
            "GET /members",
            "GET /members/<name>"
        ]
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "aceest-fitness-api", "version": APP_VERSION})

@app.route("/version")
def version():
    return jsonify({"version": APP_VERSION, "app": "ACEest Fitness & Gym"})

@app.route("/programs")
def get_programs():
    return jsonify({"programs": list(PROGRAMS.keys()), "count": len(PROGRAMS)})

@app.route("/programs/<name>")
def get_program(name):
    prog_name, prog_data = find_program(name)
    if not prog_name:
        return jsonify({"error": f"Program '{name}' not found"}), 404
    return jsonify({"program": prog_name, **prog_data})

@app.route("/calories/<program>/<weight>")
def calculate_calories(program, weight):
    try:
        weight_kg = float(weight)
    except ValueError:
        return jsonify({"error": "Weight must be a number"}), 400
    if weight_kg <= 0 or weight_kg > 300:
        return jsonify({"error": "Weight must be between 1 and 300 kg"}), 400
    prog_name, prog_data = find_program(program)
    if not prog_name:
        return jsonify({"error": f"Program '{program}' not found"}), 404
    calories = round(weight_kg * prog_data["calorie_factor"])
    return jsonify({
        "program": prog_name,
        "weight_kg": weight_kg,
        "daily_calories": calories,
        "calorie_factor": prog_data["calorie_factor"]
    })

@app.route("/members", methods=["POST"])
def add_member():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    data = request.get_json()
    name = data.get("name", "").strip()
    program = data.get("program", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    if not program:
        return jsonify({"error": "program is required"}), 400
    prog_name, _ = find_program(program)
    if not prog_name:
        return jsonify({"error": f"Program '{program}' not found"}), 400
    if name in members:
        return jsonify({"error": f"Member '{name}' already exists"}), 409
    members[name] = {"name": name, "program": prog_name}
    return jsonify({"message": f"Member '{name}' registered successfully", "member": members[name]}), 201

@app.route("/members")
def get_members():
    return jsonify({"members": list(members.values()), "count": len(members)})

@app.route("/members/<name>")
def get_member(name):
    if name not in members:
        return jsonify({"error": f"Member '{name}' not found"}), 404
    return jsonify(members[name])

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
