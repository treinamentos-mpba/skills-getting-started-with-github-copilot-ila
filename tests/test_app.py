from src.app import activities

ACTIVITY = "Chess Club"
NEW_EMAIL = "newstudent@mergington.edu"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_with_expected_fields(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert ACTIVITY in data
    for details in data.values():
        assert {"description", "schedule", "max_participants", "participants"} <= details.keys()


def test_signup_success(client):
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    assert response.status_code == 200
    assert NEW_EMAIL in activities[ACTIVITY]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown/signup", params={"email": NEW_EMAIL})

    assert response.status_code == 404


def test_signup_duplicate_returns_400(client):
    existing = activities[ACTIVITY]["participants"][0]

    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": existing})

    assert response.status_code == 400
    assert activities[ACTIVITY]["participants"].count(existing) == 1


def test_signup_full_activity_returns_400(client):
    activity = activities[ACTIVITY]
    while len(activity["participants"]) < activity["max_participants"]:
        activity["participants"].append(f"filler{len(activity['participants'])}@mergington.edu")

    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    assert response.status_code == 400
    assert NEW_EMAIL not in activity["participants"]


def test_unregister_success(client):
    existing = activities[ACTIVITY]["participants"][0]

    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": existing})

    assert response.status_code == 200
    assert existing not in activities[ACTIVITY]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete("/activities/Unknown/participants", params={"email": NEW_EMAIL})

    assert response.status_code == 404


def test_unregister_unknown_participant_returns_404(client):
    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": NEW_EMAIL})

    assert response.status_code == 404


def test_signup_and_unregister_are_reflected_in_activities(client):
    client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})
    assert NEW_EMAIL in client.get("/activities").json()[ACTIVITY]["participants"]

    client.delete(f"/activities/{ACTIVITY}/participants", params={"email": NEW_EMAIL})
    assert NEW_EMAIL not in client.get("/activities").json()[ACTIVITY]["participants"]
