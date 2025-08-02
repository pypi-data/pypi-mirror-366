from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IGettable,
    IPuttable
)
from pysimplesat.models.simplesat import Customer
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class CustomersIdEndpoint(
    SimpleSatEndpoint,
    IGettable[Customer, SimpleSatRequestParams],
    IPuttable[Customer, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Customer)
        IPuttable.__init__(self, Customer)

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Customer:
        """
        Performs a GET request against the /customers/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_one(
            Customer,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def put(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Customer:
        """
        Performs a PUT request against the /customers/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Customer: The parsed response data.
        """
        return self._parse_one(
            Customer,
            super()._make_request("PUT", data=data, params=params).json(),
        )
