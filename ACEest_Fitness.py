from flask import Flask, request, redirect, url_for
from datetime import datetime
import io
import base64
from matplotlib.figure import Figure

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. In-memory database
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# 3. --- Helper Function for Navigation ---
def get_navbar():
    """Generates the HTML for the navigation bar."""
    return """
    <nav class="navbar">
        <a href="/">🏋️ Log Workouts</a>
        <a href="/summary">📋 View Summary</a>
        <a href="/workout-chart">💡 Workout Plan</a>
        <a href="/diet-chart">🥗 Diet Guide</a>
        <a href="/progress">📈 Progress Tracker</a>
    </nav>
    """

# 4. --- Page Styles (v1.2.2 Update) ---
def get_styles():
    """Returns the CSS styles for the application."""
    return """
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            background-color: #f0f0f0; /* Light gray background */
        }
        h1, h2, h3 { 
            color: #343a40; 
        }
        .container { 
            max-width: 800px; 
            margin: 20px auto; 
            padding: 20px; 
            background-color: #ffffff; /* White containers */
            border-radius: 8px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }
        .navbar {
            width: 100%;
            background-color: #343a40;
            overflow: auto;
            margin-bottom: 20px;
        }
        .navbar a {
            float: left;
            padding: 14px 16px;
            color: white;
            text-decoration: none;
            font-size: 17px;
        }
        .navbar a:hover {
            background-color: #007bff;
        }
        
        /* Form Styles */
        form { display: grid; gap: 15px; }
        label { font-weight: bold; }
        input[type='text'], input[type='number'], select { 
            width: 100%; 
            padding: 10px; 
            box-sizing: border-box; 
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button { 
            background-color: #28a745; 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        button:hover { background-color: #218838; }
        
        /* Summary Page Styles */
        .summary-text { background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .summary-text h2 { margin-top: 15px; margin-bottom: 5px; }
        .summary-text p { margin: 2px 0 2px 20px; }
        .cat-warm-up { color: #007bff; }
        .cat-workout { color: #28a745; }
        .cat-cool-down { color: #ffc107; }
        .cat-total { color: #dc3545; }
        .italic { font-style: italic; color: #888; }
        
    </style>
    """

# 5. --- LOG TAB (Homepage) ---
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
        <div class="container">
            <h1 style="text-align: center;">🏋️ ACEest Fitness & Gym Tracker</h1>
            <form action="/add" method="POST">
                <h2>Add a Session</h2>
                <label for="category">Category:</label>
                <select id="category" name="category">
                    <option value="Warm-up">Warm-up</option>
                    <option value="Workout" selected>Workout</option>
                    <option value="Cool-down">Cool-down</option>
                </select>
                
                <label for="exercise">Exercise:</label>
                <input type="text" id="exercise" name="exercise" required>
                
                <label for="duration">Duration (min):</label>
                <input type="number" id="duration" name="duration" required>
                
                <button type="submit">✅ Add Session</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html_content

# 6. --- ADD FUNCTION (v1.2.2 Update) ---
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

