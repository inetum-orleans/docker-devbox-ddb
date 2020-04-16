from argparse import Namespace


class RestartWithArgs(Exception):
    """
    Restart the command with given args.
    """
    def __init__(self, restart_args: Namespace, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.restart_args = restart_args  # type: Namespace
