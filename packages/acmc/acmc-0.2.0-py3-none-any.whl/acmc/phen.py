"""
phenotype.py module

This module provides functionality for managing phenotypes.
"""

import argparse
import pandas as pd
import numpy as np
import json
import os
import sqlite3
import sys
import shutil
import time
import git
import re
import logging
import requests
import yaml
import semver
from git import Repo
from cerberus import Validator  # type: ignore
from deepdiff import DeepDiff
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from typing import Tuple, Set, Any
import acmc
from acmc import trud, omop, parse, util, logging_config as lc

# set up logging
_logger = lc.setup_logger()

pd.set_option("mode.chained_assignment", None)

PHEN_DIR = "phen"
"""Default phenotype directory name"""

DEFAULT_PHEN_PATH = Path("./workspace") / PHEN_DIR
"""Default phenotype directory path"""

CONCEPTS_DIR = "concepts"
"""Default concepts directory name"""

MAP_DIR = "map"
"""Default map directory name"""

CONCEPT_SET_DIR = "concept-sets"
"""Default concept set directory name"""

CSV_PATH = Path(CONCEPT_SET_DIR) / "csv"
"""Default CSV concept set directory path"""

OMOP_PATH = Path(CONCEPT_SET_DIR) / "omop"
"""Default OMOP concept set directory path"""

DEFAULT_PHEN_DIR_LIST = [CONCEPTS_DIR, MAP_DIR, CONCEPT_SET_DIR]
"""List of default phenotype directories"""

CONFIG_FILE = "config.yml"
"""Default configuration filename"""

VOCAB_VERSION_FILE = "vocab_version.yml"
"""Default vocabulary version filename"""

SEMANTIC_VERSION_TYPES = ["major", "minor", "patch"]
"""List of semantic version increment types"""

DEFAULT_VERSION_INC = "patch"
"""Default semantic version increment type"""

DEFAULT_GIT_BRANCH = "main"
"""Default phenotype repo branch name"""

SPLIT_COL_ACTION = "split_col"
"""Split column preprocessing action type"""

CODES_COL_ACTION = "codes_col"
"""Codes column preprocessing action type"""

DIVIDE_COL_ACTION = "divide_col"
"""Divide column preprocessing action type"""

COL_ACTIONS = [SPLIT_COL_ACTION, CODES_COL_ACTION, DIVIDE_COL_ACTION]
"""List of column preprocessing action types"""

CODE_FILE_TYPES = [".xlsx", ".xls", ".csv"]
"""List of supported source concept coding list file types"""

# config.yaml schema
CONFIG_SCHEMA = {
    "phenotype": {
        "type": "dict",
        "required": True,
        "schema": {
            "version": {
                "type": "string",
                "required": True,
                "regex": r"^\d+\.\d+\.\d+$",  # Enforces 'vN.N.N' format
            },
            "omop": {
                "type": "dict",
                "required": True,
                "schema": {
                    "vocabulary_id": {"type": "string", "required": True},
                    "vocabulary_name": {"type": "string", "required": True},
                    "vocabulary_reference": {
                        "type": "string",
                        "required": True,
                        "regex": r"^https?://.*",  # Ensures it's a URL
                    },
                },
            },
            "map": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "allowed": list(
                        parse.SUPPORTED_CODE_TYPES
                    ),  # Ensure only predefined values are allowed
                },
            },
            "concept_sets": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {"type": "string", "required": True},
                        "files": {
                            "type": "list",
                            "required": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "path": {"type": "string", "required": True},
                                    "columns": {"type": "dict", "required": True},
                                    "category": {
                                        "type": "string"
                                    },  # Optional but must be string if present
                                    "actions": {
                                        "type": "dict",
                                        "schema": {
                                            "divide_col": {"type": "string"},
                                            "split_col": {"type": "string"},
                                            "codes_col": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                        "metadata": {"type": "dict", "required": False},
                    },
                },
            },
        },
    }
}
"""Phenotype config.yml schema definition"""


class PhenValidationException(Exception):
    """Custom exception class raised when validation errors in phenotype configuration file"""

    def __init__(self, message, validation_errors=None):
        super().__init__(message)
        self.validation_errors = validation_errors


