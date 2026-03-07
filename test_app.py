"""
ACEest Fitness & Gym - Pytest Unit Test Suite
Tests all Flask API endpoints for correctness and edge cases.
"""

import pytest
import json
from app import app, members, PROGRAMS


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Create a Flask test client with a clean state for each test."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        members.clear()  # Reset in-memory store before each test
        yield c


@pytest.fixture
def sample_member():
    return {
        "name": "Arjun Kumar",
        "age": 28,
        "weight_kg": 75.0,
        "program": "FL",
        "adherence_percent": 85
    }


# ─── Home & Health ────────────────────────────────────────────────────────────

class TestHomeAndHealth:

    def test_home_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_home_returns_json(self, client):
        res = client.get("/")
        data = res.get_json()
        assert data["app"] == "ACEest Fitness & Gym"
        assert "endpoints" in data

    def test_health_check_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_check_status_healthy(self, client):
        res = client.get("/health")
        data = res.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "aceest-fitness-api"


# ─── Programs ─────────────────────────────────────────────────────────────────

class TestPrograms:

    def test_get_all_programs_returns_200(self, client):
        res = client.get("/programs")
        assert res.status_code == 200

    def test_get_all_programs_returns_three(self, client):
        res = client.get("/programs")
        data = res.get_json()
        assert data["total"] == 3
        assert len(data["programs"]) == 3

    def test_get_all_programs_has_expected_names(self, client):
        res = client.get("/programs")
        data = res.get_json()
        names = [p["name"] for p in data["programs"]]
        assert "Fat Loss (FL)" in names
        assert "Muscle Gain (MG)" in names
        assert "Beginner (BG)" in names

    def test_get_program_by_full_name(self, client):
        res = client.get("/programs/Fat Loss (FL)")
        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == "Fat Loss (FL)"
        assert data["code"] == "FL"

    def test_get_program_by_short_code_fl(self, client):
        res = client.get("/programs/FL")
        assert res.status_code == 200
        data = res.get_json()
        assert data["code"] == "FL"

    def test_get_program_by_short_code_mg(self, client):
        res = client.get("/programs/MG")
        assert res.status_code == 200
        data = res.get_json()
        assert data["code"] == "MG"

    def test_get_program_by_short_code_bg(self, client):
        res = client.get("/programs/BG")
        assert res.status_code == 200
        data = res.get_json()
        assert data["code"] == "BG"

    def test_get_program_has_workout_plan(self, client):
        res = client.get("/programs/MG")
        data = res.get_json()
        assert "workout_plan" in data
        assert isinstance(data["workout_plan"], list)
        assert len(data["workout_plan"]) > 0

    def test_get_program_has_nutrition_plan(self, client):
        res = client.get("/programs/FL")
        data = res.get_json()
        assert "nutrition_plan" in data
        assert "target_kcal" in data["nutrition_plan"]

    def test_get_program_invalid_returns_404(self, client):
        res = client.get("/programs/INVALID")
        assert res.status_code == 404

    def test_get_program_case_insensitive(self, client):
        res = client.get("/programs/fl")
        assert res.status_code == 200

    def test_program_calorie_factors_are_positive(self, client):
        for code in ["FL", "MG", "BG"]:
            res = client.get(f"/programs/{code}")
            data = res.get_json()
            assert data["calorie_factor"] > 0


# ─── Calorie Calculator ───────────────────────────────────────────────────────

class TestCalories:

    def test_calorie_calculation_fl(self, client):
        res = client.get("/calories/FL/70.0")
        assert res.status_code == 200
        data = res.get_json()
        # FL factor = 22, so 70 * 22 = 1540
        assert data["estimated_daily_calories"] == 70 * 22

    def test_calorie_calculation_mg(self, client):
        res = client.get("/calories/MG/80.0")
        assert res.status_code == 200
        data = res.get_json()
        # MG factor = 35, so 80 * 35 = 2800
        assert data["estimated_daily_calories"] == 80 * 35

    def test_calorie_calculation_bg(self, client):
        res = client.get("/calories/BG/65.0")
        assert res.status_code == 200
        data = res.get_json()
        # BG factor = 26, so 65 * 26 = 1690
        assert data["estimated_daily_calories"] == 65 * 26

    def test_calorie_response_includes_weight(self, client):
        res = client.get("/calories/FL/75.0")
        data = res.get_json()
        assert data["weight_kg"] == 75.0

    def test_calorie_invalid_program_returns_404(self, client):
        res = client.get("/calories/UNKNOWN/70.0")
        assert res.status_code == 404

    def test_calorie_zero_weight_returns_400(self, client):
        res = client.get("/calories/FL/0.0")
        assert res.status_code == 400

    def test_calorie_excessive_weight_returns_400(self, client):
        res = client.get("/calories/FL/999.0")
        assert res.status_code == 400


