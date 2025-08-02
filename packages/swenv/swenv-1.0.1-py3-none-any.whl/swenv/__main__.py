from __future__ import annotations

from swenv import __doc__, __prog__, __version__, configure, status, update
from swenv.utils import (add_command, configure_logging, create_command_parser,
                         exec_command)


def main():
    configure_logging()

    # Define commands
    parser = create_command_parser(__prog__, version=__version__, doc=__doc__)
    subparsers = parser.add_subparsers(title='commands')
    add_command(subparsers, configure)
    add_command(subparsers, status)
    add_command(subparsers, update)

    # Execute command
    exec_command(parser, default='update')
    

if __name__ == '__main__':
    main()
