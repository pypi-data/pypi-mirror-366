from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IPuttable,
)
from pysimplesat.models.simplesat import Response
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class ResponsesIdUpdateEndpoint(
    SimpleSatEndpoint,
    IPuttable[Response, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IPuttable.__init__(self, Response)

    def put(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Response:
        """
        Performs a PUT request against the /responses/{id}/update endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Response: The parsed response data.
        """
        return self._parse_one(
            Response,
            super()._make_request("PUT", data=data, params=params).json(),
        )
