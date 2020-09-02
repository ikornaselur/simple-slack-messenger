import json
import urllib.request
from typing import Dict, List, Optional

from simple_slack_messenger.local_types import Payload, Block


class Slack:
    token: str
    base_url: str

    def __init__(self, token: str, base_url: str = "https://slack.com/api/") -> None:
        self.token = token
        self.base_url = base_url

    def _post(self, method: str, payload: Optional[Payload] = None) -> Dict:
        if payload is None:
            data = None
        else:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{method}",
            data=data,
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        response = urllib.request.urlopen(request)
        parsed = json.loads(response.read())

        if not parsed["ok"]:
            print(json.dumps(parsed, indent=2))
            raise Exception("Request failed")

        return parsed

    def post_message(
        self,
        channel: str,
        text: Optional[str] = None,
        blocks: Optional[List[Block]] = None,
    ) -> Dict:
        method = "chat.postMessage"

        payload: Payload = {
            "channel": channel,
        }
        if text is not None:
            payload["text"] = text
        if blocks is not None:
            payload["blocks"] = blocks

        return self._post(method, payload)

    def edit_message(
        self,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[List[Block]] = None,
    ) -> Dict:
        method = "chat.update"

        payload: Payload = {
            "channel": channel,
            "ts": ts,
        }
        if text is not None:
            payload["text"] = text
        if blocks is not None:
            payload["blocks"] = blocks

        return self._post(method, payload)

    def auth_test(self) -> Dict:
        method = "auth.test"

        return self._post(method)