def _construct_git_url(remote_url: str):
    """Constructs a git url for github or gitlab including a PAT token environment variable"""
    # check the url
    parsed_url = urlparse(remote_url)

    # if github in the URL otherwise assume it's gitlab, if we want to use others such as codeberg we'd
    # need to update this function if the URL scheme is different.
    if "github.com" in parsed_url.netloc:
        # get GitHub PAT from environment variable
        auth = os.getenv("ACMC_GITHUB_PAT")
        if not auth:
            raise ValueError(
                "GitHub PAT not found. Set the ACMC_GITHUB_PAT environment variable."
            )
    else:
        # get GitLab PAT from environment variable
        auth = os.getenv("ACMC_GITLAB_PAT")
        if not auth:
            raise ValueError(
                "GitLab PAT not found. Set the ACMC_GITLAB_PAT environment variable."
            )
        auth = f"oauth2:{auth}"

    # Construct the new URL with credentials
    new_netloc = f"{auth}@{parsed_url.netloc}"
    return urlunparse(
        (
            parsed_url.scheme,
            new_netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )


def _create_empty_git_dir(path: Path):
    """Creates a directory with a .gitkeep file so that it's tracked in git"""
    path.mkdir(exist_ok=True)
    keep_path = path / ".gitkeep"
    keep_path.touch(exist_ok=True)


def _check_delete_dir(path: Path, msg: str) -> bool:
    """Checks on the command line if a user wants to delete a directory

    Args:
        path (Path): path of the directory to be deleted
        msg (str): message to be displayed to the user

    Returns:
        Boolean: True if deleted
    """
    deleted = False

    user_input = input(f"{msg}").strip().lower()
    if user_input in ["yes", "y"]:
        shutil.rmtree(path)
        deleted = True
    else:
        _logger.info("Directory was not deleted.")

    return deleted


def init(phen_dir: str, remote_url: str):
    """Initial phenotype directory as git repo with standard structure"""
    _logger.info(f"Initialising Phenotype in directory: {phen_dir}")
    phen_path = Path(phen_dir)

    # check if directory already exists and ask user if they want to recreate it
    if (
        phen_path.exists() and phen_path.is_dir()
    ):  # Check if it exists and is a directory
        configure = _check_delete_dir(
            phen_path,
            f"The phen directory already exists. Do you want to reinitialise? (yes/no): ",
        )
    else:
        configure = True

    if not configure:
        _logger.info(f"Exiting, phenotype not initiatised")
        return

    # Initialise repo from local or remote
    repo: Repo

    # if remote then clone the repo otherwise init a local repo
    if remote_url != None:
        # add PAT token to the URL
        git_url = _construct_git_url(remote_url)

        # clone the repo
        git_cmd = git.cmd.Git()
        git_cmd.clone(git_url, phen_path)

        # open repo
        repo = Repo(phen_path)
        # check if there are any commits (new repo has no commits)
        if (
            len(repo.branches) == 0 or repo.head.is_detached
        ):  # Handle detached HEAD (e.g., after init)
            _logger.debug("The phen repository has no commits yet.")
            commit_count = 0
        else:
            # Get the total number of commits in the default branch
            commit_count = sum(1 for _ in repo.iter_commits())
            _logger.debug(f"Repo has previous commits: {commit_count}")
    else:
        # local repo, create the directories and init
        phen_path.mkdir(parents=True, exist_ok=True)
        _logger.debug(f"Phen directory '{phen_path}' has been created.")
        repo = git.Repo.init(phen_path)
        commit_count = 0

    phen_path = phen_path.resolve()
    # initialise empty repos
    if commit_count == 0:
        # create initial commit
        initial_file_path = phen_path / "README.md"
        with open(initial_file_path, "w") as file:
            file.write(
                "# Initial commit\nThis is the first commit in the phen repository.\n"
            )
        repo.index.add([initial_file_path])
        repo.index.commit("Initial commit")
        commit_count = 1

    # Checkout the phens default branch, creating it if it does not exist
    if DEFAULT_GIT_BRANCH in repo.branches:
        main_branch = repo.heads[DEFAULT_GIT_BRANCH]
        main_branch.checkout()
    else:
        main_branch = repo.create_head(DEFAULT_GIT_BRANCH)
        main_branch.checkout()

    # if the phen path does not contain the config file then initialise the phen type
    config_path = phen_path / CONFIG_FILE
    if config_path.exists():
        _logger.debug(f"Phenotype configuration files already exist")
        return

    _logger.info("Creating phen directory structure and config files")
    for d in DEFAULT_PHEN_DIR_LIST:
        _create_empty_git_dir(phen_path / d)

    # create empty phen config file
    config = {
        "phenotype": {
            "version": "0.0.0",
            "omop": {
                "vocabulary_id": "",
                "vocabulary_name": "",
                "vocabulary_reference": "",
            },
            "translate": [],
            "concept_sets": [],
        }
    }

    with open(phen_path / CONFIG_FILE, "w") as file:
        yaml.dump(
            config,
            file,
            Dumper=util.QuotedDumper,
            default_flow_style=False,
            sort_keys=False,
            default_style='"',
        )

    # add git ignore
    ignore_content = """# Ignore SQLite database files
*.db
*.sqlite3
 
# Ignore SQLite journal and metadata files
*.db-journal
*.sqlite3-journal

# python
.ipynb_checkpoints
 """
    ignore_path = phen_path / ".gitignore"
    with open(ignore_path, "w") as file:
        file.write(ignore_content)

    # add to git repo and commit
    for d in DEFAULT_PHEN_DIR_LIST:
        repo.git.add(phen_path / d)
    repo.git.add(all=True)
    repo.index.commit("initialised the phen git repo.")

    _logger.info(f"Phenotype initialised successfully")


def fork(phen_dir: str, upstream_url: str, upstream_version: str, new_origin_url: str):
    """Forks an upstream phenotype in a remote repo at a specific version to a local director, and optionally sets to a new remote origin"

    Args:
        phen_dir (str): local directory path where the upstream repo is to be cloned
        upstream_url (str): url to the upstream repo
        upstream_version (str): version in the upstream repo to clone
        new_origin_url (str, optional): url of the remote repo to set as the new origin. Defaults to None.

    Raises:
        ValueError: if the specified version is not in the upstream repo
        ValueError: if the upstream repo is not a valid phenotype repo
        ValueError: if there's any other problems with Git
    """
    _logger.info(
        f"Forking upstream repo {upstream_url} {upstream_version} into directory: {phen_dir}"
    )

    phen_path = Path(phen_dir)
    # check if directory already exists and ask user if they want to recreate it
    if (
        phen_path.exists() and phen_path.is_dir()
    ):  # Check if it exists and is a directory
        configure = _check_delete_dir(
            phen_path,
            f"The phen directory already exists. Do you want to reinitialise? (yes/no): ",
        )
    else:
        configure = True

    if not configure:
        _logger.info(f"Exiting, phenotype not initiatised")
        return

    try:
        # Clone repo
        git_url = _construct_git_url(upstream_url)
        repo = git.Repo.clone_from(git_url, phen_path)

        # Fetch all branches and tags
        repo.remotes.origin.fetch()

        # Check if the version exists
        available_refs = [ref.name.split("/")[-1] for ref in repo.references]
        if upstream_version not in available_refs:
            raise ValueError(
                f"Version '{upstream_version}' not found in the repository: {upstream_url}."
            )

        # Checkout the specified version
        repo.git.checkout(upstream_version)
        main_branch = repo.heads[DEFAULT_GIT_BRANCH]
        main_branch.checkout()

        # Check if 'config.yml' exists in the root directory
        config_path = phen_path / "config.yml"
        if not os.path.isfile(config_path):
            raise ValueError(
                f"The forked repository is not a valid ACMC repo because 'config.yml' is missing in the root directory."
            )

        # Validate the phenotype is compatible with the acmc tool
        validate(str(phen_path.resolve()))

        # Delete each tag locally
        tags = repo.tags
        for tag in tags:
            repo.delete_tag(tag)
            _logger.debug(f"Deleted tags from forked repo: {tag}")

        # Add upstream remote
        repo.create_remote("upstream", upstream_url)
        remote = repo.remotes["origin"]
        repo.delete_remote(remote)  # Remove existing origin

        # Optionally set a new origin remote
        if new_origin_url:
            git_url = _construct_git_url(new_origin_url)
            repo.create_remote("origin", git_url)
            repo.git.push("--set-upstream", "origin", "main")

        _logger.info(f"Repository forked successfully at {phen_path}")
        _logger.info(f"Upstream set to {upstream_url}")
        if new_origin_url:
            _logger.info(f"Origin set to {new_origin_url}")

    except Exception as e:
        if phen_path.exists():
            shutil.rmtree(phen_path)
        raise ValueError(f"Error occurred during repository fork: {str(e)}")


def validate(phen_dir: str):
    """Validates the phenotype directory is a git repo with standard structure"""
    _logger.info(f"Validating phenotype: {phen_dir}")
    phen_path = Path(phen_dir)
    if not phen_path.is_dir():
        raise NotADirectoryError(
            f"Error: '{str(phen_path.resolve())}' is not a directory"
        )

    config_path = phen_path / CONFIG_FILE
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Error: phen configuration file '{config_path}' does not exist."
        )

    concepts_path = phen_path / CONCEPTS_DIR
    if not concepts_path.is_dir():
        raise FileNotFoundError(
            f"Error: source concepts directory {concepts_path} does not exist."
        )

    # Calidate the directory is a git repo
    try:
        git.Repo(phen_path)
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        raise Exception(f"Phen directory {phen_path} is not a git repo")

    # Load configuration File
    if config_path.suffix == ".yml":
        try:
            with config_path.open("r") as file:
                phenotype = yaml.safe_load(file)

            validator = Validator(CONFIG_SCHEMA)
            if validator.validate(phenotype):
                _logger.debug("YAML structure is valid.")
            else:
                _logger.error(f"YAML structure validation failed: {validator.errors}")
                raise Exception(f"YAML structure validation failed: {validator.errors}")
        except yaml.YAMLError as e:
            _logger.error(f"YAML syntax error: {e}")
            raise e
    else:
        raise Exception(
            f"Unsupported configuration filetype: {str(config_path.resolve())}"
        )

    # initiatise
    validation_errors = []
    phenotype = phenotype["phenotype"]
    code_types = parse.CodeTypeParser().code_types

    # check the version number is of the format vn.n.n
    match = re.match(r"(\d+\.\d+\.\d+)", phenotype["version"])
    if not match:
        validation_errors.append(
            f"Invalid version format in configuration file: {phenotype['version']}"
        )

    # create a list of all the concept set names defined in the concept set configuration
    concept_set_names = []
    for item in phenotype["concept_sets"]:
        if item["name"] in concept_set_names:
            validation_errors.append(
                f"Duplicate concept set defined in concept sets {item['name'] }"
            )
        else:
            concept_set_names.append(item["name"])

    # check codes definition
    for files in phenotype["concept_sets"]:
        for item in files["files"]:
            # check concepte code file exists
            concept_code_file_path = concepts_path / item["path"]
            if not concept_code_file_path.exists():
                validation_errors.append(
                    f"Coding file {str(concept_code_file_path.resolve())} does not exist"
                )

            # check concepte code file is not empty
            if concept_code_file_path.stat().st_size == 0:
                validation_errors.append(
                    f"Coding file {str(concept_code_file_path.resolve())} is an empty file"
                )

            # check code file type is supported
            if concept_code_file_path.suffix not in CODE_FILE_TYPES:
                raise ValueError(
                    f"Unsupported filetype {concept_code_file_path.suffix}, only support csv, xlsx, xls code file types"
                )

            # check columns specified are a supported medical coding type
            for column in item["columns"]:
                if column not in code_types:
                    validation_errors.append(
                        f"Column type {column} for file {concept_code_file_path} is not supported"
                    )

            # check the actions are supported
            if "actions" in item:
                for action in item["actions"]:
                    if action not in COL_ACTIONS:
                        validation_errors.append(f"Action {action} is not supported")

    if len(validation_errors) > 0:
        _logger.error(validation_errors)
        raise PhenValidationException(
            f"Configuration file {str(config_path.resolve())} failed validation",
            validation_errors,
        )

    _logger.info(f"Phenotype validated successfully")


