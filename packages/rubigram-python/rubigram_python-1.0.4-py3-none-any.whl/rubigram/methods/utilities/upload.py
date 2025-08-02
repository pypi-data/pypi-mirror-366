
import rubigram
from .progress import Progress


class UploadFile:
    """
    Provides a method to upload a file.

    Methods:
    - upload: Upload a file.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def upload(self: "rubigram.Client", file, *args,
                     **kwargs) -> "rubigram.types.Update":
        """
        Upload a file.

        Args:
        - file: The file to be uploaded.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The result of the file upload operation.
        """
        return await self.connection.upload_file(file=file, callback=Progress(), *args, **kwargs)
