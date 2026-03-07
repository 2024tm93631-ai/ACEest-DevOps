from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# ─── Data Store ───────────────────────────────────────────────────────────────

PROGRAMS = {
    "Fat Loss (FL)": {
        "code": "FL",
        "workout": [
            "Mon: Back Squat 5x5 + Core",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: Deadlift + Box Jumps",
            "Fri: Zone 2 Cardio 30min"
        ],
        "diet": {
            "breakfast": "Egg Whites + Oats",
            "lunch": "Grilled Chicken + Brown Rice",
            "dinner": "Fish Curry + Millet Roti",
            "target_kcal": 2000
        },
        "calorie_factor": 22,
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "code": "MG",
        "workout": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10"
        ],
        "diet": {
            "breakfast": "Eggs + Peanut Butter Oats",
            "lunch": "Chicken Biryani (250g Chicken)",
            "dinner": "Mutton Curry + Jeera Rice",
            "target_kcal": 3200
        },
        "calorie_factor": 35,
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "code": "BG",
        "workout": [
            "Full Body Circuit: Air Squats",
            "Ring Rows",
            "Push-ups",
            "Focus: Technique & Consistency"
        ],
        "diet": {
            "breakfast": "Idli / Dosa with Sambar",
            "lunch": "Rice + Dal + Vegetables",
            "dinner": "Chapati + Curry",
            "target_kcal": 2200
        },
        "calorie_factor": 26,
        "color": "#3498db"
    }
}

# In-memory member store (simulates database)
members = {}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Home endpoint - returns API info."""
    return jsonify({
        "app": "ACEest Fitness & Gym",
        "version": "2.0",
        "description": "Automated CI/CD Pipeline Demo - DevOps Assignment",
        "endpoints": {
            "GET /": "This info page",
            "GET /health": "Health check",
            "GET /programs": "List all fitness programs",
            "GET /programs/<name>": "Get a specific program details",
            "GET /calories/<program>/<weight>": "Calculate calories for weight (kg)",
            "POST /members": "Register a new member",
            "GET /members": "List all members",
            "GET /members/<name>": "Get a specific member"
        }
    })


@app.route("/health")
def health():
    """Health check for CI/CD pipeline."""
    return jsonify({"status": "healthy", "service": "aceest-fitness-api"}), 200


@app.route("/programs")
def get_programs():
    """Return all available fitness programs."""
    summary = []
    for name, data in PROGRAMS.items():
        summary.append({
            "name": name,
            "code": data["code"],
            "calorie_factor": data["calorie_factor"],
            "target_kcal": data["diet"]["target_kcal"]
        })
    return jsonify({"programs": summary, "total": len(summary)})


@app.route("/programs/<string:program_name>")
def get_program(program_name):
    """Return details of a specific program."""
    # Support both full name and short code (FL, MG, BG)
    matched = None
    for name, data in PROGRAMS.items():
        if (name.lower() == program_name.lower() or
                data["code"].lower() == program_name.lower()):
            matched = (name, data)
            break

    if not matched:
        abort(404, description=f"Program '{program_name}' not found.")

    name, data = matched
    return jsonify({
        "name": name,
        "code": data["code"],
        "workout_plan": data["workout"],
        "nutrition_plan": data["diet"],
        "calorie_factor": data["calorie_factor"]
    })


@app.route("/calories/<string:program_name>/<float:weight_kg>")
def calculate_calories(program_name, weight_kg):
    """Calculate estimated daily calories for a given program and body weight."""
    if weight_kg <= 0 or weight_kg > 300:
        abort(400, description="Weight must be between 1 and 300 kg.")

    matched = None
    for name, data in PROGRAMS.items():
        if (name.lower() == program_name.lower() or
                data["code"].lower() == program_name.lower()):
            matched = (name, data)
            break

    if not matched:
        abort(404, description=f"Program '{program_name}' not found.")

    name, data = matched
    estimated_calories = int(weight_kg * data["calorie_factor"])
    return jsonify({
        "program": name,
        "weight_kg": weight_kg,
        "estimated_daily_calories": estimated_calories
    })


@app.route("/members", methods=["POST"])
def add_member():
    """Register a new gym member."""
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON.")

    required = ["name", "age", "weight_kg", "program"]
    for field in required:
        if field not in body:
            abort(400, description=f"Missing required field: '{field}'")

    name = body["name"].strip()
    if not name:
        abort(400, description="Member name cannot be empty.")

    if name in members:
        abort(409, description=f"Member '{name}' already exists.")

    # Validate program
    program_valid = any(
        p.lower() == body["program"].lower() or
        PROGRAMS[p]["code"].lower() == body["program"].lower()
        for p in PROGRAMS
    )
    if not program_valid:
        abort(400, description=f"Invalid program: '{body['program']}'")

    members[name] = {
        "name": name,
        "age": body["age"],
        "weight_kg": body["weight_kg"],
        "program": body["program"],
        "adherence_percent": body.get("adherence_percent", 0)
    }

    return jsonify({"message": f"Member '{name}' registered successfully.", "member": members[name]}), 201


@app.route("/members", methods=["GET"])
def get_members():
    """List all registered members."""
    return jsonify({"members": list(members.values()), "total": len(members)})


@app.route("/members/<string:name>", methods=["GET"])
def get_member(name):
    """Get details of a specific member."""
    if name not in members:
        abort(404, description=f"Member '{name}' not found.")
    return jsonify(members[name])


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request", "message": str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": str(e.description)}), 404


@app.errorhandler(409)
def conflict(e):
    return jsonify({"error": "Conflict", "message": str(e.description)}), 409


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)