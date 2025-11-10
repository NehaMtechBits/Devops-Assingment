import pytest
from ACEest_Fitness import app, user_info, workouts

# Set up a test client for the app
@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # This configures the app for testing
    app.config['TESTING'] = True
    
    # We must reset the in-memory "database" before each test
    # so that tests don't interfere with each other.
    global user_info, workouts
    user_info.clear()
    workouts.clear()
    workouts.update({"Warm-up": [], "Workout": [], "Cool-down": []})

    with app.test_client() as client:
        yield client

# --- Test Page Accessibility (GET requests) ---

def test_homepage_loads(client):
    """Test that the homepage (Log Workout) loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"ACEest Session Logger" in response.data

def test_user_info_page_loads(client):
    """Test that the User Profile page loads."""
    response = client.get('/user_info')
    assert response.status_code == 200
    assert b"User Info" in response.data

def test_summary_page_loads(client):
    """Test that the Summary page loads and shows 'No sessions' message."""
    response = client.get('/summary')
    assert response.status_code == 200
    assert b"No sessions logged yet!" in response.data

def test_progress_page_loads(client):
    """Test that the Progress page loads and shows 'No workout data' message."""
    response = client.get('/progress')
    assert response.status_code == 200
    assert b"No workout data logged yet." in response.data

def test_stub_pages_load(client):
    """Test that the placeholder pages (Diet/Workout Plan) load."""
    response = client.get('/workout-chart')
    assert response.status_code == 200
    assert b"Workout Plan coming soon" in response.data
    
    response = client.get('/diet-chart')
    assert response.status_code == 200
    assert b"Diet Guide coming soon" in response.data

# --- Test Functionality (POST requests) ---

def test_save_user_info(client):
    """Test that submitting the user info form works and calculates BMI/BMR."""
    # Simulate posting form data
    response = client.post('/save_user_info', data={
        "name": "Test User",
        "regn_id": "12345",
        "age": "30",
        "gender": "M",
        "height": "180",
        "weight": "75"
    }, follow_redirects=True) # follow_redirects=True follows the redirect
    
    assert response.status_code == 200
    # Check that the page now shows the calculated BMI
    assert b"Your BMI: 23.1" in response.data
    assert b"Your BMR: 1730" in response.data
    # Check that the global variable was updated
    assert user_info["name"] == "Test User"

def test_add_workout_without_user_info(client):
    """Test adding a workout. Calories should be calculated with default weight."""
    response = client.post('/add', data={
        "category": "Workout",
        "exercise": "Push-ups",
        "duration": "10"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check that the workout was added to the in-memory 'database'
    assert len(workouts["Workout"]) == 1
    assert workouts["Workout"][0]["exercise"] == "Push-ups"
    # 70kg (default) * 6.0 MET * 3.5 / 200 * 10 min = 73.5 calories
    assert workouts["Workout"][0]["calories"] == 73.5

def test_pdf_export_fails_without_user_info(client):
    """Test that exporting a PDF fails if user info isn't set."""
    response = client.get('/export_pdf')
    assert response.status_code == 400 # 400 Bad Request
    assert b"Error: Please save user info" in response.data

# --- Test Full Workflow ---

def test_full_workflow(client):
    """Test the full user workflow: set info, add workout, view summary, export."""
    
    # 1. Save User Info
    client.post('/save_user_info', data={
        "name": "Full Workflow User",
        "regn_id": "999",
        "age": "25",
        "gender": "F",
        "height": "165",
        "weight": "60"
    })
    
    # Check that user info is set
    assert user_info["weight"] == 60

    # 2. Add a Workout
    client.post('/add', data={
        "category": "Warm-up",
        "exercise": "Jumping Jacks",
        "duration": "5"
    })
    
    # Check that workout was added
    assert len(workouts["Warm-up"]) == 1
    # Check calorie calculation with new weight
    # 60kg * 3.0 MET * 3.5 / 200 * 5 min = 15.75 calories
    assert workouts["Warm-up"][0]["calories"] == 15.75

    # 3. View Summary Page
    response = client.get('/summary')
    assert response.status_code == 200
    assert b"No sessions logged yet!" not in response.data
    assert b"Jumping Jacks - 5 min | 15.8 kcal" in response.data # check for workout data

    # 4. View Progress Page
    response = client.get('/progress')
    assert response.status_code == 200
    assert b"No workout data logged yet." not in response.data
    assert b"LIFETIME TOTAL: 5 minutes" in response.data # check for chart summary

    # 5. Export PDF
    response = client.get('/export_pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert "Full_Workflow_User_weekly_report.pdf" in response.headers["Content-Disposition"]