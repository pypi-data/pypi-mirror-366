# Dora Utils
This repository contains some simple utilities for using [`dora`](https://github.com/dora-rs/dora) that improve QoL.

To install, run
```bash
pip install dora-utils
```

For simple usage examples, see `dora_utils.examples`.

## The `DoraNode` class
The usual workflow in `dora` is to define a `Node`, which acts as an iterator over events. In this loop, you can then manually handle the events as they arrive in the node. We provide a convenient `DoraNode` convenience class to register callbacks on events in a more ROS-style fashion. Consider the `talker.py` and `listener.py` examples:
```
# talker.py
import pyarrow as pa

from dora_utils.node import DoraNode, on_event


class Talker(DoraNode):
    """Simple publisher node for a Dora tutorial."""

    @on_event("INPUT", "tick")
    def talk(self, event: dict) -> None:
        self.node.send_output("speech", pa.array(["Hello World"]))
```
```
# listener.py
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

```

The `on_event` decorator provides a simple interface for registering callbacks to inputs specified into the node using `dora`'s dataflow.yml. You can register the same callback to multiple inputs by instead passing a sequence of input names into `on_event`.

## Hydra Configuration
One sharp edge regarding `dora` is node configuration. The typical workflow is writing a script-style program where you can manually configure nodes and spin them. This is a bit cumbersome once the system scales up to many nodes with many arguments that you might want to configure in a more organized way. We provide an example design pattern that combines the `dataflow.yml` configuration system from `dora` with `hydra`.

For an example, consider `scripts/chatter.yaml`, which both defines a simple "chatter" workflow between a talker and listener node.
```
# this section of the configuration specifies the dora dataflow
dataflow:
  nodes:
    - id: talker
      path: dynamic
      inputs:
        tick: dora/timer/millis/10
      outputs:
        - speech
    - id: listener
      path: dynamic
      inputs:
        speech: talker/speech

# everything else is used to instantiate and spin the nodes with hydra
node_definitions:
  talker:  # <--- this name doesn't matter
    _target_: dora_utils.examples.chatter.talker.Talker
    node_id: talker
    max_workers: null
  listener:  # <--- this name doesn't matter
    _target_: dora_utils.examples.chatter.listener.Listener
    node_id: listener
    max_workers: null
    override_msg: null

```
Everything under the `dataflow` section is the "standard" `dora` dataflow, which defines the nodes, their IDs, their inputs/outputs, etc. Under `node_definitions` is a list of `hydra` targets, so you can instantiate arbitrarily complicated nodes using `hydra`'s composition API. Above, you'll see that there are comments saying "this name doesn't matter." We use this yaml syntax because we want to be able to use `hydra`'s configuration override syntax to preserve default values. Because lists are atomic in `hydra`, we can't override single list elements, so in any file that specifies another configuration file as a default, we would have to copy and paste the entire `node_definitions` section. When we instead structure things like a dictionary, overrides work!

If we run
```bash
python scripts/run.py -cn chatter
```
we will start the chatter example, and we should see the following printed a lot:
```
I heard Hello World from speech
I heard Hello World from speech
I heard Hello World from speech
```

Now, if we modify `chatter.yaml` to instead show
```
node_definitions:
  talker:
    _target_: dora_utils.examples.chatter.talker.Talker
    node_id: talker
    max_workers: null
  listener:
    _target_: dora_utils.examples.chatter.listener.Listener
    node_id: listener
    max_workers: null
    override_msg: "override"  # change this field for this example!
```
and run the same command, we will see
```
I heard override from speech
I heard override from speech
I heard override from speech
```

When you import the `dora_utils` package to your own project, you can use the `hydra` configuration design pattern as in our `scripts/run.py` file:
```
from pathlib import Path

import hydra
from omegaconf import DictConfig

from dora_utils.launch.run import run

CONFIG_PATH = Path(__file__).parent / "configs"


@hydra.main(config_path=str(CONFIG_PATH), config_name="default", version_base="1.3")
def main(cfg: DictConfig) -> None:
    """Main function to run a dora stack via a hydra configuration yaml file."""
    run(cfg)


if __name__ == "__main__":
    main()
```
The main variables to change in your downstream project are the configuration path and configuration name. Note that these can easily be overwritten from the command line, e.g., as follows:
```bash
python scripts/run.py -cp <my_config_path> -cn <my_config_name>
```