# 7. --- SUMMARY PAGE (v1.2.2 Update) ---
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
            <h1>📊 Weekly Session Summary</h1>
            <div class="summary-text">
    """
    
    total_time = 0
    if not any(workouts.values()):
        html += "<p class='italic'>No sessions logged yet!</p>"
    else:
        for category, sessions in workouts.items():
            cat_class = "cat-" + category.lower().replace(" ", "-")
            html += f"<h2 class='{cat_class}'>--- {category.upper()} ---</h2>"
            if sessions:
                for i, entry in enumerate(sessions, 1):
                    log_date = entry['timestamp'].split(' ')[0]
                    html += f"<p>{i}. {entry['exercise']} - {entry['duration']} min | Logged: {log_date}</p>"
                    total_time += entry['duration']
            else:
                html += "<p class='italic'>&nbsp; No sessions recorded.</p>"
            html += "<br>"

        html += "<h2 class='cat-total'>--- TOTAL TIME SPENT ---</h2>"
        html += f"<p class='cat-total' style='font-weight: bold;'>&nbsp; Total Time: {total_time} minutes</p>"

    html += "</div></div></body></html>"
    return html

# 8. --- WORKOUT PLAN TAB (v1.2.2 Update) ---
@app.route('/workout-chart')
def workout_chart():
    """Displays the static workout plan."""
    chart_data = {
        "🔥 Warm-up (5-10 min)": ["5 min light cardio (Jog/Cycle)", "Jumping Jacks (30 reps)", "Arm Circles (15 Fwd/Bwd)"],
        "💪 Strength Workout (45-60 min)": ["Push-ups (3 sets of 10-15)", "Squats (3 sets of 15-20)", "Plank (3 sets of 60 seconds)", "Lunges (3 sets of 10/leg)"],
        "🧘 Cool-down (5 min)": ["Slow Walking", "Static Stretching (Hold 30s each)", "Deep Breathing Exercises"]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Workout Plan</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>💡 Personalized Workout Plan</h1>
    """
    
    for category, exercises in chart_data.items():
        html += f"<h3 style='color: #007bff;'>{category}</h3><ul>"
        for ex in exercises:
            html += f"<li>{ex}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 9. --- DIET GUIDE TAB (v1.2.2 Update) ---
@app.route('/diet-chart')
def diet_chart():
    """Displays the static diet guide."""
    diet_plans = {
        "🎯 Weight Loss": ["Breakfast: Oatmeal with Berries", "Lunch: Grilled Chicken/Tofu Salad", "Dinner: Vegetable Soup with Lentils"],
        "💪 Muscle Gain": ["Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast", "Lunch: Chicken Breast, Quinoa, and Steamed Veggies", "Post-Workout: Protein Shake, Greek Yogurt"],
        "🏃 Endurance Focus": ["Pre-Workout: Banana & Peanut Butter", "Lunch: Whole Grain Pasta with Light Sauce", "Dinner: Salmon & Avocado Salad"]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Diet Guide</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>🥗 Best Diet Guide for Fitness Goals</h1>
    """
    
    for goal, foods in diet_plans.items():
        html += f"<h3 style='color: #28a745;'>{goal} Plan:</h3><ul>"
        for food in foods:
            html += f"<li>{food}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 10. --- PROGRESS TRACKER TAB (v1.2.2 Update) ---
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
    """
    
    # --- Check for "No Data" ---
    if total_minutes == 0:
        html += "<p class='italic' style='padding: 50px; font-size: 1.2em;'>No workout data logged yet. Log a session to see your progress!</p>"
    else:
        # --- Generate Matplotlib Figure ---
        fig = Figure(figsize=(7.5, 4.5), dpi=100, facecolor='white')
        colors = ["#007bff", "#28a745", "#ffc107"]

        # Bar Chart
        ax1 = fig.add_subplot(121)
        ax1.bar(categories, values, color=colors)
        ax1.set_title("Time Spent per Category (Min)", fontsize=10)
        ax1.set_ylabel("Total Minutes", fontsize=8)
        ax1.grid(axis='y', linestyle='--', alpha=0.7)

        # Pie Chart
        ax2 = fig.add_subplot(122)
        pie_labels = [c for c, v in zip(categories, values) if v > 0]
        pie_values = [v for v in values if v > 0]
        pie_colors = [colors[i] for i, v in enumerate(values) if v > 0]
        ax2.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90, colors=pie_colors,
                wedgeprops={"edgecolor": "black", 'linewidth': 0.5}, textprops={'fontsize': 8})
        ax2.set_title("Workout Distribution", fontsize=10)
        ax2.axis('equal')
        
        fig.tight_layout(pad=2.0)

        # --- Convert plot to image string ---
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        img_data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html += f"<img src='data:image/png;base64,{img_data}'/>"
        
        # --- Add Summary Text ---
        html += f"<h3 style='color: #dc3545; margin-top: 20px;'>Total Training Time Logged: {total_minutes} minutes</h3>"

    # --- Finish HTML Page ---
    html += "</div></body></html>"
    return html

# 11. --- RUN THE APP ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)