import typing
from datetime import datetime, timezone

from pysimplesat.clients.base_client import SimpleSatClient
from pysimplesat.config import Config

if typing.TYPE_CHECKING:
    from pysimplesat.endpoints.simplesat.SurveysEndpoint import SurveysEndpoint
    from pysimplesat.endpoints.simplesat.AnswersEndpoint import AnswersEndpoint
    from pysimplesat.endpoints.simplesat.CustomersEndpoint import CustomersEndpoint
    from pysimplesat.endpoints.simplesat.QuestionsEndpoint import QuestionsEndpoint
    from pysimplesat.endpoints.simplesat.TeamMembersEndpoint import TeamMembersEndpoint
    from pysimplesat.endpoints.simplesat.ResponsesEndpoint import ResponsesEndpoint


class SimpleSatAPIClient(SimpleSatClient):
    """
    SimpleSat API client. Handles the connection to the SimpleSat API
    and the configuration of all the available endpoints.
    """

    def __init__(
        self,
        privatekey: str,
    ) -> None:
        """
        Initializes the client with the given credentials.

        Parameters:
            privatekey (str): Your SimpleSat API private key.
        """
        self.privatekey: str = privatekey
        self.token_expiry_time: datetime = datetime.now(tz=timezone.utc)

    # Initializing endpoints
    @property
    def surveys(self) -> "SurveysEndpoint":
        from pysimplesat.endpoints.simplesat.SurveysEndpoint import SurveysEndpoint

        return SurveysEndpoint(self)

    @property
    def answers(self) -> "AnswersEndpoint":
        from pysimplesat.endpoints.simplesat.AnswersEndpoint import AnswersEndpoint

        return AnswersEndpoint(self)

    @property
    def customers(self) -> "CustomersEndpoint":
        from pysimplesat.endpoints.simplesat.CustomersEndpoint import CustomersEndpoint

        return CustomersEndpoint(self)

    @property
    def questions(self) -> "QuestionsEndpoint":
        from pysimplesat.endpoints.simplesat.QuestionsEndpoint import QuestionsEndpoint

        return QuestionsEndpoint(self)

    @property
    def team_members(self) -> "TeamMembersEndpoint":
        from pysimplesat.endpoints.simplesat.TeamMembersEndpoint import TeamMembersEndpoint

        return TeamMembersEndpoint(self)

    @property
    def responses(self) -> "ResponsesEndpoint":
        from pysimplesat.endpoints.simplesat.ResponsesEndpoint import ResponsesEndpoint

        return ResponsesEndpoint(self)


    def _get_url(self) -> str:
        """
        Generates and returns the URL for the SimpleSat API endpoints based on the company url and codebase.
        Logs in an obtains an access token.
        Returns:
            str: API URL.
        """
        return f"https://api.simplesat.io/api/v1"

    def _get_headers(self) -> dict[str, str]:
        """
        Generates and returns the headers required for making API requests. The access token is refreshed if necessary before returning.

        Returns:
            dict[str, str]: Dictionary of headers including Content-Type, Client ID, and Authorization.
        """
        return {
            "Content-Type": "application/json",
            "X-Simplesat-Token": f"{self.privatekey}",
        }
