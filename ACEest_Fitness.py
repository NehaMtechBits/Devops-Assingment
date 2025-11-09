from flask import Flask, request, redirect, url_for
from datetime import datetime
import io
import base64
from matplotlib.figure import Figure

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. In-memory database
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# 3. --- New v1.2.3 Color Palette ---
COLOR_PRIMARY = "#4CAF50"   # Green
COLOR_SECONDARY = "#2196F3" # Blue
COLOR_BACKGROUND = "#F8F9FA" # Light Gray
COLOR_CARD_BG = "#FFFFFF"    # White
COLOR_TEXT = "#343A40"       # Dark Charcoal
COLOR_WARN = "#DC3545"       # Red
COLOR_YELLOW = "#FFC107"

# 4. --- Helper Function for Navigation ---
def get_navbar():
    """Generates the HTML for the navigation bar."""
    return """
    <nav class="navbar">
        <a href="/">🏋️ Log Workouts</a>
        <a href="/workout-chart">💡 Workout Plan</a>
        <a href="/diet-chart">🥗 Diet Guide</a>
        <a href="/progress">📈 Progress Tracker</a>
    </nav>
    """

# 5. --- Page Styles (v1.2.3 Update) ---
def get_styles():
    """Returns the CSS styles for the application."""
    return f"""
    <style>
        body {{ 
            font-family: "Inter", Arial, sans-serif; 
            margin: 0; 
            background-color: {COLOR_BACKGROUND};
            color: {COLOR_TEXT};
        }}
        h1, h2, h3 {{ 
            color: {COLOR_TEXT}; 
        }}
        .container {{ 
            max-width: 800px; 
            margin: 20px auto; 
            padding: 30px; 
            background-color: {COLOR_CARD_BG}; /* Card style */
            border-radius: 8px; 
            border: 1px solid #E9ECEF; /* Highlight border */
        }}
        .navbar {{
            width: 100%;
            background-color: {COLOR_BACKGROUND};
            border-bottom: 1px solid #E9ECEF;
            overflow: auto;
        }}
        .navbar a {{
            float: left;
            padding: 15px 18px;
            color: {COLOR_TEXT};
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
        }}
        .navbar a:hover {{
            background-color: #ddd;
            color: {COLOR_PRIMARY};
        }}
        
        /* Form Styles */
        form {{ display: grid; gap: 15px; }}
        label {{ font-weight: bold; }}
        input[type='text'], input[type='number'], select {{ 
            width: 100%; 
            padding: 12px; 
            box-sizing: border-box; 
            border: 1px solid #ccc;
            border-radius: 4px;
            font-family: "Inter", Arial, sans-serif;
        }}
        .btn {{
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            text-decoration: none;
            text-align: center;
            display: inline-block;
        }}
        .btn-primary {{
            background-color: {COLOR_PRIMARY};
            color: white;
        }}
        .btn-primary:hover {{ background-color: #388E3C; }}
        
        .btn-secondary {{
            background-color: {COLOR_SECONDARY};
            color: white;
        }}
        .btn-secondary:hover {{ background-color: #1976D2; }}
        
        /* Summary Page */
        .summary-text {{ background-color: {COLOR_BACKGROUND}; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .summary-text h2 {{ margin-top: 15px; margin-bottom: 5px; }}
        .summary-text p {{ margin: 2px 0 2px 20px; }}
        .cat-warm-up {{ color: {COLOR_SECONDARY}; }}
        .cat-workout {{ color: {COLOR_PRIMARY}; }}
        .cat-cool-down {{ color: {COLOR_YELLOW}; }}
        .cat-total {{ color: {COLOR_WARN}; }}
        .italic {{ font-style: italic; color: #888; }}
        
        /* Plan/Guide Pages */
        .plan-list {{ list-style-type: none; padding-left: 0; }}
        .plan-list li {{ margin-bottom: 10px; }}
        
    </style>
    """

