from flask import Flask, request, jsonify, redirect, url_for
from fpdf import FPDF

app = Flask(__name__)

# Global data
user_info = {}
workouts = {
    "Warm-up": [],
    "Workout": [],
    "Cool-down": []
}


@app.route("/")
def index():
    return "<h1>Welcome to ACEest Fitness App</h1>"


@app.route("/save_user_info", methods=["POST"])
  
def save_user_info():
    """Save user information (form submission)."""
    # Don't reassign global user_info; update in place
    user_info.clear()
    user_info.update({
        "name": request.form.get("name"),
        "regn_id": request.form.get("regn_id"),
        "age": request.form.get("age", type=float),
        "gender": request.form.get("gender"),
        "height": request.form.get("height", type=float),
        "weight": request.form.get("weight", type=float),
    })

    if not all(user_info.values()):
        return jsonify({"error": "Missing fields"}), 400

    # Compute BMI and BMR
    height_m = user_info["height"] / 100
    user_info["bmi"] = round(user_info["weight"] / (height_m**2), 2)

    if user_info["gender"].lower() == "m":
        user_info["bmr"] = round(
            10 * user_info["weight"] + 6.25 * user_info["height"] - 5 * user_info["age"] + 5, 2
        )
    else:
        user_info["bmr"] = round(
            10 * user_info["weight"] + 6.25 * user_info["height"] - 5 * user_info["age"] - 161, 2
        )

    return jsonify(user_info)
@app.route("/add", methods=["POST"])
def add_workout():
    """Add a workout entry with calories burned calculation."""
    category = request.form.get("category")
    exercise = request.form.get("exercise")
    duration = request.form.get("duration", type=float)

    if category not in workouts:
        return jsonify({"error": "Invalid category"}), 400

    # Example MET (Metabolic Equivalent of Task) values
    met_values = {
        "Jumping Jacks": 3.0,
        "Running": 9.8,
        "Cycling": 7.5,
        "Push-ups": 8.0,
        "Yoga": 2.5,
    }
    met = met_values.get(exercise, 3.0)
    weight = user_info.get("weight", 70)
    calories = met * 3.5 * weight / 200 * duration

    entry = {"exercise": exercise, "duration": duration, "calories": calories}
    workouts[category].append(entry)
    return redirect(url_for("summary"))


@app.route("/summary")
def summary():
    """Show a summary of workouts."""
    summary_lines = []
    total_calories = 0
    total_minutes = 0

    for cat, data in workouts.items():
        for entry in data:
            total_calories += entry["calories"]
            total_minutes += entry["duration"]
            # 👇 Convert duration to int to remove .0
            summary_lines.append(f"{entry['exercise']} - {int(entry['duration'])} min ({entry['calories']:.1f} kcal)")
 
    if not summary_lines:
        summary_lines.append("No workouts logged yet.")

    html = "<br>".join(summary_lines)
    html += f"<br><b>Total Calories:</b> {total_calories:.1f} kcal"
    html += f"<br><b>Total Duration:</b> {int(total_minutes)} minutes"
    return html


@app.route("/progress")
def progress():
    """Show progress summary."""
    total_minutes = sum(entry["duration"] for cat in workouts.values() for entry in cat)
    if total_minutes == 0:
        return "No workout data logged yet."
    return f"LIFETIME TOTAL: {int(total_minutes)} minutes"


@app.route("/export_pdf")
def export_pdf():
    """Export a dummy PDF report."""
    if not user_info:
        return jsonify({"error": "No user info"}), 400

    filename = f"{user_info['name'].replace(' ', '_')}_weekly_report.pdf"

    # Generate a simple PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Weekly Fitness Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Name: {user_info['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Total Workouts: {sum(len(v) for v in workouts.values())}", ln=True)
    pdf.cell(200, 10, txt=f"Weight: {user_info['weight']} kg", ln=True)
    pdf.output(filename)

    response = app.response_class(
        response=open(filename, "rb").read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
