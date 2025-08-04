import os
import re
from argparse import _SubParsersAction


class Install:
    IGNORES = [
        "pkg_resources==0.0.0",  # This can't be installed.
    ]

    def __git1(self, line: str):
        """
        Git with credentials and commit hash.
        """
        match = re.search(
            r"^(\S+)\s+@\s+git\+https?\:\/\/([^@]+)@([^@]+)@([^@]+)$",
            line,
            re.I,
        )

        if match is None:
            return

        return f"-e git+https://{match[2]}@{match[3]}@{match[4]}#egg={match[1]}"

    def __git2(self, line: str):
        """
        Git with credentials.
        """
        match = re.search(
            r"^(\S+)\s+@\s+git\+https?\:\/\/([^@]+)@([^@]+)$",
            line,
            re.I,
        )

        if match is None:
            return

        return f"-e git+https://{match[2]}@{match[3]}#egg={match[1]}"

    def __selector(self, line: str):
        if not line:
            return

        if line in self.IGNORES:
            return

        value = self.__git1(line)

        if value:
            return value

        value = self.__git2(line)

        if value:
            return value

        return line

    def __main(self, args):
        filepath = args.f
        output = args.o

        with open(filepath, "r") as f1:
            with open(output, "w") as f2:
                f2.write(
                    "\n".join(
                        selected
                        for line in f1.readlines()
                        if (selected := self.__selector(line.strip()))
                    )
                )

        os.system(f"pip install -r {output}")

    def run(self, subparsers: _SubParsersAction):
        parser = subparsers.add_parser(
            "install",
            help="pip install",
        )

        parser.add_argument(
            "-f",
            type=str,
            help="filepath",
            default="requirements.txt",
            required=False,
        )

        parser.add_argument(
            "-o",
            type=str,
            help="output",
            default="fun.requirements.txt",
            required=False,
        )

        parser.set_defaults(func=self.__main)
