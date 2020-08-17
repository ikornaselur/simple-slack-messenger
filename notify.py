#!/usr/bin/env python3
import json
import os
import urllib.request
from typing import Dict, Optional


class Slack:
    token: str

    def __init__(self, token: str) -> None:
        self.token = token

    def _post(self, url: str, payload: Optional[Dict] = None) -> Dict:
        if payload is None:
            data = None
        else:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        response = urllib.request.urlopen(request)

        return json.loads(response.read())

    def post_message(self, channel: str, text: str) -> Dict:
        url = "https://slack.com/api/chat.postMessage"

        payload = {
            "channel": channel,
            "text": text,
            "attachments": [{"text": "And here’s an attachment!"}],
        }

        return self._post(url, payload)

    def auth_test(self) -> Dict:
        url = "https://slack.com/api/auth.test"

        return self._post(url)


if __name__ == "__main__":
    slack = Slack(os.environ["SLACK_TOKEN"])

    response = slack.post_message("#testing", "hello there")
    # response = slack.auth_test()

    print(json.dumps(response, indent=2))
