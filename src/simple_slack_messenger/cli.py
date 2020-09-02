import os
import time

from simple_slack_messenger.messenger import Messenger
from simple_slack_messenger.utils import set_block_state


if __name__ == "__main__":
    messenger = Messenger(
        channel=os.environ["SLACK_CHANNEL"], message_id="deployment-test", verbose=True
    )

    envs = ["Dev", "Staging"]
    steps = ["Migrations", "Deploy", "Other things", "Extra stuff"]

    result = messenger.create_deployment(environments=envs, steps=steps)

    channel_id = result["channel"]
    ts = result["ts"]
    blocks = result["message"]["blocks"]
    text = result["message"]["text"]

    # Simulate waits for testing
    for environment in envs:
        time.sleep(1)
        for step in steps:
            blocks = set_block_state(
                blocks,
                environment=environment,
                step=step,
                state=":loading: In progress...",
            )
            response = messenger.update_deployment(ts, blocks=blocks)
            time.sleep(1)
            blocks = set_block_state(
                blocks,
                environment=environment,
                step=step,
                state=":heavy_check_mark: Done!",
            )

    blocks[0]["text"]["text"] = "The deployment has been finished"
    messenger.update_deployment(ts, blocks=blocks)
