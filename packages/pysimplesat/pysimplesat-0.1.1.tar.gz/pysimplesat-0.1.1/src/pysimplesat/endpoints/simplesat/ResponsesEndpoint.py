from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.endpoints.simplesat.ResponsesIdEndpoint import ResponsesIdEndpoint
from pysimplesat.endpoints.simplesat.ResponsesSearchEndpoint import ResponsesSearchEndpoint
from pysimplesat.endpoints.simplesat.ResponsesCreateOrUpdateEndpoint import ResponsesCreateOrUpdateEndpoint


class ResponsesEndpoint(
    SimpleSatEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "responses", parent_endpoint=parent_endpoint)
        self.search = self._register_child_endpoint(ResponsesSearchEndpoint(client, parent_endpoint=self))
        self.createorupdate = self._register_child_endpoint(ResponsesCreateOrUpdateEndpoint(client, parent_endpoint=self))

    def id(self, id: int) -> ResponsesIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized ResponsesIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            ResponsesIdEndpoint: The initialized ResponsesIdEndpoint object.
        """
        child = ResponsesIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
