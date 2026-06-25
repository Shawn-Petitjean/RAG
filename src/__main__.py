import fire  # type: ignore[import-untyped]
from .interface import Cli


def main() -> None:
    """it only serve the purpose of running the CLI."""
    try:
        fire.Fire(Cli)
    except Exception as e:
        print(f"an error a occured {e.__class__.__name__}\n{e}")


if __name__ == "__main__":
    main()
