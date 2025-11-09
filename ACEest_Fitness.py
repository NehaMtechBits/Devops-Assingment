from flask import Flask, request, redirect, url_for
from datetime import datetime

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. This is your in-memory database
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# 3. --- Helper Function for Navigation ---
# This creates the "tabs" (navigation bar) on every page
def get_navbar():
    return """
    <nav style="background-color: #eee; padding: 10px; margin-bottom: 20px;">
        <a href="/" style="padding: 10px;">🏋️ Log Workouts</a> |
        <a href="/summary" style="padding: 10px;">📋 View Summary</a> |
        <a href="/workout-chart" style="padding: 10px;">📊 Workout Chart</a> |
        <a href="/diet-chart" style="padding: 10px;">🥗 Diet Chart</a>
    </nav>
    """

# 4. --- Page Styles ---
def get_styles():
    return """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        h1, h2, h3 { color: #333; }
        .container { max-width: 600px; margin: auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        form { display: grid; gap: 10px; }
        label { font-weight: bold; }
        input[type='text'], input[type='number'], select { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        a { color: #007bff; text-decoration: none; }
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
            <h1>🏋️ ACEest Fitness & Gym Tracker</h1>
            <h2>Add a Session</h2>
            
            <form action="/add" method="POST">
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
                
                <button type="submit">Add Session</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html_content

# 6. --- ADD FUNCTION (No change) ---
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
    except ValueError:
        return "Input Error: Duration must be a number.", 400

    entry = {
        "exercise": workout,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)
    
    return redirect(url_for('index'))

# 7. --- SUMMARY PAGE (Added Nav) ---
@app.route('/summary')
def view_summary():
    """Displays a summary of all logged workouts."""
    summary_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Workout Summary</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>📋 Workout Summary</h1>
    """

    if not any(workouts.values()):
        summary_html += "<h2>No sessions logged yet!</h2>"
    else:
        total_time = 0
        for category, sessions in workouts.items():
            summary_html += f"<h2 style='color: #007bff;'>{category}:</h2>"
            if sessions:
                for entry in sessions:
                    summary_html += f"<div style='margin-left: 20px;'>{entry['exercise']} - {entry['duration']} min</div>"
                    total_time += entry['duration']
            else:
                summary_html += "<div style='margin-left: 20px; font-style: italic;'>No sessions recorded.</div>"
        
        summary_html += f"<h3 style='color: #28a745; margin-top: 20px;'>Total Time Spent: {total_time} minutes</h3>"

        # Motivational Note
        if total_time < 30:
            msg = "Good start! Keep moving 💪"
        elif total_time < 60:
            msg = "Nice effort! You're building consistency 🔥"
        else:
            msg = "Excellent dedication! Keep up the great work 🏆"
        summary_html += f"<p style='font-style: italic; color: #555;'>{msg}</p>"

    summary_html += "</div></body></html>"
    return summary_html

# 8. --- NEW: WORKOUT CHART TAB ---
@app.route('/workout-chart')
def workout_chart():
    """Displays the static workout chart."""
    chart_data = {
        "Warm-up": ["5 min Jog", "Jumping Jacks", "Arm Circles", "Leg Swings", "Dynamic Stretching"],
        "Workout": ["Push-ups", "Squats", "Plank", "Lunges", "Burpees", "Crunches"],
        "Cool-down": ["Slow Walking", "Static Stretching", "Deep Breathing", "Yoga Poses"]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Workout Chart</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>🏋️ Personalized Workout Chart</h1>
    """
    
    for category, exercises in chart_data.items():
        html += f"<h3 style='color: #007bff;'>{category} Exercises:</h3><ul>"
        for ex in exercises:
            html += f"<li>{ex}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 9. --- NEW: DIET CHART TAB ---
@app.route('/diet-chart')
def diet_chart():
    """Displays the static diet chart."""
    diet_plans = {
        "Weight Loss": ["Oatmeal with Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Stir-fry Veggies"],
        "Muscle Gain": ["Egg Omelet", "Chicken Breast", "Quinoa & Beans", "Protein Shake", "Greek Yogurt with Nuts"],
        "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado", "Trail Mix"]
    }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Diet Chart</title>{get_styles()}</head>
    <body>
        {get_navbar()}
        <div class="container">
            <h1>🥗 Best Diet Chart for Fitness Goals</h1>
    """
    
    for goal, foods in diet_plans.items():
        html += f"<h3 style='color: #28a745;'>{goal} Plan:</h3><ul>"
        for food in foods:
            html += f"<li>{food}</li>"
        html += "</ul>"
        
    html += "</div></body></html>"
    return html

# 10. --- RUN THE APP ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)