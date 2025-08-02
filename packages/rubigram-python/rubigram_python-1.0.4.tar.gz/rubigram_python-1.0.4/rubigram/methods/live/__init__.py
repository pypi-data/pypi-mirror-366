
from .add_live_comment import AddLiveComment
from .get_live_comments import GetLiveComments
from .get_live_status import GetLiveStatus
from .send_live import SendLive


class Lives(
    AddLiveComment,
    GetLiveComments,
    GetLiveStatus,
    SendLive
):
    pass
