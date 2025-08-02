from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.endpoints.simplesat.SurveysIdEndpoint import SurveysIdEndpoint
from pysimplesat.interfaces import (
    IGettable,
)
from pysimplesat.models.simplesat import Survey
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class SurveysEndpoint(
    SimpleSatEndpoint,
    IGettable[Survey, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "surveys", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Survey)

    def id(self, id: int) -> SurveysIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized SurveysIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            SurveysIdEndpoint: The initialized SurveysIdEndpoint object.
        """
        child = SurveysIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Survey:
        """
        Performs a GET request against the /surveys endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Survey: The parsed response data.
        """
        print("get")
        return self._parse_many(
            Survey,
            super()._make_request("GET", data=data, params=params).json().get('surveys', {}),
        )
