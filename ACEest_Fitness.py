from flask import Flask, request, redirect, url_for, make_response, send_file
from datetime import datetime
import io
import base64
from matplotlib.figure import Figure

# --- PDF Report Imports ---
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors as rl_colors

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. --- Globals (In-memory database) ---
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}
user_info = {} # Holds user data (name, weight, bmi, etc.)

# 3. --- New v1.3 MET Values ---
MET_VALUES = {
    "Warm-up": 3.0,
    "Workout": 6.0,
    "Cool-down": 2.5
}

# 4. --- New v1.3 Color Palette ---
COLOR_PRIMARY = "#4CAF50"   # Green
COLOR_SECONDARY = "#2196F3" # Blue
COLOR_BACKGROUND = "#F8F9FA"
COLOR_CARD_BG = "#FFFFFF"
COLOR_TEXT = "#343A40"
COLOR_WARN = "#DC3545"
COLOR_YELLOW = "#FFC107"

# 5. --- Helper Function for Navigation (v1.3 Update) ---
def get_navbar():
    """Generates the HTML for the navigation bar."""
    return """
    <nav class="navbar">
        <a href="/">🏋️ Log Workouts</a>
        <a href="/user_info">👤 User Profile</a>
        <a href="/workout-chart">💡 Workout Plan</a>
        <a href="/diet-chart">🥗 Diet Guide</a>
        <a href="/progress">📈 Progress Tracker</a>
        <a href="/export_pdf" style="background-color: #007bff; color: white;">📄 Export Report</a>
    </nav>
    """

# 6. --- Page Styles (v1.2.3 Styles) ---
def get_styles():
    """Returns the CSS styles for the application."""
    # This function remains the same as the v1.2.3 conversion
    # (Omitted for brevity, but it's the same CSS as the v1.2.3 answer)
    return f"""
    <style>
        body {{ font-family: "Inter", Arial, sans-serif; margin: 0; background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT}; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 30px; background-color: {COLOR_CARD_BG}; border-radius: 8px; border: 1px solid #E9ECEF; }}
        .navbar {{ width: 100%; background-color: {COLOR_BACKGROUND}; border-bottom: 1px solid #E9ECEF; overflow: auto; }}
        .navbar a {{ float: left; padding: 15px 18px; color: {COLOR_TEXT}; text-decoration: none; font-size: 16px; font-weight: bold; }}
        .navbar a:hover {{ background-color: #ddd; color: {COLOR_PRIMARY}; }}
        form {{ display: grid; gap: 15px; }}
        label {{ font-weight: bold; }}
        input[type='text'], input[type='number'], select {{ width: 100%; padding: 12px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-family: "Inter", Arial, sans-serif; }}
        .btn {{ padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; text-decoration: none; text-align: center; display: inline-block; }}
        .btn-primary {{ background-color: {COLOR_PRIMARY}; color: white; }}
        .btn-primary:hover {{ background-color: #388E3C; }}
        .btn-secondary {{ background-color: {COLOR_SECONDARY}; color: white; }}
        .btn-secondary:hover {{ background-color: #1976D2; }}
        .summary-text {{ background-color: {COLOR_BACKGROUND}; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .summary-text h2 {{ margin-top: 15px; margin-bottom: 5px; }}
        .summary-text p {{ margin: 2px 0 2px 20px; }}
        .cat-warm-up {{ color: {COLOR_SECONDARY}; }}
        .cat-workout {{ color: {COLOR_PRIMARY}; }}
        .cat-cool-down {{ color: {COLOR_YELLOW}; }}
        .cat-total {{ color: {COLOR_WARN}; }}
        .italic {{ font-style: italic; color: #888; }}
        .plan-list {{ list-style-type: none; padding-left: 0; }}
        .plan-list li {{ margin-bottom: 10px; }}
    </style>
    """

