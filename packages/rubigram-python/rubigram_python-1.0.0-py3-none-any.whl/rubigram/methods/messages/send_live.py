
from typing import Optional
import rubigram


class SendLive:
    async def send_live(
        self: "rubigram.Client",
        object_guid: str,
        auto_delete: Optional[int] = None,
        *args, **kwargs,
    ) -> rubigram.types.Update:
        """
        Send a live message.

        Args:
            object_guid (str):
                The GUID of the group or user to send the live message to.

            auto_delete (int, optional):
                Duration in seconds after which the message will be auto-deleted.
        """
        return await self.send_message(
            object_guid=object_guid,
            type="SendLive",
            auto_delete=auto_delete,
            *args, **kwargs
        )
