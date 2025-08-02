from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.endpoints.simplesat.SurveysIdEmailEndpoint import SurveysIdEmailEndpoint


class SurveysIdEndpoint(
    SimpleSatEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.email = self._register_child_endpoint(SurveysIdEmailEndpoint(client, parent_endpoint=self))
