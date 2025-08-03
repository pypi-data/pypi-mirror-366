from typing import Annotated

from stanlee.base_tool import Tool


class SendMessageToUser(Tool):
    name = "send_message_to_user"
    description = "Send a message to user and wait for response"

    def execute(self, message) -> str:
        return message
