import pytest
import requests
from conftest import base_url, get_headers, auth_token
from testdata.test_data import restaurants_endpoint


class TestRestaurant:

    @pytest.mark.parametrize("name", ["Restaurant 1", "Restaurant 2"])
    def test_create_restaurant(self, name, create_restaurant):
        response = create_restaurant(name)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_update_restaurant(self, base_url, auth_token, create_restaurant):
        name = "Updated Restaurant"
        restaurant = create_restaurant("Restaurant")
        restaurant_id = restaurant.json()["id"]

        endpoint = f"{restaurants_endpoint}{restaurant_id}/"
        url = f"{base_url}{endpoint}"
        headers = get_headers(auth_token)
        data = {"name": name}

        response = requests.put(url, headers=headers, json=data)
        assert response.status_code == 200
        assert name == response.json()["name"]

    def test_delete_restaurant(self, base_url, auth_token, create_restaurant):
        restaurant = create_restaurant("Restaurant")
        restaurant_id = restaurant.json()["id"]

        endpoint = f"{restaurants_endpoint}{restaurant_id}/"
        url = f"{base_url}{endpoint}"
        headers = get_headers(auth_token)

        response = requests.delete(url, headers=headers)
        assert response.status_code == 204

    def test_get_restaurants(self, base_url, auth_token, create_restaurant):
        url = f"{base_url}{restaurants_endpoint}"
        headers = get_headers(auth_token)

        response = requests.get(url, headers=headers)
        assert response.status_code == 200

        restaurants = response.json()
        assert isinstance(restaurants, list)