# ─── Member Registration ──────────────────────────────────────────────────────

class TestMembers:

    def test_add_member_returns_201(self, client, sample_member):
        res = client.post("/members",
                          data=json.dumps(sample_member),
                          content_type="application/json")
        assert res.status_code == 201

    def test_add_member_response_message(self, client, sample_member):
        res = client.post("/members",
                          data=json.dumps(sample_member),
                          content_type="application/json")
        data = res.get_json()
        assert "registered successfully" in data["message"]

    def test_add_member_stores_data(self, client, sample_member):
        client.post("/members",
                    data=json.dumps(sample_member),
                    content_type="application/json")
        res = client.get(f"/members/{sample_member['name']}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == sample_member["name"]
        assert data["age"] == sample_member["age"]
        assert data["weight_kg"] == sample_member["weight_kg"]

    def test_add_duplicate_member_returns_409(self, client, sample_member):
        client.post("/members",
                    data=json.dumps(sample_member),
                    content_type="application/json")
        res = client.post("/members",
                          data=json.dumps(sample_member),
                          content_type="application/json")
        assert res.status_code == 409

    def test_add_member_missing_name_returns_400(self, client):
        res = client.post("/members",
                          data=json.dumps({"age": 25, "weight_kg": 70, "program": "FL"}),
                          content_type="application/json")
        assert res.status_code == 400

    def test_add_member_missing_program_returns_400(self, client):
        res = client.post("/members",
                          data=json.dumps({"name": "Test", "age": 25, "weight_kg": 70}),
                          content_type="application/json")
        assert res.status_code == 400

    def test_add_member_invalid_program_returns_400(self, client):
        res = client.post("/members",
                          data=json.dumps({"name": "Test", "age": 25,
                                           "weight_kg": 70, "program": "INVALID"}),
                          content_type="application/json")
        assert res.status_code == 400

    def test_add_member_no_json_returns_400(self, client):
        res = client.post("/members", data="not json", content_type="text/plain")
        assert res.status_code in [400, 415]

    def test_get_all_members_empty(self, client):
        res = client.get("/members")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total"] == 0
        assert data["members"] == []

    def test_get_all_members_after_adding(self, client, sample_member):
        client.post("/members",
                    data=json.dumps(sample_member),
                    content_type="application/json")
        res = client.get("/members")
        data = res.get_json()
        assert data["total"] == 1

    def test_get_member_not_found_returns_404(self, client):
        res = client.get("/members/NonExistentPerson")
        assert res.status_code == 404

    def test_multiple_members_can_be_added(self, client):
        for i in range(3):
            member = {
                "name": f"Member{i}",
                "age": 25 + i,
                "weight_kg": 70.0 + i,
                "program": "BG"
            }
            res = client.post("/members",
                              data=json.dumps(member),
                              content_type="application/json")
            assert res.status_code == 201
        res = client.get("/members")
        assert res.get_json()["total"] == 3


# ─── Error Handling ───────────────────────────────────────────────────────────

class TestErrorHandling:

    def test_404_returns_json(self, client):
        res = client.get("/nonexistent-route")
        assert res.status_code == 404

    def test_programs_data_integrity(self, client):
        """Ensure all 3 programs have all required fields."""
        for code in ["FL", "MG", "BG"]:
            res = client.get(f"/programs/{code}")
            data = res.get_json()
            assert "name" in data
            assert "code" in data
            assert "workout_plan" in data
            assert "nutrition_plan" in data
            assert "calorie_factor" in data


