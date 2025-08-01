from typing import List

from fastapi.encoders import jsonable_encoder

from appodus_utils.messaging.models import MessageRequest
from appodus_utils.sdk.appodus_sdk.communication.chat_bot_client import ChatBotClient
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class CommunicationClient:
    def __init__(self, communication_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._communication_manager_url = communication_manager_url

    async def send_messages(self, message_requests: List[MessageRequest]):
        endpoint = f"{self._communication_manager_url}/{self._client_utils.get_api_version}/messages/"
        message_requests_data = jsonable_encoder(message_requests)
        headers = self._client_utils.auth_headers("post", f"{endpoint}", message_requests_data)
        response = await self._client_utils.get_http_client.post(f"{endpoint}", json=message_requests_data, headers=headers)
        response.raise_for_status()

        return response.json()

    @property
    def chat_bot_client(self) -> ChatBotClient:
        return ChatBotClient(
            communication_manager_url=self._communication_manager_url,
            client_utils=self._client_utils
        )
