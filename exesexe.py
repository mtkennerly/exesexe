__all__ = [
    "interpret",
    "parse_directive"
]

import subprocess
import sys

_help_message = """
usage: exesexe [-h] directive command [command ...]

Manipulate return codes from executables.

positional arguments:
  directive   directive for parsing return code
  command     command to be evaluated

optional arguments:
  -h, --help  show this help message and exit

The directive is a comma-separated list, where each segment may have one of
these forms:

  1      whitelist 1 (convert to 0)
  -1=2   substitute -1 with 2
  5:8=9  substitute 5, 6, 7, and 8 with 9
  !1     blacklist 1 (don't convert 1 at all; convert everything else to 0)
  *=3    substitute all others with 3

The precedence order is whitelists, specific substitutions, blacklists,
then *-substitutions, so *=4,1=2,!3 would convert 1 to 2 rather than 4 or 0.
The lexical order only matters for overlapping segments, like 1=0,1=2,
where the rightmost segment overrides the left segments.
""".strip()


def _parse_args(argv=None):
    # Can't just use argparse since -h may be in the command to interpret.

    if not argv:
        argv = sys.argv

    if len(argv) >= 2 and argv[1] in ["-h", "--help"]:
        print(_help_message)
        sys.exit(0)
    elif len(argv) < 3:
        print(_help_message)
        sys.exit(1)

    return argv[1], argv[2:]


def _parse_subdirectives(whitelist, blacklist, substitutions):
    if whitelist is None:
        whitelist = []
    elif isinstance(whitelist, int):
        whitelist = [whitelist]

    if blacklist is None:
        blacklist = []
    elif isinstance(blacklist, int):
        blacklist = [blacklist]

    if substitutions is None:
        substitutions = {}

    if len(whitelist) == 0 and len(blacklist) == 0 and len(substitutions) == 0:
        raise ValueError("Must specify at least one criterion")

    return whitelist, blacklist, substitutions


def parse_directive(directive):
    """
    Parse a directive into a whitelist, blacklist, and substitution map.

    :param str directive: Directive to parse
    :return: whitelist, blacklist, substitutions
    :rype: tuple[list, list, dict]
    """

    whitelist = []
    blacklist = []
    substitutions = {}

    for segment in directive.split(","):
        if segment.startswith("*="):
            scope = ["*"]
        elif ":" in segment:
            start, stop = segment.strip("!").split("=")[0].split(":")
            scope = range(*sorted([int(start), int(stop) + 1]))
        else:
            start = int(segment.strip("!").split("=")[0])
            scope = range(start, start + 1)

        for code in scope:
            if "=" in segment:
                sub = int(segment.split("=")[1])

                if segment.startswith("!"):
                    blacklist.append(code)
                    substitutions["*"] = sub
                else:
                    substitutions[code] = sub
            elif segment.startswith("!"):
                blacklist.append(code)
            else:
                whitelist.append(code)

    return whitelist, blacklist, substitutions


def interpret(command, whitelist=None, blacklist=None, substitutions=None):
    """
    Run a command and interpret its return code.

    :param command: Command to execute and interpret its return code
    :type command: list or str
    :param whitelist: Return codes to convert to 0
    :type whitelist: list or int or None
    :param blacklist: Return codes to leave alone (whitelist others)
    :type blacklist: list or int or None
    :param substitutions: Return codes to map to a specific code
    :type substitutions: dict or None
    :return: Interpreted return code
    :rtype: int
    """

    whitelist, blacklist, substitutons = _parse_subdirectives(
        whitelist, blacklist, substitutions
    )

    code = subprocess.call(command)

    if whitelist and code in whitelist:
        return 0
    elif substitutions and code in substitutions:
        return substitutions[code]
    elif blacklist:
        if code in blacklist:
            return code
        elif substitutions and "*" in substitutions:
            return substitutions["*"]
        else:
            return 0
    else:
        return substitutions.get("*", code)


def main():
    directive, command = _parse_args()
    whitelist, blacklist, substitutions = parse_directive(directive)
    code = interpret(command, whitelist, blacklist, substitutions)
    sys.exit(code)


if __name__ == "__main__":
    main()
