from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.endpoints.simplesat.TeamMembersIdEndpoint import TeamMembersIdEndpoint
from pysimplesat.interfaces import (
    IPostable,
)
from pysimplesat.models.simplesat import TeamMember
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class TeamMembersEndpoint(
    SimpleSatEndpoint,
    IPostable[TeamMember, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "team-members", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, TeamMember)

    def id(self, id: int) -> TeamMembersIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized TeamMembersIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            TeamMembersIdEndpoint: The initialized TeamMembersIdEndpoint object.
        """
        child = TeamMembersIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child

    def post(self, data: JSON | None = None, params: SimpleSatRequestParams | None = None) -> TeamMember:
        """
        Performs a POST request against the /team-members endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            TeamMember: The parsed response data.
        """
        return self._parse_one(TeamMember, super()._make_request("POST", data=data, params=params).json())
