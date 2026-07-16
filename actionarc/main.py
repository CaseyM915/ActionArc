"""ActionArc entry point."""

from actionarc.gui.application import run_application


def main() -> None:
    """Launch the ActionArc desktop application."""
    raise SystemExit(run_application())


if __name__ == "__main__":
    main()