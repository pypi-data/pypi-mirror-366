#!/usr/bin/env python

from esi_utils_io.cmd import get_command_output


def test_get_command_output():
    cmd = "ls *.md"
    rc, so, se = get_command_output(cmd)
    assert rc is True

    cmd = "ls asdf"
    rc, so, se = get_command_output(cmd)
    assert rc is False


if __name__ == "__main__":
    test_get_command_output()