# 6. --- LOG TAB (Homepage) (v1.2.3 Update) ---
@app.route('/')
def index():
    """Renders the main page (Log Workout)"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ACEest Fitness - Log Workout</title>
        {get_styles()}
    </head>
    <body>
        {get_navbar()}
        <div style="text-align: center; margin-top: 20px;">
            <h1 style="font-size: 2.5em;">ACEest Session Logger</h1>
            <p style="font-size: 1.2em; color: #6C757D;">Track your progress with precision.</p>
        </div>
        <div class="container">
            <form action="/add" method="POST">
                <h2>Log a New Session</h2>
                <label for="category">Category:</label>
                <select id="category" name="category">
                    <option value="Warm-up">Warm-up</option>
                    <option value="Workout" selected>Workout</option>
                    <option value="Cool-down">Cool-down</option>
                </select>
                
                <label for="exercise">Exercise Name:</label>
                <input type="text" id="exercise" name="exercise" required>
                
                <label for="duration">Duration (min):</label>
                <input type="number" id="duration" name="duration" required>
                
                <button type="submit" class="btn btn-primary">✅ ADD SESSION</button>
            </form>
            <br>
            <a href="/summary" class="btn btn-secondary" style="width: 100%; box-sizing: border-box;">📋 VIEW SUMMARY</a>
        </div>
    </body>
    </html>
    """
    return html_content

# 7. --- ADD FUNCTION (v1.2.3 Update) ---
@app.route('/add', methods=['POST'])
def add_workout():
    """Processes the form data and adds a workout."""
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

    entry = {
        "exercise": workout,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)
    
    return redirect(url_for('index')) # Go back to homepage

# 8. --- SUMMARY PAGE (v1.2.3 Update) ---
@app.route('/summary')
def view_summary():
    """Displays a summary of all logged workouts."""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Workout Summary</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>🏋️ Full Session History</h1>
            <div class="summary-text">
    """
    
    total_time = 0
    if not any(workouts.values()):
        html += "<p class='italic' style='font-size: 1.2em;'>No sessions logged yet! Start tracking your workouts.</p>"
    else:
        for category, sessions in workouts.items():
            cat_class = "cat-" + category.lower().replace(" ", "-")
            html += f"<h2 class='{cat_class}'>--- {category.upper()} ---</h2>"
            if sessions:
                for i, entry in enumerate(sessions, 1):
                    log_date = entry['timestamp'].split(' ')[0]
                    html += f"<p>{i}. {entry['exercise']} - {entry['duration']} min | Date: {log_date}</p>"
                    total_time += entry['duration']
            else:
                html += "<p class='italic'>&nbsp; No sessions recorded.</p>"
            html += "<br>"

        html += f"<h2 class='cat-total'>--- LIFETIME TOTALS ---</h2>"
        html += f"<p class='cat-total' style='font-weight: bold; font-size: 1.1em;'>&nbsp; Total Training Time: {total_time} minutes</p>"

    html += "</div></div></body></html>"
    return html

# 9. --- WORKOUT PLAN TAB (v1.2.3 Update) ---
@app.route('/workout-chart')
def workout_chart():
    """Displays the static workout plan."""
    chart_data = {
        "🔥 Warm-up (5-10 min)": ["5 min light cardio (Jog/Cycle) to raise heart rate.", "Jumping Jacks (30 reps) for dynamic mobility.", "Arm Circles (15 Fwd/Bwd) to prepare shoulders."],
        "💪 Strength & Cardio (45-60 min)": ["Push-ups (3 sets of 10-15) - Upper body strength.", "Squats (3 sets of 15-20) - Lower body foundation.", "Plank (3 sets of 60 seconds) - Core stabilization.", "Lunges (3 sets of 10/leg) - Balance and leg development."],
        "🧘 Cool-down (5 min)": ["Slow Walking - Bring heart rate down gradually.", "Static Stretching (Hold 30s each) - Focus on major muscle groups.", "Deep Breathing Exercises - Aid recovery and relaxation."]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Workout Plan</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>💡 Personalized Workout Plan Guide</h1>
    """
    
    for category, exercises in chart_data.items():
        html += f"<h3 style='color: {COLOR_SECONDARY};'>{category}</h3><ul class='plan-list'>"
        for ex in exercises:
            html += f"<li>• {ex}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 10. --- DIET GUIDE TAB (v1.2.3 Update) ---
