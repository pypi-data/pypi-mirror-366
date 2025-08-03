from dora_utils.node import DoraNode, on_event


class Listener(DoraNode):
    """Simple publisher node for a Dora tutorial."""

    def __init__(
        self, node_id: str = "listener", max_workers: int | None = None, override_msg: str | None = None
    ) -> None:
        """Initialize the listener."""
        super().__init__(node_id=node_id, max_workers=max_workers)
        self.override_msg = override_msg

    @on_event("INPUT", "speech")
    def listen(self, event: dict) -> None:
        if self.override_msg is not None:
            message = self.override_msg
        else:
            message = event["value"][0].as_py()
        print(f"""I heard {message} from {event["id"]}""")
