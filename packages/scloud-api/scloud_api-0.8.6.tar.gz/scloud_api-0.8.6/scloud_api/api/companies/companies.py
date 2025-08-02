from scloud_api.base import Client, ApiResponse

class Companies(Client):
    def get_companies(self, filters=None):
        return self._request("/api/Companies", "GET", filters)

    def get_company(self, company_id):
        return self._request(f"/api/Companies/{company_id}", "GET")