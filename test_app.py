import pytest
from ACEest_Fitness import app, user_info, workouts


# --- FIXTURE: Create test client and reset globals ---
@pytest.fixture
def client():
    """Provide a fresh Flask test client for each test."""
    app.config["TESTING"] = True

    # Reset global state before each test
    user_info.clear()
    workouts.clear()
    workouts.update({"Warm-up": [], "Workout": [], "Cool-down": []})

    with app.test_client() as client:
        yield client


def test_full_workflow(client):
    """End-to-end test: save info → add workout → summary → progress → export."""

    # 1️⃣ Save user info
    client.post(
        "/save_user_info",
        data={
            "name": "Full Workflow User",
            "regn_id": "999",
            "age": "25",
            "gender": "F",
            "height": "165",
            "weight": "60",
        },
    )
    assert "weight" in user_info, "User info not saved correctly"
    assert user_info["weight"] == 60

    # 2️⃣ Add workout
    response = client.post(
        "/add",
        data={"category": "Warm-up", "exercise": "Jumping Jacks", "duration": "5"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Validate data stored
    assert "Warm-up" in workouts
    assert len(workouts["Warm-up"]) == 1
    entry = workouts["Warm-up"][0]
    assert entry["exercise"] == "Jumping Jacks"
    assert round(entry["calories"], 2) == 15.75  # MET=3.0, 5 min for 60kg user

    # 3️⃣ Check summary page
    response = client.get("/summary")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Jumping Jacks - 5 min" in html
    assert "15.8 kcal" in html  # rounded display

    # 4️⃣ Check progress page
    response = client.get("/progress")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "No workout data logged yet." not in html
    assert "LIFETIME TOTAL: 5 minutes" in html

    # 5️⃣ Export PDF
    response = client.get("/export_pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "Full_Workflow_User_weekly_report.pdf" in response.headers.get("Content-Disposition", "")
