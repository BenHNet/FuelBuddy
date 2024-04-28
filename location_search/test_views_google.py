from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.urls import reverse

from . import views_google


class MapSubmitTestCase(TestCase):

    def test_map_submit(self):
        factory = RequestFactory()
        url = reverse('submit')

        data = {
            'location': 'New York',
            'range': '5 Miles',
            'gasType': 'Regular',
            'preferenceSelect': 'Some Preference'
        }
        request = factory.post(url, data)

        # Add location value to session
        request.session = {'location': 'New York'}

        with patch.object(views_google, 'geocode', return_value=self.mock_geocode_response()), \
                patch.object(views_google, 'nearby_gas_search', return_value=self.mock_nearby_gas_search_response()), \
                patch('os.environ', {'api_key': 'mock_api_key'}):
            response = views_google.map_submit(request)

        self.assertEqual(response.status_code, 200)  # Assuming successful render

    def mock_geocode_response(self):
        return {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": 40.712776, "lng": -74.005974}
                    }
                }
            ]
        }

    def mock_nearby_gas_search_response(self):
        return {
            "results": [
                {
                    "name": "Gas Station 1",
                    "vicinity": "123 Main St",
                    "geometry": {"location": {"lat": 40.712776, "lng": -74.005974}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                },
                {
                    "name": "Gas Station 2",
                    "vicinity": "456 Elm St",
                    "geometry": {"location": {"lat": 40.712345, "lng": -74.001234}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                }
            ]
        }


class UpdatePriceTestCase(TestCase):

    @patch('location_search.views_google.Gas_Station.objects.get')
    def test_update_price(self, mock_gas_station_get):
        location = '40.712776+-74.005974'
        url = reverse('updatePrice', args=(
        location,))  # https://fuelbuddy.azurewebsites.net/location_search/updatePrice_google/40.5918021+-105.0766215
        data = {
            'regular_gas_price': '3.00',
            'premium_gas_price': '3.50',
            'diesel_price': '3.20'
        }

        # Mocking the Gas_Station object
        mock_gas_station = MagicMock()
        mock_gas_station.regular_gas_price = None
        mock_gas_station.premium_gas_price = None
        mock_gas_station.diesel_price = None
        mock_gas_station.id = 1
        mock_gas_station.station_name = 'Mock Gas Station Name'
        mock_gas_station.address = 'Mock Gas Station Address'
        mock_gas_station.latitude = 40.712776
        mock_gas_station.longitude = -74.005974

        # Mocking Gas_Station.objects.get to return the mocked Gas_Station object
        mock_gas_station_get.return_value = mock_gas_station

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Assuming successful redirect


class GeocodeTestCase(TestCase):

    @patch.object(views_google.requests, 'get')
    def test_geocode(self, mock_requests_get):
        mock_requests_get.return_value.json.return_value = self.mock_geocode_response()
        response = views_google.geocode('New York', 'mock_api_key')
        self.assertEqual(response, self.mock_geocode_response())

    def mock_geocode_response(self):
        return {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": 40.712776, "lng": -74.005974}
                    }
                }
            ]
        }


class NearbyGasSearchTestCase(TestCase):

    @patch.object(views_google.requests, 'get')
    def test_nearby_gas_search(self, mock_requests_get):
        mock_requests_get.return_value.json.return_value = self.mock_nearby_gas_search_response()
        location = {'lat': 40.712776, 'lng': -74.005974}
        response = views_google.nearby_gas_search(location, 5, 'mock_api_key')
        self.assertEqual(response, self.mock_nearby_gas_search_response())

    def mock_nearby_gas_search_response(self):
        return {
            "results": [
                {
                    "name": "Gas Station 1",
                    "vicinity": "123 Main St",
                    "geometry": {"location": {"lat": 40.712776, "lng": -74.005974}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                },
                {
                    "name": "Gas Station 2",
                    "vicinity": "456 Elm St",
                    "geometry": {"location": {"lat": 40.712345, "lng": -74.001234}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                }
            ]
        }


class GetMapDataTestCase(TestCase):

    def test_get_map_data(self):
        factory = RequestFactory()
        url = reverse('searchPage')
        request = factory.get(url)
        request.session = {'location': 'New York'}

        with patch.object(views_google, 'geocode', return_value=self.mock_geocode_response()), \
                patch.object(views_google, 'nearby_gas_search', return_value=self.mock_nearby_gas_search_response()), \
                patch('os.environ', {'api_key': 'mock_api_key'}):
            response = views_google.get_map_data(request)

        self.assertIn('stations', response)

    def mock_geocode_response(self):
        return {
            "results": [
                {
                    "geometry": {
                        "location": {"lat": 40.712776, "lng": -74.005974}
                    }
                }
            ]
        }

    def mock_nearby_gas_search_response(self):
        return {
            "results": [
                {
                    "name": "Gas Station 1",
                    "vicinity": "123 Main St",
                    "geometry": {"location": {"lat": 40.712776, "lng": -74.005974}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                },
                {
                    "name": "Gas Station 2",
                    "vicinity": "456 Elm St",
                    "geometry": {"location": {"lat": 40.712345, "lng": -74.001234}},
                    "icon": "gas_station_icon",
                    "icon_background_color": "#ffffff",
                    "icon_mask_base_uri": "mask_uri",
                    "business_status": "OPERATIONAL"
                }
            ]
        }
