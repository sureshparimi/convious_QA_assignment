import requests
from datetime import date
from conftest import get_headers, get_new_user
from testdata.test_data import *


def vote_with_new_user(base_url, restaurant_id):
    token = get_new_user(base_url)
    headers = get_headers(token)
    data = {"restaurant_id": restaurant_id}
    url = base_url + polls_vote_endpoint
    return requests.post(url, headers=headers, json=data)


class TestPoll:

    def test_get_today_poll(self, base_url, auth_token):
        url = base_url + polls_today_endpoint
        headers = get_headers(auth_token)

        response = requests.get(url, headers=headers)
        assert response.status_code == 200

        poll_data = response.json()
        assert "top" in poll_data
        assert "rankings" in poll_data
        assert "available_votes" in poll_data

    def test_vote_for_restaurant(self, base_url, create_restaurant):
        token = get_new_user(base_url)
        restaurant = create_restaurant("Restaurant")
        restaurant_id = restaurant.json()["id"]

        url = base_url + polls_vote_endpoint
        headers = get_headers(token)
        data = {"restaurant_id": restaurant_id}

        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 201

        poll_data = response.json()
        assert "top" in poll_data
        assert "rankings" in poll_data
        assert "available_votes" in poll_data

    def test_get_voting_history(self, base_url, auth_token):
        params = history_params
        url = base_url + polls_history_endpoint
        headers = get_headers(auth_token)

        response = requests.get(url, headers=headers, params=params)
        assert response.status_code == 200

        voting_history = response.json()
        assert isinstance(voting_history, list)

    def test_reset_votes(self, base_url, auth_token):
        url = base_url + polls_reset_endpoint
        headers = get_headers(auth_token)
        # today = date.today()
        data = {"date": f"{vote_rest_date}"}

        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

        reset_response = response.json()
        assert "ok" in reset_response
        assert reset_response["ok"] is True

    def test_user_gets_limited_votes_daily(self, base_url, auth_token, create_restaurant):
        votes_available = 5
        token = get_new_user(base_url)
        restaurant = create_restaurant("Restaurant")
        restaurant_id = restaurant.json()["id"]

        url = base_url + polls_vote_endpoint
        headers = get_headers(token)
        data = {"restaurant_id": restaurant_id}
        for _ in range(votes_available):
            response = requests.post(url, headers=headers, json=data)
            assert response.status_code == 201
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 400

    def test_voting_scores(self, base_url, auth_token, create_restaurant):
        token = get_new_user(base_url)
        restaurant = create_restaurant("Restaurant")
        restaurant_id = restaurant.json()["id"]

        endpoint = polls_vote_endpoint
        url = base_url + endpoint
        headers = get_headers(token)
        data = {"restaurant_id": restaurant_id}

        response = requests.post(url, headers=headers, json=data)  # voting first time, should score 4
        assert response.status_code == 201
        assert 4 == next((item['score'] for item in response.json()['rankings'] if item['id'] == restaurant_id), None)

        response = requests.post(url, headers=headers, json=data)  # voting second time, should score 2
        assert response.status_code == 201
        assert 6 == next((item['score'] for item in response.json()['rankings'] if item['id'] == restaurant_id), None)

        response = requests.post(url, headers=headers, json=data)  # voting third time, should score 1
        assert response.status_code == 201
        assert 7 == next((item['score'] for item in response.json()['rankings'] if item['id'] == restaurant_id), None)

    def test_restaurant_with_more_voters_win(self, base_url, auth_token, create_restaurant):
        # reset the polls
        url = base_url + polls_reset_endpoint
        headers = get_headers(auth_token)
        data = {"date": f"{date.today()}"}
        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 200

        restaurant = create_restaurant("Restaurant")
        restaurant_id_1 = restaurant.json()["id"]

        token = get_new_user(base_url)
        url = base_url + polls_vote_endpoint
        headers = get_headers(token)
        data = {"restaurant_id": restaurant_id_1}

        # vote for 4 times by same user results score 8
        for _ in range(4):
            response = requests.post(url, headers=headers, json=data)
            assert response.status_code == 201

        restaurant = create_restaurant("Restaurant")
        restaurant_id_2 = restaurant.json()["id"]

        # vote for 1 time by 2 users results score 8
        response = vote_with_new_user(base_url, restaurant_id_2)
        assert response.status_code == 201

        response = vote_with_new_user(base_url, restaurant_id_2)
        assert response.status_code == 201

        # now restaurant 2 should top as there are 2 voters
        url = base_url + polls_today_endpoint
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        assert response.json()['top']['id'] == restaurant_id_2
