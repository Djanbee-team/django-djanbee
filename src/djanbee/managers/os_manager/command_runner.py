from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import shlex
import subprocess

@dataclass
class CommandResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int

    def __bool__(self):
        return self.success

    def __iter__(self):
        msg = self.stdout if self.success else self.stderr
        yield self.success
        yield msg


class CommandRunner:
    def run(
        self,
        args: Union[str, List[str]],
        cwd: Optional[Path] = None,
        sudo: bool = False
    ) -> CommandResult:
        # turn a string into a list
        if isinstance(args, str):
            cmd = shlex.split(args)
        else:
            cmd = args[:]
        if sudo:
            cmd = ["sudo"] + cmd

        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return CommandResult(
            success=(proc.returncode == 0),
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            exit_code=proc.returncode,
        )
