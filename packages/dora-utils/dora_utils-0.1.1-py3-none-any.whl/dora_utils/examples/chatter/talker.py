import pyarrow as pa

from dora_utils.node import DoraNode, on_event


class Talker(DoraNode):
    """Simple publisher node for a Dora tutorial."""

    @on_event("INPUT", "tick")
    def talk(self, event: dict) -> None:
        self.node.send_output("speech", pa.array(["Hello World"]))
