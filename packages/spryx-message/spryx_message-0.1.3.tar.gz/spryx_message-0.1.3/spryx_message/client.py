from spryx_http import SpryxAsyncClient

from spryx_message.resources.channels import Channels
from spryx_message.resources.contacts import Contacts
from spryx_message.resources.files import Files
from spryx_message.resources.messages import Messages


class SpryxMessage(SpryxAsyncClient):
    def __init__(
        self,
        application_id: str,
        application_secret: str,
        base_url: str = "https://dev-message.spryx.ai",
        iam_base_url: str = "https://dev-iam.spryx.ai",
    ):
        super().__init__(
            base_url=base_url,
            iam_base_url=iam_base_url,
            application_id=application_id,
            application_secret=application_secret,
        )

        self.channels = Channels(self)
        self.contacts = Contacts(self)
        self.files = Files(self)
        self.messages = Messages(self) 