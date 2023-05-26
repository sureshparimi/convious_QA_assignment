import os
import uuid

import requests
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def base_url():
    return "https://qa-convious-homework.fly.dev/api/v1"


@pytest.fixture
def auth_token(base_url):
    endpoint = "/auth/token/login"
    url = base_url + endpoint
    headers = {"Content-Type": "application/json"}
    data = {"username": os.getenv("TEST_USERNAME"), "password": os.getenv("TEST_PASSWORD")}

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200
    assert "auth_token" in response.json()

    return response.json()["auth_token"]


# @pytest.fixture(scope="session")
# def get_headers(base_url, auth_token):
#     return {"Content-Type": "application/json", "Authorization": f"Token {auth_token}"}


@pytest.fixture
def create_restaurant(base_url, auth_token):
    endpoint = "/restaurants/"
    url = base_url + endpoint
    headers = {"Content-Type": "application/json", "Authorization": f"Token {auth_token}"}

    def _create_restaurant(name):
        data = {"name": name}

        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 201
        assert "id" in response.json()

        return response

    return _create_restaurant


def get_user_data():
    return {
        "username": f"{uuid.uuid4()}",
        "email": f"{uuid.uuid4()}+test@mailinator.com",
        "password": "iPhone@123"
    }


def get_headers(token):
    return {"Content-Type": "application/json", "Authorization": f"Token {token}"}


def get_new_user(base_url):
    url = f"{base_url}/auth/users/create"
    user_data = get_user_data()
    response = requests.post(url, json=user_data)
    assert response.status_code == 201
    return get_auth_token(base_url, user_data)


def get_auth_token(base_url, user_data):
    endpoint = "/auth/token/login"
    url = base_url + endpoint
    headers = {"Content-Type": "application/json"}
    data = {"username": user_data['username'], "password": user_data['password']}

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200
    assert "auth_token" in response.json()

    return response.json()["auth_token"]
