import hydra
from hydra.utils import instantiate
from omegaconf import DictConfig


@hydra.main(version_base="1.3")
def main(node_cfg: DictConfig) -> None:
    """Instantiate a standalone dora node.

    This function is used as a shim to launch a dora node using Popen to simulate how dora would launch it.
    """
    node = instantiate(node_cfg, _convert_="all")
    node.spin()


if __name__ == "__main__":
    main()
