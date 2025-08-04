import os
import re
from argparse import _SubParsersAction
from configparser import ConfigParser
from typing import List, Optional

from ..not_chalk import NotChalk

try:
    from simple_chalk import chalk  # type: ignore
except Exception:
    chalk = NotChalk()


class Freeze:
    RX_BITBUCKET_EDITABLE = r"^-e git\+https:\/\/(?:(.+)@)?bitbucket\.org\/(.+)\/(.+?)(?:\.git)?@(.+)#egg=.+$"
    RX_BITBUCKET = (
        r"^(.+)\s@\sgit\+https:\/\/bitbucket\.org\/(.+)\/(.+?)(?:\.git)?(?:@(.+))?$"
    )
    IGNORES = [
        "pkg_resources==0.0.0",  # This can't be installed.
    ]

    def __add(
        self,
        line: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = line

        print(message)

        self.__lines.append(line.strip() + "\r\n")

    def __warn(self):
        self.__warns += 1

    def __setup_cfg(self, args, lines: List[str]):
        if not args.cfg:
            return

        config = ConfigParser(
            allow_no_value=True,
            comment_prefixes=[],
            strict=False,
        )

        config.read(args.cfg_path)

        if not config.has_option("options", "install_requires"):
            return

        text = "\n" + "".join(lines).strip()
        config["options"]["install_requires"] = text

        with open(args.cfg_path, "w") as f:
            config.write(f)

        print(chalk.gray.dim(f"Updated `{args.cfg_path}`."))

    def __bitbucket_editable(self, line: str):
        match = re.match(self.RX_BITBUCKET_EDITABLE, line)

        if match is None:
            return False

        access_token = match[1]
        access_token = f"{access_token}@" if access_token is not None else ""
        path = match[2]
        name = match[3]
        commit_hash = match[4]
        text = f"{name} @ git+https://{access_token}bitbucket.org/{path}/{name}@{commit_hash}"

        self.__add(
            text,
            chalk.green(text),
        )

        return True

    def __bitbucket(self, line: str):
        match = re.match(self.RX_BITBUCKET, line)

        if match is None:
            return False

        # name = match[1]
        # path = match[2]
        # repository = match[3]
        # commit_hash = match[4]

        self.__add(
            line,
            "{0} {1}".format(
                chalk.yellow(line),
                chalk.green("# This might not work properly."),
            ),
        )
        self.__warn()

        return True

    def __default(self, line: str):
        self.__add(line)
        return True

    def __selector(self, line: str):
        line = line.strip()

        if line in self.IGNORES:
            return

        for fn in [
            self.__bitbucket_editable,
            self.__bitbucket,
            self.__default,
        ]:
            ok = fn(line)

            if ok:
                break

    def __main(self, args):
        filepath = args.f

        os.system(f"pip freeze > {filepath}")

        with open(filepath, "r") as f:
            for line in f.readlines():
                self.__selector(line)

        print()

        self.__setup_cfg(args, self.__lines)

        with open(filepath, "w") as f:
            f.writelines(self.__lines)

        print(chalk.gray.dim(f"Updated `{filepath}`."))

        print()

        if self.__warns > 0:
            text = "You have {0} warning(s). Scroll up.".format(
                self.__warns,
            )

            print(chalk.bgYellow.bold(text))

    def run(self, subparsers: _SubParsersAction):
        self.__lines: List[str] = []
        self.__warns = 0

        parser = subparsers.add_parser(
            "freeze",
            help="pip freeze",
        )

        parser.add_argument(
            "-f",
            type=str,
            help="filepath",
            default="requirements.txt",
            required=False,
        )

        parser.add_argument(
            "-cfg",
            type=bool,
            help="If it should write to `setup.cfg`.",
            default=True,
            required=False,
        )
        parser.add_argument(
            "-cfg_path",
            type=str,
            help="Path to `setup.cfg`.",
            default="setup.cfg",
            required=False,
        )

        parser.set_defaults(func=self.__main)
