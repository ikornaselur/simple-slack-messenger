from typing import List

from simple_slack_messenger.types import Block


def set_block_state(
    blocks: List[Block], environment: str, step: str, state: str
) -> List[Block]:
    """ Find the block based on environment and step and set the state """
    block_idx = -1
    environment_section = False

    for idx, block in enumerate(blocks):
        if block["text"]["text"] == environment:
            environment_section = True
        if environment_section and f"*{step}*" in block["text"]["text"]:
            block_idx = idx
            break

    if block_idx == -1:
        raise Exception("Block not found")

    blocks[block_idx]["text"]["text"] = f"*{step}*: {state}"

    return blocks