@app.route('/diet-chart')
def diet_chart():
    """Displays the static diet guide."""
    diet_plans = {
        "🎯 Weight Loss Focus (Calorie Deficit)": ["Breakfast: Oatmeal with Berries (High Fiber).", "Lunch: Grilled Chicken/Tofu Salad (Lean Protein).", "Dinner: Vegetable Soup with Lentils (Low Calorie, High Volume)."],
        "💪 Muscle Gain Focus (High Protein)": ["Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast (Protein/Carb combo).", "Lunch: Chicken Breast, Quinoa, and Steamed Veggies (Balanced Meal).", "Post-Workout: Protein Shake & Greek Yogurt (Immediate Recovery)."],
        "🏃 Endurance Focus (Complex Carbs)": ["Pre-Workout: Banana & Peanut Butter (Quick Energy).", "Lunch: Whole Grain Pasta with Light Sauce (Sustainable Carbs).", "Dinner: Salmon & Avocado Salad (Omega-3s and Healthy Fats)."]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Diet Guide</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>🥗 Nutritional Goal Setting Guide</h1>
    """
    
    for goal, foods in diet_plans.items():
        html += f"<h3 style='color: {COLOR_PRIMARY};'>{goal}</h3><ul class='plan-list'>"
        for food in foods:
            html += f"<li>• {food}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 11. --- PROGRESS TRACKER TAB (v1.2.3 Update) ---
@app.route('/progress')
def progress():
    """Generates and displays the progress charts."""
    
    totals = {cat: sum(entry['duration'] for entry in sessions) for cat, sessions in workouts.items()}
    categories = list(totals.keys())
    values = list(totals.values())
    total_minutes = sum(values)
    
    # --- Start HTML Page ---
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Progress Tracker</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container" style="text-align: center;">
            <h1>📈 Personal Progress Tracker</h1>
            <p style="font-size: 1.1em; color: #6C757D;">Visualization of your logged workout time distribution.</p>
    """
    
    # --- Check for "No Data" ---
    if total_minutes == 0:
        html += f"<p class='italic' style='padding: 50px; font-size: 1.3em;'>No workout data logged yet. Log a session to see your progress!</p>"
    else:
        # --- Generate Matplotlib Figure (v1.2.3 Styling) ---
        fig = Figure(figsize=(8, 5), dpi=100, facecolor=COLOR_CARD_BG)
        chart_colors = [COLOR_SECONDARY, COLOR_PRIMARY, COLOR_YELLOW]

        # Bar Chart
        ax1 = fig.add_subplot(121)
        ax1.bar(categories, values, color=chart_colors)
        ax1.set_title("Total Minutes per Category", fontsize=10)
        ax1.set_ylabel("Total Minutes", fontsize=8)
        ax1.grid(axis='y', linestyle='-', alpha=0.3)
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.set_facecolor(COLOR_CARD_BG)

        # Pie Chart
        ax2 = fig.add_subplot(122)
        pie_labels = [c for c, v in zip(categories, values) if v > 0]
        pie_values = [v for v in values if v > 0]
        pie_colors = [chart_colors[i] for i, v in enumerate(values) if v > 0]
        ax2.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90, colors=pie_colors,
                wedgeprops={"edgecolor": "white", 'linewidth': 1}, textprops={'fontsize': 8})
        ax2.set_title("Workout Distribution (%)", fontsize=10)
        ax2.axis('equal')
        ax2.set_facecolor(COLOR_CARD_BG)
        
        fig.tight_layout(pad=2.0)

        # --- Convert plot to image string ---
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        img_data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html += f"<img src='data:image/png;base64,{img_data}'/>"
        
        # --- Add Summary Text ---
        html += f"<h3 style='color: {COLOR_WARN}; margin-top: 20px;'>LIFETIME TOTAL: {total_minutes} minutes logged across all categories.</h3>"

    # --- Finish HTML Page ---
    html += "</div></body></html>"
    return html

# 12. --- RUN THE APP ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)