from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IGettable,
)
from pysimplesat.models.simplesat import Question
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class QuestionsEndpoint(
    SimpleSatEndpoint,
    IGettable[Question, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "questions", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Question)

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Question:
        """
        Performs a GET request against the /questions endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Question: The parsed response data.
        """
        print("get")
        return self._parse_many(
            Question,
            super()._make_request("GET", data=data, params=params).json().get('questions', {}),
        )
