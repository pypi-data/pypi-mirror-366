import argparse
import sys
from pathlib import Path


class CheckInputExist(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None:
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(CheckInputExist, self).__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Path,
        option_string: str = None,
    ) -> None:
        if values.exists():
            setattr(namespace, self.dest, values)
        else:
            print(
                f"ERROR: The file, {values}, was not found. Please make sure that there is not a typo in the file name."
            )
            sys.exit(1)