# 7. --- LOG TAB (Homepage) ---
@app.route('/')
def index():
    """Renders the main page (Log Workout)"""
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head><meta charset="UTF-8"><title>ACEest - Log Workout</title>{get_styles()}</head>
    <body>{get_navbar()}
        <div style="text-align: center; margin-top: 20px;">
            <h1 style="font-size: 2.5em;">ACEest Session Logger</h1>
            <p style="font-size: 1.2em; color: #6C757D;">Track your progress with precision.</p>
        </div>
        <div class="container">
            <form action="/add" method="POST">
                <h2>Log a New Session</h2>
                <label for="category">Category:</label>
                <select id="category" name="category">
                    <option value="Warm-up">Warm-up</option><option value="Workout" selected>Workout</option><option value="Cool-down">Cool-down</option>
                </select>
                <label for="exercise">Exercise Name:</label><input type="text" id="exercise" name="exercise" required>
                <label for="duration">Duration (min):</label><input type="number" id="duration" name="duration" required>
                <button type="submit" class="btn btn-primary">✅ ADD SESSION</button>
            </form>
            <br><a href="/summary" class="btn btn-secondary" style="width: 100%; box-sizing: border-box;">📋 VIEW SUMMARY</a>
        </div>
    </body></html>
    """
    return html

# 8. --- NEW: USER INFO PAGE ---
@app.route('/user_info', methods=['GET'])
def user_info_page():
    """Displays the user info form."""
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head><meta charset="UTF-8"><title>User Profile</title>{get_styles()}</head>
    <body>{get_navbar()}
        <div class="container">
            <h1>📝 User Info</h1>
            <form action="/save_user_info" method="POST">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" value="{user_info.get('name', '')}" required>
                
                <label for="regn_id">Regn-ID:</label>
                <input type="text" id="regn_id" name="regn_id" value="{user_info.get('regn_id', '')}">
                
                <label for="age">Age:</label>
                <input type="number" id="age" name="age" value="{user_info.get('age', '')}" required>
                
                <label for="gender">Gender (M/F):</label>
                <input type="text" id="gender" name="gender" value="{user_info.get('gender', '')}" required>
                
                <label for="height">Height (cm):</label>
                <input type="number" step="0.1" id="height" name="height" value="{user_info.get('height', '')}" required>
                
                <label for="weight">Weight (kg):</label>
                <input type="number" step="0.1" id="weight" name="weight" value="{user_info.get('weight', '')}" required>
                
                <button type="submit" class="btn btn-primary">Save Info</button>
            </form>
    """
    if 'bmi' in user_info:
        html += f"<h3>Your BMI: {user_info['bmi']:.1f}</h3>"
        html += f"<h3>Your BMR: {user_info['bmr']:.0f} kcal/day</h3>"
    html += "</div></body></html>"
    return html

# 9. --- NEW: SAVE USER INFO LOGIC ---
@app.route('/save_user_info', methods=['POST'])
def save_user_info():
    """Saves user info and calculates BMI/BMR."""
    global user_info # Modify the global variable
    try:
        name = request.form['name'].strip()
        regn_id = request.form['regn_id'].strip()
        age = int(request.form['age'].strip())
        gender = request.form['gender'].strip().upper()
        height_cm = float(request.form['height'].strip())
        weight_kg = float(request.form['weight'].strip())
        
        bmi = weight_kg / ((height_cm / 100) ** 2)
        
        if gender == "M":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
            
        user_info = {
            "name": name, "regn_id": regn_id, "age": age, "gender": gender,
            "height": height_cm, "weight": weight_kg, "bmi": bmi, "bmr": bmr,
            "weekly_cal_goal": 2000
        }
    except Exception as e:
        return f"Error processing form: {e}", 400
    
    return redirect(url_for('user_info_page'))

# 10. --- ADD FUNCTION (v1.3 Update) ---
@app.route('/add', methods=['POST'])
def add_workout():
    """Processes the form data and adds a workout, now with calories."""
    category = request.form['category']
    workout = request.form['exercise'].strip()
    duration_str = request.form['duration'].strip()

    if not workout or not duration_str:
        return "Input Error: Please enter both exercise and duration.", 400

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError("Duration must be positive")
    except ValueError:
        return "Input Error: Duration must be a positive whole number.", 400

    # --- New Calorie Calculation ---
    weight = user_info.get("weight", 70) # Default 70kg if user info not set
    met = MET_VALUES.get(category, 5.0)  # Default 5.0 METs
    calories = (met * 3.5 * weight / 200) * duration

    entry = {
        "exercise": workout,
        "duration": duration,
        "calories": calories, # Add calories
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)
    
    return redirect(url_for('index')) # Go back to homepage

# 11. --- SUMMARY PAGE (v1.3 Update) ---
@app.route('/summary')
def view_summary():
    """Displays a summary of all logged workouts, now with calories."""
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head><title>Workout Summary</title>{get_styles()}</head>
    <body>{get_navbar()}
        <div class="container">
            <h1>🏋️ Full Session History</h1>
            <div class="summary-text">
    """
    
    total_time = 0
    if not any(workouts.values()):
        html += "<p class='italic' style='font-size: 1.2em;'>No sessions logged yet!</p>"
    else:
        for category, sessions in workouts.items():
            cat_class = "cat-" + category.lower().replace(" ", "-")
            html += f"<h2 class='{cat_class}'>--- {category.upper()} ---</h2>"
            if sessions:
                for i, entry in enumerate(sessions, 1):
                    log_date = entry['timestamp'].split(' ')[0]
                    # Add calories to the summary line
                    html += f"<p>{i}. {entry['exercise']} - {entry['duration']} min | {entry['calories']:.1f} kcal | Date: {log_date}</p>"
                    total_time += entry['duration']
            else:
                html += "<p class='italic'>&nbsp; No sessions recorded.</p>"
            html += "<br>"

        html += f"<h2 class='cat-total'>--- LIFETIME TOTALS ---</h2>"
        html += f"<p class='cat-total' style='font-weight: bold; font-size: 1.1em;'>&nbsp; Total Training Time: {total_time} minutes</p>"

    html += "</div></div></body></html>"
    return html

# 12. --- WORKOUT & DIET PLAN STUBS (v1.3) ---
@app.route('/workout-chart')
def workout_chart():
    """Displays placeholder text for workout plan."""
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head><title>Workout Plan</title>{get_styles()}</head>
    <body>{get_navbar()}
        <div class="container">
            <h1>💡 Workout Plan</h1>
            <p>Workout Plan coming soon.</p>
        </div>
    </body></html>
    """
    return html

