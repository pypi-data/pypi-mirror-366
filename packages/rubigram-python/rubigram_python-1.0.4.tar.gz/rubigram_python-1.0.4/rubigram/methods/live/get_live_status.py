
import rubigram


class GetLiveStatus:
    """
    A class to handle fetching the status of a live stream from Rubigram.

    Attributes:
        client (rubigram.Client): The Rubigram client instance.
    """

    def __init__(self, client: "rubigram.Client"):
        """
        Initialize the LiveStatus with a Rubigram client.

        Args:
            client (rubigram.Client): The Rubigram client instance.
        """
        self.client = client

    async def get_live_status(
        self,
        live_id: str,
        access_token: str
    ) -> rubigram.types.Update:
        """
        Retrieve the status of a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            access_token (str): The access token required to authenticate the request.

        Returns:
            rubigram.types.Update: The update response containing live status data.
        """
        return await self.builder(
            'getLiveStatus',
            input={
                'live_id': live_id,
                'access_token': access_token
            }
        )
