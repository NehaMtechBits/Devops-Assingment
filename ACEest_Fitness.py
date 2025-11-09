from flask import Flask, request, redirect, url_for
from datetime import datetime

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. This is your in-memory database, just like in the tkinter app.
# It's a global variable for simplicity.
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# 3. This is the main page (homepage)
@app.route('/')
def index():
    """Renders the main page with a form to add workouts."""
    # This HTML is the web-based version of your tkinter GUI
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ACEest Fitness & Gym Tracker</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
            h1, h2 { color: #333; }
            .container { max-width: 500px; margin: auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            form { display: grid; gap: 10px; }
            label { font-weight: bold; }
            input[type='text'], input[type='number'], select { width: 100%; padding: 8px; box-sizing: border-box; }
            button { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            .summary-link { display: inline-block; margin-top: 20px; background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
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
            
            <a href="/summary" class="summary-link">View Summary</a>
        </div>
    </body>
    </html>
    """
    return html_content

# 4. This route handles adding the workout (like your add_workout function)
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
    
    # After adding, send the user back to the homepage
    return redirect(url_for('index'))

# 5. This route shows the summary (like your view_summary function)
@app.route('/summary')
def view_summary():
    """Displays a summary of all logged workouts."""
    if not any(workouts.values()):
        return "<h2>No sessions logged yet!</h2><a href='/'>Go Back</a>"

    # Build an HTML response string
    total_time = 0
    summary_html = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; } h2 { color: #007bff; }
        .category { margin-bottom: 15px; }
        .session { margin-left: 20px; }
        .total { margin-top: 20px; font-size: 1.2em; color: #28a745; }
        .motivation { font-style: italic; color: #555; }
    </style>
    <h1>Workout Summary</h1>
    """
    
    for category, sessions in workouts.items():
        summary_html += f"<div class='category'><h2>{category}:</h2>"
        if sessions:
            for entry in sessions:
                summary_html += f"<div class='session'>{entry['exercise']} - {entry['duration']} min</div>"
                total_time += entry['duration']
        else:
            summary_html += "<div class='session'>No sessions recorded.</div>"
        summary_html += "</div>"

    summary_html += f"<div class='total'>Total Time Spent: {total_time} minutes</div>"

    # Motivational Note
    if total_time < 30:
        msg = "Good start! Keep moving 💪"
    elif total_time < 60:
        msg = "Nice effort! You're building consistency 🔥"
    else:
        msg = "Excellent dedication! Keep up the great work 🏆"
        
    summary_html += f"<div class='motivation'>{msg}</div><br><a href='/'>Go Back</a>"
    return summary_html

# 6. This makes the app runnable
if __name__ == "__main__":
    # The host='0.0.0.0' is CRUCIAL for Docker.
    # It tells the app to be accessible from outside the container.
    app.run(host='0.0.0.0', port=5000, debug=True)