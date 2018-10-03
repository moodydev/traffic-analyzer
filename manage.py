import argparse

from app import ENVIRONMENTS, scripts


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'command',
        help='Command to be executed',
        choices=['runserver', 'load_analyzer', 'shell']
    )

    parser.add_argument(
        '-e', '--environment',
        help='Choose config environment that will be used',
        default='development',
        choices=ENVIRONMENTS.keys(),
        required=False,
        dest='environment'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    # TODO set global env variable, so it't not injected in scripts
    if args.command == 'runserver':
        scripts.runserver(args.environment)

    if args.command == 'load_analyzer':
        scripts.load_analyzer(args.environment)

    if args.command == 'shell':
        scripts.shell(args.environment)