def _read_table_file(path: Path, excel_sheet: str = ""):
    """
    Load Code List File
    """

    path = path.resolve()
    if path.suffix == ".csv":
        df = pd.read_csv(path, dtype=str)
    elif path.suffix == ".xlsx" or path.suffix == ".xls":
        if excel_sheet != "":
            df = pd.read_excel(path, sheet_name=excel_sheet, dtype=str)
        else:
            df = pd.read_excel(path, dtype=str)
    elif path.suffix == ".dta":
        df = pd.read_stata(path)
    else:
        raise ValueError(
            f"Unsupported filetype {path.suffix}, only support{CODE_FILE_TYPES} code file types"
        )

    return df


def _process_actions(df: pd.DataFrame, concept_set: dict) -> pd.DataFrame:
    # Perform Structural Changes to file before preprocessing
    _logger.debug("Processing file structural actions")
    if (
        "actions" in concept_set
        and "split_col" in concept_set["actions"]
        and "codes_col" in concept_set["actions"]
    ):
        split_col = concept_set["actions"]["split_col"]
        codes_col = concept_set["actions"]["codes_col"]
        _logger.debug(
            "Action: Splitting",
            split_col,
            "column into:",
            df[split_col].unique(),
        )
        codes = df[codes_col]
        oh = pd.get_dummies(df[split_col], dtype=bool)  # one hot encode
        oh = oh.where((oh != True), codes, axis=0)  # fill in 1s with codes
        oh[oh == False] = np.nan  # replace 0s with None
        df = pd.concat([df, oh], axis=1)  # merge in new columns

    return df


def _preprocess_source_concepts(
    df: pd.DataFrame, concept_set: dict, code_file_path: Path
) -> Tuple[pd.DataFrame, list]:
    """Perform QA Checks on columns individually and append to df"""
    out = pd.DataFrame([])  # create output df to append to
    code_errors = []  # list of errors from processing

    # remove unnamed columns due to extra commas, missing headers, or incorrect parsing
    df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])

    # Preprocess codes
    code_types = parse.CodeTypeParser().code_types
    for code_type in concept_set["columns"]:
        parser = code_types[code_type]
        _logger.info(f"Processing {code_type} codes for {code_file_path}")

        # get codes by column name
        source_col_name = concept_set["columns"][code_type]
        codes = df[source_col_name].dropna()
        codes = codes.astype(str)  # convert to string
        codes = codes.str.strip()  # remove excess spaces

        # process codes, validating them using parser and returning the errors
        codes, errors = parser.process(codes, code_file_path)
        if len(errors) > 0:
            code_errors.extend(errors)
            _logger.warning(f"Codes validation failed with {len(errors)} errors")

        # add processed codes to df
        new_col_name = f"{source_col_name}_SOURCE"
        df = df.rename(columns={source_col_name: new_col_name})
        process_codes = pd.DataFrame({code_type: codes}).join(df)
        out = pd.concat(
            [out, process_codes],
            ignore_index=True,
        )

    _logger.debug(out.head())

    return out, code_errors


