from scloud_api.base import Client, ApiResponse

class Warehouses(Client):
    def get_warehouses(self, filters=None):
        return self._request('/api/Warehouses', 'GET', filters)

    def get_warehouse(self, warehouse_id):
        return self._request(f'/api/Warehouses/{warehouse_id}', 'GET')