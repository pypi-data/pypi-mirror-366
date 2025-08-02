"""
main.py module

This module provides the functionality for the acmc command line interface
"""

import argparse
import logging
from pathlib import Path

import acmc
from acmc import trud, omop, phen, parse, logging_config as lc


DEFAULT_WORKSPACE_PATH = Path("./workspace")
"""Default phenotype workspace path"""


def _trud_install(args: argparse.Namespace):
    """Handle the `trud install` command."""
    trud.install()


def _omop_install(args: argparse.Namespace):
    """Handle the `omop install` command."""
    omop.install(args.omop_zip_file, args.version)


def _omop_clear(args: argparse.Namespace):
    """Handle the `omop clear` command."""
    omop.clear(omop.DB_PATH)


def _omop_delete(args: argparse.Namespace):
    """Handle the `omop delete` command."""
    omop.delete(omop.DB_PATH)


def _phen_init(args: argparse.Namespace):
    """Handle the `phen init` command."""
    phen.init(args.phen_dir, args.remote_url)


def _phen_fork(args: argparse.Namespace):
    """Handle the `phen fork` command."""
    phen.fork(
        args.phen_dir,
        args.upstream_url,
        args.upstream_version,
        new_origin_url=args.remote_url,
    )


def _phen_validate(args: argparse.Namespace):
    """Handle the `phen validate` command."""
    phen.validate(args.phen_dir)


def _phen_map(args: argparse.Namespace):
    """Handle the `phen map` command."""
    phen.map(
        args.phen_dir,
        args.target_coding,
        args.not_translate,
        args.no_metadata,
        args.do_reverse_translate,
    )


def _phen_export(args: argparse.Namespace):
    """Handle the `phen copy` command."""
    phen.export(args.phen_dir, args.version)


def _phen_publish(args: argparse.Namespace):
    """Handle the `phen publish` command."""
    phen.publish(args.phen_dir, args.msg, args.remote_url, args.increment)


def _phen_copy(args: argparse.Namespace):
    """Handle the `phen copy` command."""
    phen.copy(args.phen_dir, args.target_dir, args.version)


def _phen_diff(args: argparse.Namespace):
    """Handle the `phen diff` command."""
    phen.diff(
        args.phen_dir,
        args.version,
        args.old_phen_dir,
        args.old_version,
        args.not_check_config,
        args.output_changed_concepts,
    )