# Translate Df with multiple codes into single code type Series
def translate_codes(
    source_df: pd.DataFrame,
    target_code_type: str,
    concept_name: str,
    not_translate: bool,
    do_reverse_translate: bool,
) -> pd.DataFrame:
    """Translates each source code type the source coding list into a target type and returns all conversions as a concept set"""

    # codes = pd.DataFrame([], dtype=str)
    codes = pd.DataFrame(
        columns=["SOURCE_CONCEPT", "SOURCE_CONCEPT_TYPE", "CONCEPT"], dtype="string"
    )
    # Convert codes to target type
    _logger.info(f"Converting to target code type {target_code_type}")

    for source_code_type in source_df.columns:
        # if target code type is the same as thet source code type, no translation, just appending source as target
        if source_code_type == target_code_type:
            copy_df = pd.DataFrame(
                {
                    "SOURCE_CONCEPT": source_df[source_code_type],
                    "SOURCE_CONCEPT_TYPE": source_code_type,
                    "CONCEPT": source_df[source_code_type],
                }
            )
            codes = pd.concat([codes, copy_df])
            _logger.debug(
                f"Target code type {target_code_type} is the same as source code type {len(source_df)}, copying codes rather than translating"
            )
        elif not not_translate:
            # get the translation filename using source to target code types
            filename = f"{source_code_type}_to_{target_code_type}.parquet"
            map_path = trud.PROCESSED_PATH / filename

            filename_reversed = f"{target_code_type}_to_{source_code_type}.parquet"
            map_path_reversed = trud.PROCESSED_PATH / filename_reversed

            # do the mapping if it exists
            if map_path.exists():
                codes = _translate_codes(map_path, source_df, source_code_type, codes)
            # otherwise do reverse mapping if enabled and it exists
            elif do_reverse_translate and map_path_reversed.exists():
                codes = _translate_codes(
                    map_path_reversed, source_df, source_code_type, codes, reverse=True
                )
            else:
                _logger.warning(
                    f"No mapping from {source_code_type} to {target_code_type}, file {str(map_path.resolve())} does not exist"
                )

    codes = codes.dropna()  # delete NaNs

    # added concept set type to output if any translations
    if len(codes.index) > 0:
        codes["CONCEPT_SET"] = concept_name
    else:
        _logger.debug(f"No codes converted with target code type {target_code_type}")

    return codes


def _translate_codes(
    map_path, source_df, source_code_type, codes, reverse=False
) -> pd.DataFrame:
    # get mapping
    df_map = pd.read_parquet(map_path)

    # do mapping
    if not (reverse):
        translated_df = pd.merge(source_df[source_code_type], df_map, how="left")
    else:
        translated_df = pd.merge(
            source_df[source_code_type], df_map, how="left"
        )  # output codes from target as reversed

    # normalise the output
    translated_df.columns = pd.Index(["SOURCE_CONCEPT", "CONCEPT"])
    translated_df["SOURCE_CONCEPT_TYPE"] = source_code_type

    # add to list of codes
    codes = pd.concat([codes, translated_df])

    return codes


def _write_code_errors(code_errors: list, code_errors_path: Path):
    err_df = pd.DataFrame(
        [
            {
                "CONCEPT": ", ".join(err.codes[~err.mask].tolist()),
                "VOCABULARY": err.code_type,
                "SOURCE": err.codes_file,
                "CAUSE": err.message,
            }
            for err in code_errors
            if err.mask is not None
        ]
    )

    err_df = err_df.drop_duplicates()  # Remove Duplicates from Error file
    err_df = err_df.sort_values(by=["SOURCE", "VOCABULARY", "CONCEPT"])
    err_df.to_csv(code_errors_path, index=False, mode="w")


def write_vocab_version(phen_path: Path):
    # write the vocab version files

    if not trud.VERSION_PATH.exists():
        raise FileNotFoundError(
            f"TRUD version path {trud.VERSION_PATH} does not exist, please check TRUD is installed"
        )

    if not omop.VERSION_PATH.exists():
        raise FileNotFoundError(
            f"OMOP version path {omop.VERSION_PATH} does not exist, please check OMOP is installed"
        )

    with trud.VERSION_PATH.open("r") as file:
        trud_version = yaml.safe_load(file)

    with omop.VERSION_PATH.open("r") as file:
        omop_version = yaml.safe_load(file)

    # Create the combined YAML structure
    version_data = {
        "versions": {
            "acmc": acmc.__version__,
            "trud": trud_version,
            "omop": omop_version,
        }
    }

    with open(phen_path / VOCAB_VERSION_FILE, "w") as file:
        yaml.dump(
            version_data,
            file,
            Dumper=util.QuotedDumper,
            default_flow_style=False,
            sort_keys=False,
            default_style='"',
        )


def map(
    phen_dir: str,
    target_code_type: str,
    not_translate: bool,
    no_metadata: bool,
    do_reverse_translate: bool,
):
    _logger.info(f"Processing phenotype: {phen_dir}")

    # Validate configuration
    validate(phen_dir)

    # initialise paths
    phen_path = Path(phen_dir)
    config_path = phen_path / CONFIG_FILE

    # load configuration
    with config_path.open("r") as file:
        config = yaml.safe_load(file)
    phenotype = config["phenotype"]

    if len(phenotype["map"]) == 0:
        raise ValueError(f"No map codes defined in the phenotype configuration")

    if target_code_type is not None and target_code_type not in phenotype["map"]:
        raise ValueError(
            f"Target code type {target_code_type} not in phenotype configuration map {phenotype['map']}"
        )

    if target_code_type is not None:
        _map_target_code_type(
            phen_path,
            phenotype,
            target_code_type,
            not_translate,
            no_metadata,
            do_reverse_translate,
        )
    else:
        for t in phenotype["map"]:
            _map_target_code_type(
                phen_path,
                phenotype,
                t,
                not_translate,
                no_metadata,
                do_reverse_translate,
            )

    _logger.info(f"Phenotype processed successfully")


