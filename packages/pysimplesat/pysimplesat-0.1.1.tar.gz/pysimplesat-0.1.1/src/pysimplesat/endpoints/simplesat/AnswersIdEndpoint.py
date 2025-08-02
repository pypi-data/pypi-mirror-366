from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IGettable,
    IPuttable
)
from pysimplesat.models.simplesat import Answer
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class AnswersIdEndpoint(
    SimpleSatEndpoint,
    IGettable[Answer, SimpleSatRequestParams],
    IPuttable[Answer, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Answer)
        IPuttable.__init__(self, Answer)

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Answer:
        """
        Performs a GET request against the /answers/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_one(
            Answer,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def put(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Answer:
        """
        Performs a PUT request against the /answers/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Answer: The parsed response data.
        """
        return self._parse_one(
            Answer,
            super()._make_request("PUT", data=data, params=params).json(),
        )
