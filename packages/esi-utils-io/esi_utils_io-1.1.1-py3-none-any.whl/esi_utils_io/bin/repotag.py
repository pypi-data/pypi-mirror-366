#!/usr/bin/env python

# stdlib imports
import argparse
import contextlib
import json
import os
import pathlib
import re
import subprocess
import sys
from configparser import ConfigParser
from datetime import datetime

# third party imports
import toml

VALID_VERSION_PAT = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    "(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    "(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    ")*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class RepoFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def get_command_output(cmd):
    """
    Method for calling external system command.
    Args:
        cmd: String command (e.g., 'ls -l', etc.).
    Returns:
        Three-element tuple containing a boolean indicating success or failure,
        the stdout from running the command, and stderr.
    """
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    retcode = proc.returncode
    if retcode == 0:
        retcode = True
    else:
        retcode = False
    return (retcode, stdout, stderr)


def get_branches(branch_string):
    if not len(branch_string):
        return []
    all_branches = branch_string.split("\n")
    all_branches = [branch.strip("*") for branch in all_branches]
    all_branches = [branch.strip() for branch in all_branches]
    return all_branches


def get_main_branch():
    res, stdout, stderr = get_command_output("git branch")
    branches = stdout.decode("utf8").strip().split("\n")
    for branch in branches:
        if "master" in branch:
            return "master"
        if "main" in branch:
            return "main"
    return None


def increment_minor(old_version):
    parts = old_version.split(".")
    new_minor = str(int(parts[-1]) + 1)
    new_version = ".".join(parts[0:-1] + [new_minor])
    return new_version


class RepoVersion(object):
    def __init__(self, repofolder):
        self._repofolder = repofolder
        self._using_config = (repofolder / "setup.cfg").exists()
        self._using_poetry, self._using_setuptools = self._check_toml()
        self._files_modified = []
        if sum([self._using_config, self._using_poetry, self._using_setuptools]) == 0:
            raise Exception("This repository is not using Poetry or setuptools.")

    def get_files_modified(self):
        return self._files_modified

    def _check_toml(self):
        toml_file = self._repofolder / "pyproject.toml"
        with open(toml_file, "rt") as fh:
            tdict = toml.load(fh)
        if "tool.poetry" in tdict:
            return (True, False)
        elif "Version" in tdict:
            return (False, True)
        return (False, False)

    def update_version(self, version_str):
        if self._using_poetry or self._using_setuptools:
            toml_file = self._repofolder / "pyproject.toml"
            with open(toml_file, "rt") as fh:
                tdict = toml.load(fh)
            if self._using_setuptools:
                tdict["Version"] = version_str
            else:
                tdict["tool.poetry"]["version"] = version_str
            with open(toml_file, "wt") as fh:
                toml.dump(tdict, fh)
            self._files_modified.append(toml_file)
        else:
            # TODO Make this handle pointer to text file also!
            cfg_file = self._repofolder / "setup.cfg"
            config = ConfigParser()
            config.read(cfg_file)
            config["metadata"]["version"] = version_str
            with open(cfg_file, "wt") as fh:
                config.write(fh)
            self._files_modified.append(cfg_file)

    def get_version(self):
        if self._using_config:
            config_file = self._repofolder / "setup.cfg"
            old_version = self._get_setup_version(config_file)
        else:
            project_file = self._repofolder / "pyproject.toml"
            old_version = self._get_toml_version(project_file)
        return old_version

    def _get_setup_version(self, cfg_file):
        config = ConfigParser()
        config.read(cfg_file)
        if "metadata" not in config:
            return None
        version_str = config["metadata"].get("version", None)
        if version_str is None:
            return version_str
        if re.match(VALID_VERSION_PAT, version_str) is None:
            # this might be a file
            if "file" in version_str:
                parts = version_str.split(":")
                filename = self._repofolder / parts[1].strip()
                with open(filename, "rt") as fh:
                    version_str = fh.read().strip()
                    return version_str
        return version_str

    def _get_toml_version(self, toml_file):
        with open(toml_file, "rt") as fh:
            tdict = toml.load(fh)
        if "tool.poetry" in tdict:
            return tdict["tool.poetry"].get("version", None)
        if "Version" in tdict:
            return tdict.get("Version", None)
        return None


def update_json_file(jsonfile, new_version, status):
    with open(jsonfile, "rt") as fh:
        jdict = json.load(fh)
    jdict[0]["version"] = new_version
    homepage_url = jdict[0]["homepageURL"]
    package = homepage_url.split("/")[-1]
    if package == "":
        package = homepage_url.split("/")[-2]
    download_url = f"{homepage_url}/-/archive/{new_version}/{package}-{new_version}.zip"
    disclaimer_url = f"{homepage_url}/-/raw/{new_version}/DISCLAIMER.md"
    jdict[0]["downloadURL"] = download_url
    jdict[0]["disclaimerURL"] = disclaimer_url
    jdict[0]["date"]["metadataLastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    if status is not None:
        jdict[0]["status"] = status
    with open(jsonfile, "wt") as fh:
        json.dump(jdict, fh)


def validate_tag(new_version):
    if new_version != "rev":
        if re.match(VALID_VERSION_PAT, new_version) is None:
            msg = (
                f"{new_version} is not a valid semantic version. "
                "See https://semver.org/ for help"
            )

            return (False, msg)
    return (True, f"{new_version} is a validated semantic version.")


def checkout_branch(new_version, main_branch, dry_run):
    new_branch = f"new_tag_{new_version}"
    checkout_cmd = f"git checkout -b {new_branch} {main_branch}"
    msg = f">>{checkout_cmd}"
    if not dry_run:
        res, stdout, stderr = get_command_output(checkout_cmd)
        if not res:
            msg = f"{checkout_cmd} failed: \n'{stdout}'\n'{stderr}'"
            return (False, msg)
        msg = f"{checkout_cmd} succeeded."
    return (True, new_branch, msg)


def modify_files(repofolder, repo_version, old_version, new_version, status, dry_run):
    # modify build files (setup.cfg or pyproject.toml)
    files_modified = []
    msg = f"Updating {old_version} to {new_version} in build system file.\n"
    if not dry_run:
        repo_version.update_version(new_version)
        files_modified += repo_version.get_files_modified()

    # modify code.json
    jsonfile = repofolder / "code.json"
    if jsonfile.exists():
        msg += f"Modifying version and other metadata in {jsonfile}."
        if not dry_run:
            update_json_file(jsonfile, new_version, status)
            files_modified.append(jsonfile)
    return (True, msg, files_modified)


def commit_changes(new_version, files_modified, new_branch, dry_run):
    commit_cmd = f"git commit -am'Tagging a new version: {new_version}'"
    msg = f">>{commit_cmd}"
    if not dry_run:
        res, stdout, stderr = get_command_output(commit_cmd)
        if not res:
            msg = f"Commit failed: \n'{stdout}'\n'{stderr}'. Undoing checkout. "
            for file in files_modified:
                # checkout file
                checkout_cmd = f"git checkout {file}"
                res, stdout, stderr = get_command_output(checkout_cmd)
                if not res:
                    msg += f"Failed to run {checkout_cmd}. "

            # delete new branch
            delete_cmd = f"git branch -d {new_branch}"
            res, stdout, stderr = get_command_output(delete_cmd)
            if not res:
                msg += f"Failed to run {delete_cmd}. "
            return (False, msg)
        msg = f"Changes committed to {new_branch}."
    return (True, msg)


def push_changes(new_branch, dry_run):
    push_cmd = f"git push origin {new_branch}"
    msg = f">>{push_cmd}"
    if not dry_run:
        res, stdout, stderr = get_command_output(push_cmd)
        if not res:
            msg = f"Failed to run {push_cmd}.\n'{stdout}'\n'{stderr}'."
            return (False, msg)
        msg = "Changes pushed to origin."
        return (True, msg)
    return (True, msg)


def create_tag(new_version, comment, dry_run):
    # now run git tag and push up
    tag_cmd = f"git tag -a {new_version} -m '{comment}'"
    msg = f">>{tag_cmd}."
    if not dry_run:
        res, stdout, stderr = get_command_output(tag_cmd)
        if not res:
            msg = f"Failed to run {tag_cmd}.\n'{stdout}'\n'{stderr}'."
            return (False, msg)
        msg = f"git tag command '{tag_cmd} successfully run."
        return (True, msg)
    return (True, msg)


def push_tag(new_version, dry_run):
    push_tag_cmd = f"git push origin {new_version}"
    msg = f">>{push_tag_cmd}"
    if not dry_run:
        res, stdout, stderr = get_command_output(push_tag_cmd)
        if not res:
            msg = "Failed to run {push_tag_cmd}.\n'{stdout}'\n'{stderr}'."
            return (False, msg)
        msg = (
            "git tag successfully pushed to origin. You will likely need "
            "to navigate to your origin in the browser to manually start a merge "
            "request for this new tag."
        )
        return (True, msg)
    return (True, msg)


def main():
    desc = """Update software version, code.json, git tag for current repository.

Note: The directory chosen must be a valid git repository.

This program will perform the following actions:

 - Update code version string in:
     - setuptools setup.cfg file
     - setuptools pyproject.toml file
     - poetry pyproject.toml file
     - USGS software code.json file
 - Update other metadata in code.json, including:
     - downloadURL
     - repositoryURL
     - disclaimerURL
     - metadataLastUpdated
     - (optionally) status ("Development", "Alpha", "Production", etc.)
 - Commit the above changes via git
 - Create a tag
 - Push the tag and changes to git "origin" remote.

 Users will likely need to go to the repository URL and manually create a Merge
 Request for these commits.
    """
    parser = argparse.ArgumentParser(description=desc, formatter_class=RepoFormatter)
    taghelp = (
        "This can be either 'rev' or a version string. "
        "Non-semantic version strings (see https://semver.org/) "
        "will cause an error"
    )
    parser.add_argument("tag", help=taghelp)
    parser.add_argument("comment", help="Provide a comment to git tag")
    parser.add_argument(
        "-s",
        "--status",
        choices=[
            "Ideation",
            "Development",
            "Alpha",
            "Beta",
            "Release Candidate",
            "Production",
            "Archival",
        ],
        default=None,
        help="Set status field in code.json. Default is to not change that value",
    )
    parser.add_argument(
        "-r",
        "--repository",
        help="Path to repository (default current directory)",
        default=pathlib.Path.cwd(),
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        default=False,
        help="Print out actions that *would* be taken.",
    )
    args = parser.parse_args()

    # make sure target directory is a valid git repository
    current_folder = pathlib.Path.cwd()
    repofolder = pathlib.Path(args.repository)
    if not (repofolder / ".git").exists():
        print(f"{repofolder} does not appear to be a valid git repository. Exiting.")
        sys.exit(1)

    try:
        # change to repository directory
        os.chdir(repofolder)

        # get the name of the main/master branch
        main_branch = get_main_branch()
        if main_branch is None:
            print(f"{repofolder} has no main/master branch. Exiting.")
            sys.exit(1)

        # make sure this repo is using setuptools or poetry
        try:
            repo_version = RepoVersion(repofolder)
            old_version = repo_version.get_version()
            if old_version is None:
                raise Exception(f"No valid version found for {repofolder}")
        except Exception as e:
            print(f"Error: '{str(e)}. Exiting.")
            sys.exit(1)
        print(f"Current version of package is {old_version}")

        # validate new tag
        new_version = args.tag
        if args.tag != "rev":
            result, msg = validate_tag(new_version)
            print(msg)
            if not result:
                sys.exit(1)
        else:
            new_version = increment_minor(old_version)

        # now checkout a new branch, commit these changes, and push them
        result, new_branch, msg = checkout_branch(
            new_version, main_branch, args.dry_run
        )
        print(msg)
        if not result:
            sys.exit(1)

        # modify build files (setup.cfg or pyproject.toml)
        result, msg, files_modified = modify_files(
            repofolder,
            repo_version,
            old_version,
            new_version,
            args.status,
            args.dry_run,
        )
        print(msg)
        if not result:
            sys.exit(1)

        # now commit the changes to build files
        result, msg = commit_changes(
            new_version, files_modified, new_branch, args.dry_run
        )
        print(msg)
        if not result:
            sys.exit(1)

        # push the changes
        result, msg = push_changes(new_branch, args.dry_run)
        print(msg)
        if not result:
            sys.exit(1)

        # now run git tag and push up
        result, msg = create_tag(new_version, args.comment, args.dry_run)
        print(msg)
        if not result:
            sys.exit(1)

        # now push up tag (should cause deploy step in gitlab CI)
        result, msg = push_tag(new_version, args.dry_run)
        print(msg)
        if not result:
            sys.exit(0)
    finally:
        os.chdir(current_folder)


if __name__ == "__main__":
    main()