def _map_target_code_type(
    phen_path: Path,
    phenotype: dict,
    target_code_type: str,
    not_translate: bool,
    no_metadata: bool,
    do_reverse_translate: bool,
):
    _logger.debug(f"Target coding format: {target_code_type}")
    concepts_path = phen_path / CONCEPTS_DIR
    # Create output dataframe
    out = pd.DataFrame([])
    code_errors = []

    # Process each folder in codes section
    for files in phenotype["concept_sets"]:
        concept_set_name = files["name"]
        if "metadata" in files:
            concept_set_metadata = files["metadata"]
        else:
            concept_set_metadata = {}
        for concept_set in files["files"]:
            _logger.debug(f"--- {concept_set} ---")

            # Load code file
            codes_file_path = Path(concepts_path / concept_set["path"])
            df = _read_table_file(codes_file_path)

            # process structural actions
            df = _process_actions(df, concept_set)

            # preprocessing and validate of source concepts
            _logger.debug("Processing and validating source concept codes")
            df, errors = _preprocess_source_concepts(
                df,
                concept_set,
                codes_file_path,
            )

            # create df with just the source code columns
            source_column_names = list(concept_set["columns"].keys())
            source_df = df[source_column_names]

            _logger.debug(source_df.columns)
            _logger.debug(source_df.head())

            _logger.debug(
                f"Length of errors from _preprocess_source_concepts {len(errors)}"
            )
            if len(errors) > 0:
                code_errors.extend(errors)
            _logger.debug(f" Length of code_errors {len(code_errors)}")

            # Map source concepts codes to target codes
            # if processing a source coding list with categorical data
            if (
                "actions" in concept_set
                and "divide_col" in concept_set["actions"]
                and len(df) > 0
            ):
                divide_col = concept_set["actions"]["divide_col"]
                _logger.debug(f"Action: Dividing Table by {divide_col}")
                _logger.debug(f"column into: {df[divide_col].unique()}")
                df_grp = df.groupby(divide_col)
                for cat, grp in df_grp:
                    if cat == concept_set["category"]:
                        grp = grp.drop(
                            columns=[divide_col]
                        )  # delete categorical column
                        source_df = grp[source_column_names]
                        trans_out = translate_codes(
                            source_df,
                            target_code_type=target_code_type,
                            concept_name=concept_set_name,
                            not_translate=not_translate,
                            do_reverse_translate=do_reverse_translate,
                        )
                        trans_out = add_metadata(
                            codes=trans_out,
                            metadata=concept_set_metadata,
                            no_metadata=no_metadata,
                        )
                        out = pd.concat([out, trans_out])
            else:
                source_df = df[source_column_names]
                trans_out = translate_codes(
                    source_df,
                    target_code_type=target_code_type,
                    concept_name=concept_set_name,
                    not_translate=not_translate,
                    do_reverse_translate=do_reverse_translate,
                )
                trans_out = add_metadata(
                    codes=trans_out,
                    metadata=concept_set_metadata,
                    no_metadata=no_metadata,
                )
                out = pd.concat([out, trans_out])

    if len(code_errors) > 0:
        _logger.error(f"The map processing has {len(code_errors)} errors")
        error_path = phen_path / MAP_DIR / "errors"
        error_path.mkdir(parents=True, exist_ok=True)
        error_filename = f"{target_code_type}-code-errors.csv"
        _write_code_errors(code_errors, error_path / error_filename)

    # Check there is output from processing
    if len(out.index) == 0:
        _logger.error(f"No output after map processing")
        raise Exception(
            f"No output after map processing, check config {str(phen_path.resolve())}"
        )

    # final processing
    out = out.reset_index(drop=True)
    out = out.drop_duplicates(subset=["CONCEPT_SET", "CONCEPT"])
    out = out.sort_values(by=["CONCEPT_SET", "CONCEPT"])

    # out_count = len(out.index)
    # added metadata
    # Loop over each source_concept_type and perform the left join on all columns apart from source code columns
    # result_list = []
    # for files in phenotype["concept_sets"]:
    #     concept_set_name = files["name"]
    #     for concept_set in files["files"]:
    #         source_column_names = list(concept_set["columns"].keys())
    #         for source_concept_type in source_column_names:
    #             # Filter output based on the current source_concept_type
    #             out_filtered_df = out[out["SOURCE_CONCEPT_TYPE"] == source_concept_type]
    #             filtered_count = len(out_filtered_df.index)

    #             # Remove the source type columns except the current type will leave the metadata and the join
    #             remove_types = [
    #                 type for type in source_column_names if type != source_concept_type
    #             ]
    #             metadata_df = df.drop(columns=remove_types)
    #             metadata_df = metadata_df.rename(
    #                 columns={source_concept_type: "SOURCE_CONCEPT"}
    #             )
    #             metadata_df_count = len(metadata_df.index)

    # Perform the left join with df2 on SOURCE_CONCEPT to add the metadata
    # result = pd.merge(out_filtered_df, metadata_df, how="left", on="SOURCE_CONCEPT")
    # result_count = len(result.index)

    #             _logger.debug(
    #                 f"Adding metadata for {source_concept_type}: out_count {out_count}, filtered_count {filtered_count}, metadata_df_count {metadata_df_count}, result_count {result_count}"
    #             )

    #             # Append the result to the result_list
    #             result_list.append(result)

    # Concatenate all the results into a single DataFrame
    # final_out = pd.concat(result_list, ignore_index=True)
    # final_out = final_out.drop_duplicates(subset=["CONCEPT_SET", "CONCEPT"])
    # _logger.debug(
    #     f"Check metadata processing counts: before {len(out.index)} : after {len(final_out.index)}"
    # )

    # Save output to map directory
    output_filename = target_code_type + ".csv"
    map_path = phen_path / MAP_DIR / output_filename
    out.to_csv(map_path, index=False)
    _logger.info(f"Saved mapped concepts to {str(map_path.resolve())}")

    # save concept sets as separate files
    concept_set_path = phen_path / CSV_PATH / target_code_type

    # empty the concept-set directory except for hiddle files, e.g. .git
    if concept_set_path.exists():
        for item in concept_set_path.iterdir():
            if not item.name.startswith("."):
                item.unlink()
    else:
        concept_set_path.mkdir(parents=True, exist_ok=True)

    # write each concept as a separate file
    for name, concept in out.groupby("CONCEPT_SET"):
        concept = concept.sort_values(by="CONCEPT")  # sort rows
        concept = concept.dropna(how="all", axis=1)  # remove empty cols
        concept = concept.reindex(
            sorted(concept.columns), axis=1
        )  # sort cols alphabetically
        filename = f"{name}.csv"
        concept_path = concept_set_path / filename
        concept.to_csv(concept_path, index=False)

    write_vocab_version(phen_path)

    _logger.info(f"Phenotype processed target code type {target_code_type}")


