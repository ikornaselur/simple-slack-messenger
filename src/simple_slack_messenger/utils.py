from typing import List

from simple_slack_messenger.local_types import Block


def set_block_state(blocks: List[Block], step: str, state: str) -> List[Block]:
    """ Find the block based on step and set the state """
    block_idx = -1

    for idx, block in enumerate(blocks):
        if f"*{step}*" in block["text"]["text"]:
            block_idx = idx
            break

    if block_idx == -1:
        raise Exception("Block not found")

    blocks[block_idx]["text"]["text"] = f"*{step}*: {state}"

    return blocks
