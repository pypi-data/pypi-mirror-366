from scloud_api.base import Client, ApiResponse

class QueuedJobs(Client):
    def get_queued_job(self, job_id) -> ApiResponse:
        """
        get_queued_job(self, job_id) -> ApiResponse

        :param job_id: int the job id to
        :return: ApiResponse
        """
        return self._request(f"/api/QueuedJobs/{job_id}", "GET")