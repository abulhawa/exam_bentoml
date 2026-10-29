import requests

# The URL of the login and prediction endpoints
login_url = "http://127.0.0.1:3001/login"
predict_url = "http://127.0.0.1:3001/predict"


prediction_payload = {
    "input_data": {
        "gre_score": 300,
        "toefl_score": 110,
        "university_rating": 3,
        "sop": 3.5,
        "lor": 2.5,
        "cgpa": 9,
        "research": 1,
    }
}


def test_login_success():
    response = requests.post(
        login_url,
        json={"credentials": {"username": "user123", "password": "password123"}},
    )

    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure():
    response = requests.post(
        login_url,
        json={"credentials": {"username": "user123", "password": "wrong"}},
    )

    assert response.status_code == 401


def test_predict_with_jwt():
    login_response = requests.post(
        login_url,
        json={"credentials": {"username": "user123", "password": "password123"}},
    )
    token = login_response.json().get("token")
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=prediction_payload,
    )

    assert response.status_code == 200

    prediction = response.json()["prediction"]

    assert isinstance(prediction, list)
    assert len(prediction) == 1
    assert isinstance(prediction[0], float)


def test_predict_with_invalid_payload():
    login_response = requests.post(
        login_url,
        json={"credentials": {"username": "user123", "password": "password123"}},
    )

    token = login_response.json().get("token")
    invalid_payload = {
        "input_data": {
            **prediction_payload["input_data"],
            "gre_score": 3000,
        }
    }

    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=invalid_payload,
    )

    assert response.status_code == 400


def test_predict_with_invalid_token():

    invalid_token = "something random"

    # Send a POST request to the prediction
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {invalid_token}",
        },
        json=prediction_payload,
    )

    assert response.status_code == 401


def test_predict_with_missing_token():

    # Send a POST request to the prediction
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
        },
        json=prediction_payload,
    )

    assert response.status_code == 401


def test_expired_token():
    import jwt
    from datetime import datetime, timedelta, UTC

    expired_token = jwt.encode(
        {
            "sub": "user123",
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        "your_jwt_secret_key_here",
        algorithm="HS256",
    )

    # Send a POST request to the prediction
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {expired_token}",
        },
        json=prediction_payload,
    )

    assert response.status_code == 401
