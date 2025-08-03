import atexit
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def write_tmp(subcfg: DictConfig, tmp_dir: Path, name: str) -> Path:
    """Write a temporary yaml file for the given subconfig."""
    yaml_data = OmegaConf.to_yaml(subcfg, resolve=True)
    yaml_path = tmp_dir / f"{name}.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_data)
    return yaml_path


def run(cfg: DictConfig) -> None:
    """Main function to run the judo stack."""
    tmp_dir = Path(tempfile.mkdtemp())

    # [HACK] instantiate dora nodes specified in the hydra config
    # we extract each node config and write it to a temp yaml file, then use dora to launch the node using Popen.
    # there were strange interactions when trying to spin the nodes by manually calling spin with threading or mp, but
    # this workaround seems to work with dynamic nodes.
    dataflow_path = write_tmp(cfg.dataflow, tmp_dir, "tmp_dataflow")
    dora = subprocess.Popen(f"dora up && dora start {dataflow_path}", shell=True, start_new_session=True)

    yaml_paths = []
    node_processes = []
    for node_cfg in cfg.node_definitions.values():
        # allow skipping of node definitions by setting to null when overriding configs
        if node_cfg is None:
            continue

        node_name = f"tmp_{node_cfg.node_id}"
        yaml_path = write_tmp(node_cfg, tmp_dir, node_name)
        p = subprocess.Popen(
            f"python {Path(__file__).parent}/_launch_node.py -cp {tmp_dir} -cn {node_name}",
            shell=True,
            start_new_session=True,
        )
        yaml_paths.append(yaml_path)
        node_processes.append(p)

    # register callback to tear down dora cleanly and terminate all node processes
    cleaned = False
    def _cleanup():
        nonlocal cleaned
        if cleaned:
            return  # idempotent cleanup
        cleaned = True

        # tear down dora daemon and coordinator
        subprocess.run(["dora", "destroy"], check=True)

        # terminate all node processes if they are still running
        for p in node_processes:
            try:
                if p.poll() is None:
                    os.killpg(p.pid, signal.SIGINT)
                    p.wait(timeout=5)
            except Exception:
                pass

        # remove temporary yaml files
        shutil.rmtree(tmp_dir, ignore_errors=True)

    atexit.register(_cleanup)

    # don't terminate the script until the main dora process does
    caught_keyboard_interrupt = False
    try:
        dora.wait()
    except KeyboardInterrupt:
        caught_keyboard_interrupt = True
        pass
    finally:
        _cleanup()
        if caught_keyboard_interrupt:
            raise KeyboardInterrupt("Caught KeyboardInterrupt, cleaning up and exiting.")
        sys.exit(0)