# Add metadata dict to each row of Df codes
def add_metadata(
    codes: pd.DataFrame,
    metadata: dict,
    no_metadata: bool,
) -> pd.DataFrame:
    """Add concept set metadata, stored as a dictionary, to each concept row"""

    if not no_metadata:
        for meta_name, meta_value in metadata.items():
            codes[meta_name] = meta_value
            _logger.debug(
                f"Adding metadata for concept set: metadata name {meta_name}, metadata value {meta_value}"
            )

    return codes


def _generate_version_tag(
    repo: git.Repo, increment: str = DEFAULT_VERSION_INC, use_v_prefix: bool = False
) -> str:
    # Get all valid semantic version tags
    versions = []
    for tag in repo.tags:
        if tag.name.startswith("v"):
            tag_name = tag.name[1:]  # Remove the first character
        else:
            tag_name = tag.name
        if semver.Version.is_valid(tag_name):
            versions.append(semver.Version.parse(tag_name))

    _logger.debug(f"Versions: {versions}")
    # Determine the next version
    if not versions:
        new_version = semver.Version(0, 0, 1)
    else:
        latest_version = max(versions)
        if increment == "major":
            new_version = latest_version.bump_major()
        elif increment == "minor":
            new_version = latest_version.bump_minor()
        else:
            new_version = latest_version.bump_patch()

    # Create the new tag
    new_version_str = f"v{new_version}" if use_v_prefix else str(new_version)

    return new_version_str


def publish(
    phen_dir: str, msg: str, remote_url: str, increment: str = DEFAULT_VERSION_INC
):
    """Publishes updates to the phenotype by commiting all changes to the repo directory"""

    # Validate config
    validate(phen_dir)
    phen_path = Path(phen_dir)

    # load git repo and set the branch
    repo = git.Repo(phen_path)
    if DEFAULT_GIT_BRANCH in repo.branches:
        main_branch = repo.heads[DEFAULT_GIT_BRANCH]
        main_branch.checkout()
    else:
        raise AttributeError(
            f"Phen repo does not contain the default branch {DEFAULT_GIT_BRANCH}"
        )

    # check if any changes to publish
    if not repo.is_dirty() and not repo.untracked_files:
        if remote_url is not None and "origin" not in repo.remotes:
            _logger.info(f"First publish to remote url {remote_url}")
        else:
            _logger.info("Nothing to publish, no changes to the repo")
            return

    # get next version
    new_version_str = _generate_version_tag(repo, increment)
    _logger.info(f"New version: {new_version_str}")

    # Write version in configuration file
    config_path = phen_path / CONFIG_FILE
    with config_path.open("r") as file:
        config = yaml.safe_load(file)

    config["phenotype"]["version"] = new_version_str
    with open(config_path, "w") as file:
        yaml.dump(
            config,
            file,
            Dumper=util.QuotedDumper,
            default_flow_style=False,
            sort_keys=False,
            default_style='"',
        )

    # Add and commit changes to repo including version updates
    commit_message = f"Committing updates to phenotype {phen_path}"
    repo.git.add("--all")
    repo.index.commit(commit_message)

    # Add tag to the repo
    repo.create_tag(new_version_str)

    # push to origin if a remote repo
    if remote_url is not None and "origin" not in repo.remotes:
        git_url = _construct_git_url(remote_url)
        repo.create_remote("origin", git_url)

    try:
        if "origin" in repo.remotes:
            _logger.debug(f"Remote 'origin' is set {repo.remotes.origin.url}")
            origin = repo.remotes.origin
            _logger.info(f"Pushing main branch to remote repo")
            repo.git.push("--set-upstream", "origin", "main")
            _logger.info(f"Pushing version tags to remote git repo")
            origin.push(tags=True)
            _logger.debug("Changes pushed to 'origin'")
        else:
            _logger.debug("Remote 'origin' is not set")
    except Exception as e:
        tag_ref = repo.tags[new_version_str]
        repo.delete_tag(tag_ref)
        repo.git.reset("--soft", "HEAD~1")
        raise e

    _logger.info(f"Phenotype published successfully")


def export(phen_dir: str, version: str):
    """Exports a phen repo at a specific tagged version into a target directory"""
    _logger.info(f"Exporting phenotype {phen_dir} at version {version}")

    # validate configuration
    validate(phen_dir)
    phen_path = Path(phen_dir)

    # load configuration
    config_path = phen_path / CONFIG_FILE
    with config_path.open("r") as file:
        config = yaml.safe_load(file)

    map_path = phen_path / MAP_DIR
    if not map_path.exists():
        _logger.warning(f"Map path does not exist '{map_path}'")

    export_path = phen_path / OMOP_PATH
    # check export directory exists and if not create it
    if not export_path.exists():
        export_path.mkdir(parents=True)
        _logger.debug(f"OMOP export directory '{export_path}' created.")

    # omop export db
    export_db_path = omop.export(
        map_path,
        export_path,
        config["phenotype"]["version"],
        config["phenotype"]["omop"],
    )

    _logger.info(f"Phenotype exported successfully")