@app.route('/diet-chart')
def diet_chart():
    """Displays placeholder text for diet guide."""
    html = f"""
    <!DOCTYPE html><html lang="en">
    <head><title>Diet Guide</title>{get_styles()}</head>
    <body>{get_navbar()}
        <div class="container">
            <h1>🥗 Diet Guide</h1>
            <p>Diet Guide coming soon.</p>
        </div>
    </body></html>
    """
    return html

# 13. --- PROGRESS TRACKER (Unchanged from v1.2.3) ---
@app.route('/progress')
def progress():
    # This route remains the same as the v1.2.3 conversion
    # (Omitted for brevity, but it's the same Matplotlib code as the v1.2.3 answer)
    totals = {cat: sum(entry['duration'] for entry in sessions) for cat, sessions in workouts.items()}
    categories = list(totals.keys())
    values = list(totals.values())
    total_minutes = sum(values)
    
    html = f"<!DOCTYPE html><html lang='en'><head><title>Progress Tracker</title>{get_styles()}</head><body>{get_navbar()}<div class='container' style='text-align: center;'><h1>📈 Personal Progress Tracker</h1>"
    
    if total_minutes == 0:
        html += "<p class='italic' style='padding: 50px; font-size: 1.3em;'>No workout data logged yet.</p>"
    else:
        fig = Figure(figsize=(8, 5), dpi=100, facecolor=COLOR_CARD_BG)
        chart_colors = [COLOR_SECONDARY, COLOR_PRIMARY, COLOR_YELLOW]
        ax1 = fig.add_subplot(121); ax1.bar(categories, values, color=chart_colors)
        ax1.set_title("Total Minutes per Category", fontsize=10); ax1.set_ylabel("Total Minutes", fontsize=8)
        ax1.grid(axis='y', linestyle='-', alpha=0.3); ax1.spines['right'].set_visible(False); ax1.spines['top'].set_visible(False); ax1.set_facecolor(COLOR_CARD_BG)
        ax2 = fig.add_subplot(122); pie_labels = [c for c, v in zip(categories, values) if v > 0]; pie_values = [v for v in values if v > 0]; pie_colors = [chart_colors[i] for i, v in enumerate(values) if v > 0]
        ax2.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90, colors=pie_colors, wedgeprops={"edgecolor": "white", 'linewidth': 1}, textprops={'fontsize': 8})
        ax2.set_title("Workout Distribution (%)", fontsize=10); ax2.axis('equal'); ax2.set_facecolor(COLOR_CARD_BG)
        fig.tight_layout(pad=2.0)
        buf = io.BytesIO(); fig.savefig(buf, format="png"); img_data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html += f"<img src='data:image/png;base64,{img_data}'/>"
        html += f"<h3 style='color: {COLOR_WARN}; margin-top: 20px;'>LIFETIME TOTAL: {total_minutes} minutes logged.</h3>"

    html += "</div></body></html>"
    return html

# 14. --- NEW: PDF EXPORT ROUTE ---
@app.route('/export_pdf')
def export_pdf():
    """Generates a PDF report and sends it to the user."""
    if not user_info:
        return "Error: Please save user info before exporting.", 400
        
    filename = f"{user_info['name'].replace(' ','_')}_weekly_report.pdf"
    
    # --- Create PDF in memory ---
    buf = io.BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Weekly Fitness Report - {user_info['name']}")
    
    # User Info
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, f"Regn-ID: {user_info['regn_id']} | Age: {user_info['age']} | Gender: {user_info['gender']}")
    c.drawString(50, height - 100, f"Height: {user_info['height']} cm | Weight: {user_info['weight']} kg | BMI: {user_info['bmi']:.1f} | BMR: {user_info['bmr']:.0f} kcal/day")
    
    # Table of workouts
    y = height - 140
    table_data = [["Category", "Exercise", "Duration (min)", "Calories (kcal)", "Date"]]
    for cat, sessions in workouts.items():
        for e in sessions:
            table_data.append([
                cat, 
                e['exercise'], 
                str(e['duration']), 
                f"{e['calories']:.1f}", 
                e['timestamp'].split()[0]
            ])
            
    table = Table(table_data, colWidths=[80, 150, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.black)
    ]))
    
    # Draw table
    table.wrapOn(c, width - 100, y)
    table_height = table._height
    table.drawOn(c, 50, y - table_height)
    
    # Save PDF
    c.showPage()
    c.save()
    buf.seek(0)
    
    # --- Send file to user ---
    return send_file(buf, as_attachment=True, download_name=filename, mimetype='application/pdf')

# 15. --- RUN THE APP ---
if __name__ == "__main__":
    app.run