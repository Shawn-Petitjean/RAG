import fire  # type: ignore[import-untyped]
from .interface import Cli


def main() -> None:
    fire.Fire(Cli)


if __name__ == "__main__":
    main()