def copy(phen_dir: str, target_dir: str, version: str):
    """Copys a phen repo at a specific tagged version into a target directory"""

    # Validate
    validate(phen_dir)
    phen_path = Path(phen_dir)

    # Check target directory exists
    target_path = Path(target_dir)
    if not target_path.exists():
        raise FileNotFoundError(f"The target directory {target_path} does not exist")

    # Set copy directory
    copy_path = target_path / version
    _logger.info(f"Copying repo {phen_path} to {copy_path}")

    if (
        copy_path.exists() and copy_path.is_dir()
    ):  # Check if it exists and is a directory
        copy = _check_delete_dir(
            copy_path,
            f"The directory {str(copy_path.resolve())} already exists. Do you want to overwrite? (yes/no): ",
        )
    else:
        copy = True

    if not copy:
        _logger.info(f"Not copying the version {version}")
        return

    _logger.debug(f"Cloning repo from {phen_path} into {copy_path}...")
    repo = git.Repo.clone_from(phen_path, copy_path)

    # Check out the latest commit or specified version
    if version:
        # Checkout a specific version (e.g., branch, tag, or commit hash)
        _logger.info(f"Checking out version {version}...")
        repo.git.checkout(version)
    else:
        # Checkout the latest commit (HEAD)
        _logger.info(f"Checking out the latest commit...")
        repo.git.checkout("HEAD")

    _logger.debug(f"Copied {phen_path} {repo.head.commit.hexsha[:7]} in {copy_path}")

    _logger.info(f"Phenotype copied successfully")


# Convert concept_sets list into dictionaries
def extract_concepts(config_data: dict) -> Tuple[dict, Set[str]]:
    """Extracts concepts as {name: file_path} dictionary and a name set."""
    concepts_dict = {
        item["name"]: [file["path"] for file in item["files"]]
        for item in config_data["phenotype"]["concept_sets"]
    }
    name_set = set(concepts_dict.keys())
    return concepts_dict, name_set


def _extract_clean_deepdiff_keys(diff: dict, key_type: str) -> Set[Any]:
    """
    Extracts clean keys from a DeepDiff dictionary.

    :param diff: DeepDiff result dictionary
    :param key_type: The type of change to extract (e.g., "dictionary_item_added", "dictionary_item_removed")
    :return: A set of clean key names
    """
    return {key.split("root['")[1].split("']")[0] for key in diff.get(key_type, [])}


def diff_config(old_config: dict, new_config: dict) -> str:
    report = f"\n# Changes to phenotype configuration\n"
    report += f"This compares changes in the phenotype configuration including added, removed and renamed concept sets and changes to concept set source concept code file paths\n\n"

    old_concepts, old_names = extract_concepts(old_config)
    new_concepts, new_names = extract_concepts(new_config)

    # Check added and removed concept set names
    added_names = new_names - old_names  # Names that appear in new but not in old
    removed_names = old_names - new_names  # Names that were in old but not in new

    # find file path changes for unchanged names
    unchanged_names = old_names & new_names  # Names that exist in both
    file_diff = DeepDiff(
        {name: old_concepts[name] for name in unchanged_names},
        {name: new_concepts[name] for name in unchanged_names},
    )

    # Find renamed concepts (same file, different name)
    renamed_concepts = []
    for removed in removed_names:
        old_path = old_concepts[removed]
        for added in added_names:
            new_path = new_concepts[added]
            if old_path == new_path:
                renamed_concepts.append((removed, added))

    # Remove renamed concepts from added and removed sets
    for old_name, new_name in renamed_concepts:
        added_names.discard(new_name)
        removed_names.discard(old_name)

    # generate config report
    if added_names:
        report += "## Added Concepts\n"
        for name in added_names:
            report += f"- `{name}` (File: `{new_concepts[name]}`)\n"
        report += "\n"

    if removed_names:
        report += "## Removed Concepts\n"
        for name in removed_names:
            report += f"- `{name}` (File: `{old_concepts[name]}`)\n"
        report += "\n"

    if renamed_concepts:
        report += "## Renamed Concepts\n"
        for old_name, new_name in renamed_concepts:
            report += (
                f"- `{old_name}` ➝ `{new_name}` (File: `{old_concepts[old_name]}`)\n"
            )
        report += "\n"

    if "values_changed" in file_diff:
        report += "## Updated File Paths\n"
        for name, change in file_diff["values_changed"].items():
            old_file = change["old_value"]
            new_file = change["new_value"]
            clean_name = name.split("root['")[1].split("']")[0]
            report += (
                f"- `{clean_name}` changed file from `{old_file}` ➝ `{new_file}`\n"
            )
        report += "\n"

    if not (
        added_names
        or removed_names
        or renamed_concepts
        or file_diff.get("values_changed")
    ):
        report += "No changes in concept sets.\n"

    return report


def diff_map_files(
    old_map_path: Path,
    new_map_path: Path,
    output_changed_concepts: bool,
    csv_output_path: Path,
) -> str:
    old_output_files = [
        file.name
        for file in old_map_path.iterdir()
        if file.is_file() and not file.name.startswith(".")
    ]
    new_output_files = [
        file.name
        for file in new_map_path.iterdir()
        if file.is_file() and not file.name.startswith(".")
    ]

    # Convert the lists to sets for easy comparison
    old_output_set = set(old_output_files)
    new_output_set = set(new_output_files)

    # Outputs that are in old_output_set but not in new_output_set (removed files)
    removed_outputs = old_output_set - new_output_set
    # Outputs that are in new_output_set but not in old_output_set (added files)
    added_outputs = new_output_set - old_output_set
    # Outputs that are the intersection of old_output_set and new_output_set
    common_outputs = old_output_set & new_output_set

    report = f"\n# Changes to available translations\n"
    report += f"This compares the coding translations files available.\n\n"
    report += f"- Removed outputs: {sorted(list(removed_outputs))}\n"
    report += f"- Added outputs: {sorted(list(added_outputs))}\n"
    report += f"- Common outputs: {sorted(list(common_outputs))}\n\n"

    # Step N: Compare common outputs between versions
    report += f"# Changes to concepts in translation files\n\n"
    report += f"This compares the added and removed concepts in each of the coding translation files. Note that this might be different to the config.yaml if the translations have not been run for the current config.\n\n"
    for file in common_outputs:
        old_output = old_map_path / file
        new_output = new_map_path / file

        _logger.debug(f"Old ouptput: {str(old_output.resolve())}")
        _logger.debug(f"New ouptput: {str(new_output.resolve())}")

        df1 = pd.read_csv(old_output)
        df1_count = df1[["CONCEPT", "CONCEPT_SET"]].groupby("CONCEPT_SET").count()
        df2 = pd.read_csv(new_output)
        df2_count = df2[["CONCEPT", "CONCEPT_SET"]].groupby("CONCEPT_SET").count()

        # Check for added and removed concepts
        report += f"- File {file}\n"
        sorted_list = sorted(list(set(df1_count.index) - set(df2_count.index)))
        report += f"- Removed concepts {sorted_list}\n"
        sorted_list = sorted(list(set(df2_count.index) - set(df1_count.index)))
        report += f"- Added concepts {sorted_list}\n"

        # Find differences in rows between df1 and df2
        out = df1.merge(
            df2,
            on=["CONCEPT", "CONCEPT_SET"],
            how="outer",
            suffixes=["_old", "_new"],
            indicator=True,
        )
        out = out[out["_merge"] != "both"]  # only select rows that are different
        out["_merge"] = out["_merge"].cat.rename_categories(
            {"left_only": "Removed", "right_only": "Added"}
        )  # rename categories
        out.sort_values(by=["CONCEPT_SET", "_merge"], inplace=True)

        # Count the number of added and removed concepts for each concept set
        report += f"- Changed concepts:\n"
        for concept_set_name, grp in out.groupby("CONCEPT_SET"):
            counts = grp["_merge"].value_counts()
            report += "\t - {} +{} -{}\n".format(
                concept_set_name, counts["Added"], counts["Removed"]
            )
        report += "\n"

        # Write the output to a CSV file
        if output_changed_concepts and out.shape[0] > 0:
            csv_filename = f"{Path(file).stem}_diff.csv"
            csv_filepath = csv_output_path / csv_filename
            out.to_csv(csv_filepath, index=False)
            _logger.debug(f"CSV of changes written to {str(csv_filepath.resolve())}")

    return report


