from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.endpoints.simplesat.AnswersIdEndpoint import AnswersIdEndpoint
from pysimplesat.endpoints.simplesat.AnswersSearchEndpoint import AnswersSearchEndpoint


class AnswersEndpoint(
    SimpleSatEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "answers", parent_endpoint=parent_endpoint)
        self.search = self._register_child_endpoint(AnswersSearchEndpoint(client, parent_endpoint=self))

    def id(self, id: int) -> AnswersIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized AnswersIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            AnswersIdEndpoint: The initialized AnswersIdEndpoint object.
        """
        child = AnswersIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
