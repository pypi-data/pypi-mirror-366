from scloud_api.base import Client, ApiResponse

class Settings(Client):
    def get_shipping_carriers(self, site_code=0) -> ApiResponse:
        return self._request('/api/Settings/ShippingCarriers', "GET", {'siteCode': site_code})

    def get_shipping_services(self, carrier, site_code=0) -> ApiResponse:
        return self._request('/api/Settings/ShippingServices', 'GET', {'carrier': carrier, 'siteCode': site_code})