def main():
    parser = argparse.ArgumentParser(description="ACMC command-line tool")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--version", action="version", version=f"acmc {acmc.__version__}"
    )

    # Top-level commands
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    ### TRUD Command ###
    trud_parser = subparsers.add_parser("trud", help="TRUD commands")
    trud_subparsers = trud_parser.add_subparsers(
        dest="subcommand", required=True, help="TRUD subcommands"
    )

    # trud install
    trud_install_parser = trud_subparsers.add_parser(
        "install", help="Install TRUD components"
    )
    trud_install_parser.set_defaults(func=_trud_install)

    ### OMOP Command ###
    omop_parser = subparsers.add_parser("omop", help="OMOP commands")
    omop_subparsers = omop_parser.add_subparsers(
        dest="subcommand", required=True, help="OMOP subcommands"
    )

    # omop install
    omop_install_parser = omop_subparsers.add_parser(
        "install", help="Install OMOP codes within database"
    )
    omop_install_parser.add_argument(
        "-f", "--omop-zip-file", required=True, help="Path to downloaded OMOP zip file"
    )
    omop_install_parser.add_argument(
        "-v", "--version", required=True, help="OMOP vocabularies release version"
    )
    omop_install_parser.set_defaults(func=_omop_install)

    # omop clear
    omop_clear_parser = omop_subparsers.add_parser(
        "clear", help="Clear OMOP data from database"
    )
    omop_clear_parser.set_defaults(func=_omop_clear)

    # omop delete
    omop_delete_parser = omop_subparsers.add_parser(
        "delete", help="Delete OMOP database"
    )
    omop_delete_parser.set_defaults(func=_omop_delete)

    ### PHEN Command ###
    phen_parser = subparsers.add_parser("phen", help="Phen commands")
    phen_subparsers = phen_parser.add_subparsers(
        dest="subcommand", required=True, help="Phen subcommands"
    )

    # phen init
    phen_init_parser = phen_subparsers.add_parser(
        "init", help="Initiatise phenotype directory"
    )
    phen_init_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_init_parser.add_argument(
        "-r",
        "--remote_url",
        help="(Optional) URL to repository where the phenotype will be published.",
    )
    phen_init_parser.set_defaults(func=_phen_init)

    # phen fork
    phen_fork_parser = phen_subparsers.add_parser(
        "fork", help="Fork an existing phenotype"
    )
    phen_fork_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_fork_parser.add_argument(
        "-r",
        "--remote_url",
        help="(Optional) URL to repository where the forked phenotype will be published.",
    )
    phen_fork_parser.add_argument(
        "-u",
        "--upstream-url",
        required=True,
        help="(Required) URL to the phenotype repository to fork.",
    )
    phen_fork_parser.add_argument(
        "-v",
        "--upstream-version",
        required=True,
        help="(Required) Phenotype version to fork.",
    )
    phen_fork_parser.set_defaults(func=_phen_fork)

    # phen validate
    phen_validate_parser = phen_subparsers.add_parser(
        "validate", help="Validate phenotype configuration"
    )
    phen_validate_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_validate_parser.set_defaults(func=_phen_validate)

    # phen map
    phen_map_parser = phen_subparsers.add_parser("map", help="Process phen mapping")
    phen_map_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_map_parser.add_argument(
        "-t",
        "--target-coding",
        choices=parse.SUPPORTED_CODE_TYPES,
        help=f"Specify the target coding {parse.SUPPORTED_CODE_TYPES}",
    )
    phen_map_parser.add_argument(
        "--not-translate",
        action="store_true",
        default=False,
        help="(Optional) Prevent any phenotype translation using NHS TRUD vocabularies.",
    )
    phen_map_parser.add_argument(
        "--no-metadata",
        action="store_true",
        default=False,
        help="(Optional) Prevent copying of metadata columns to output.",
    )
    phen_map_parser.add_argument(
        "--do-reverse-translate",
        action="store_true",
        default=False,
        help="(Optional) Enable reversing one directional mappings. WARNING goes against NHS TRUD guidelines.",
    )
    phen_map_parser.set_defaults(func=_phen_map)

    # phen export
    phen_export_parser = phen_subparsers.add_parser(
        "export", help="Export phen to OMOP database"
    )
    phen_export_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_export_parser.add_argument(
        "-v",
        "--version",
        type=str,
        default="latest",
        help="Phenotype version to export, defaults to the latest version",
    )
    phen_export_parser.set_defaults(func=_phen_export)

    # phen publish
    phen_publish_parser = phen_subparsers.add_parser(
        "publish", help="Publish phenotype configuration"
    )
    phen_publish_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_publish_parser.add_argument(
        "-i",
        "--increment",
        type=str,
        default=phen.DEFAULT_VERSION_INC,
        choices=phen.SEMANTIC_VERSION_TYPES,
        help=f"Version increment: {phen.SEMANTIC_VERSION_TYPES}, default is {phen.DEFAULT_VERSION_INC} increment",
    )
    phen_publish_parser.add_argument(
        "-m", "--msg", help="Message to include with the published version"
    )
    phen_publish_parser.add_argument(
        "-r", "--remote_url", help="URL to remote git repository"
    )
    phen_publish_parser.set_defaults(func=_phen_publish)

    # phen copy
    phen_copy_parser = phen_subparsers.add_parser(
        "copy", help="Publish phenotype configuration"
    )
    phen_copy_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_copy_parser.add_argument(
        "-td",
        "--target-dir",
        type=str,
        default=str(DEFAULT_WORKSPACE_PATH.resolve()),
        help="Target directory for the copy",
    )
    phen_copy_parser.add_argument(
        "-v",
        "--version",
        type=str,
        default="latest",
        help="Phenotype version to copy, defaults to the latest version",
    )
    phen_copy_parser.set_defaults(func=_phen_copy)

    # phen diff
    phen_diff_parser = phen_subparsers.add_parser(
        "diff", help="Publish phenotype configuration"
    )
    phen_diff_parser.add_argument(
        "-d",
        "--phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="(Optional) Local phenotype workspace directory (default is ./workspace/phen).",
    )
    phen_diff_parser.add_argument(
        "-v",
        "--version",
        default="latest",
        help="Phenotype version to compare with an old version, defaults to the HEAD of the workspace directory",
    )
    phen_diff_parser.add_argument(
        "-od",
        "--old-phen-dir",
        type=str,
        default=str(phen.DEFAULT_PHEN_PATH.resolve()),
        help="Directory for the old phenotype version, defaults to workspace directory",
    )
    phen_diff_parser.add_argument(
        "-ov",
        "--old-version",
        required=True,
        help="Old phenotype version to compare with the changed version",
    )
    phen_diff_parser.add_argument(
        "--not-check-config",
        action="store_true",
        default=False,
        help="(Optional) Prevent loading and comparing config file, in the case where one does not exist",
    )
    phen_diff_parser.add_argument(
        "--output-changed-concepts",
        action="store_true",
        default=False,
        help="(Optional) Output a table of concepts that have been added or removed to csv",
    )
    phen_diff_parser.set_defaults(func=_phen_diff)

    # Parse arguments
    args = parser.parse_args()

    # setup logging
    if args.debug:
        lc.set_log_level(logging.DEBUG)

    # Call the function associated with the command
    args.func(args)


if __name__ == "__main__":
    main()
