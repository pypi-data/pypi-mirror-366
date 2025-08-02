class ApiResponse:
    def __init__(self, status_code, response, error):
        self.status_code = status_code
        self.payload = response['Items'] if 'Items' in response else response
        self.total_results = response['TotalResults'] if 'TotalResults' in response else None
        if status_code != 200 and response:
            self.error = response
        else:
            self.error = error