def diff_phen(
    new_phen_path: Path,
    new_version: str,
    old_phen_path: Path,
    old_version: str,
    report_path: Path,
    csv_output_path: Path,
    not_check_config: bool,
    output_changed_concepts: bool,
):
    """Compare the differences between two versions of a phenotype"""

    # write report heading
    report = f"# Phenotype Comparison Report\n"

    # Step 1: check differences configuration files
    if not not_check_config:
        # validate phenotypes
        _logger.debug(f"Validating for diff old path: {str(old_phen_path.resolve())}")
        validate(str(old_phen_path.resolve()))
        _logger.debug(f"Validating for diff new path: {str(new_phen_path.resolve())}")
        validate(str(new_phen_path.resolve()))

        # get old and new config
        old_config_path = old_phen_path / CONFIG_FILE
        with old_config_path.open("r") as file:
            old_config = yaml.safe_load(file)
        new_config_path = new_phen_path / CONFIG_FILE
        with new_config_path.open("r") as file:
            new_config = yaml.safe_load(file)

        # write report
        report += f"## Original phenotype\n"
        report += f"  - {old_config['phenotype']['omop']['vocabulary_id']}\n"
        report += f"  - {old_version}\n"
        report += f"  - {str(old_phen_path.resolve())}\n"
        report += f"## Changed phenotype:\n"
        report += f"  - {new_config['phenotype']['omop']['vocabulary_id']}\n"
        report += f"  - {new_version}\n"
        report += f"  - {str(new_phen_path.resolve())}\n"

        # Convert list of dicts into a dict: {name: file}
        report += diff_config(old_config, new_config)

    # Step 2: check differences between map files
    # List files from output directories
    old_map_path = old_phen_path / MAP_DIR
    new_map_path = new_phen_path / MAP_DIR
    report += diff_map_files(
        old_map_path, new_map_path, output_changed_concepts, csv_output_path
    )

    # initialise report file
    _logger.debug(f"Writing to report file {str(report_path.resolve())}")
    report_file = open(report_path, "w")
    report_file.write(report)
    report_file.close()

    _logger.info(f"Phenotypes diff'd successfully")


def diff(
    phen_dir: str,
    version: str,
    old_phen_dir: str,
    old_version: str,
    not_check_config: bool,
    output_changed_concepts: bool,
):
    # make tmp directory .acmc
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    temp_dir = Path(f".acmc/diff_{timestamp}")

    changed_phen_path = Path(phen_dir)
    if not changed_phen_path.exists():
        raise ValueError(
            f"Changed phenotype directory does not exist: {str(changed_phen_path.resolve())}"
        )

    old_phen_path = Path(old_phen_dir)
    if not old_phen_path.exists():
        raise ValueError(
            f"Old phenotype directory does not exist: {str(old_phen_path.resolve())}"
        )

    try:
        # Create the directory
        temp_dir.mkdir(parents=True, exist_ok=True)
        _logger.debug(f"Temporary directory created: {temp_dir}")

        # Create temporary directories
        changed_path = temp_dir / "changed"
        changed_path.mkdir(parents=True, exist_ok=True)
        old_path = temp_dir / "old"
        old_path.mkdir(parents=True, exist_ok=True)

        # checkout changed
        if version == "latest":
            _logger.debug(
                f"Copying changed repo from {phen_dir} into {changed_path} at version {version}..."
            )
            shutil.copytree(changed_phen_path, changed_path, dirs_exist_ok=True)
        else:
            _logger.debug(
                f"Cloning changed repo from {phen_dir} into {changed_path} at version {version}..."
            )
            changed_repo = git.Repo.clone_from(changed_phen_path, changed_path)
            changed_repo.git.checkout(version)

        # checkout old
        if old_version == "latest":
            _logger.debug(
                f"Copying old repo from {old_phen_dir} into {old_path} at version {old_version}..."
            )
            shutil.copytree(old_phen_path, old_path, dirs_exist_ok=True)
        else:
            _logger.debug(
                f"Cloning old repo from {old_phen_dir} into {old_path} at version {old_version}..."
            )
            old_repo = git.Repo.clone_from(old_phen_dir, old_path)
            old_repo.git.checkout(old_version)

        report_filename = f"{version}_{old_version}_diff.md"
        report_path = changed_phen_path / report_filename
        csv_output_path = changed_phen_path
        # diff old with new
        diff_phen(
            changed_path,
            version,
            old_path,
            old_version,
            report_path,
            csv_output_path,
            not_check_config,
            output_changed_concepts,
        )

    finally:
        # clean up tmp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
