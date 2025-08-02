from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IGettable,
)
from pysimplesat.models.simplesat import TeamMember
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class TeamMembersIdEndpoint(
    SimpleSatEndpoint,
    IGettable[TeamMember, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, TeamMember)

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> TeamMember:
        """
        Performs a GET request against the /team-members/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_one(
            TeamMember,
            super()._make_request("GET", data=data, params=params).json(),
        )
