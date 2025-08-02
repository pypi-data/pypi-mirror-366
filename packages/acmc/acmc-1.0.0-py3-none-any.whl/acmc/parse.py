"""
parse.py module

This module provides functionality to set up medical code translation classes

"""

import pandas as pd
import numpy as np
import os
from typing import Callable, Optional, Tuple
from pathlib import Path
from acmc import trud, logging_config as lc

# setup logging
_logger = lc.setup_logger()

SUPPORTED_CODE_TYPES = {"read2", "read3", "icd10", "snomed", "opcs4", "atc"}
"""List of support medical coding types"""


class CodesError:
    """A class used in InvalidCodesException to report an error if a code parser check fails"""

    def __init__(self, message, codes=None, codes_file=None, mask=None, code_type=None):
        # initialise class variables with provided parameters
        for key, value in locals().items():
            if key != "self":
                setattr(self, key, value)


class InvalidCodesException(Exception):
    """Custom exception class raised when invalid codes are found that cannot be resolved by processing"""

    def __init__(self, error):
        super().__init__(error.message)
        self.error = error


class Proto:
    """
    Define checks as list of 3 tuple: (Message, Condition, Process)
    - Message = The name of the condition (what is printed and logged)
    - Condition = True if Passed, and False if Failed
    - Process = Aims to resolve all issues that stop condition from passing (Do not change index!)
    """

    checks: list[
        tuple[
            str,  # The description, e.g., "Not Empty"
            Callable[
                [pd.DataFrame],
                pd.Series,
            ],  # The first lambda function: takes a list and returns a pd.Series of booleans
            Callable[
                [pd.DataFrame, Path],
                pd.DataFrame,
            ],  # The second lambda function: takes a list and a string, and returns nothing
        ]
    ]

    def __init__(self, name: str, trud_codes_path: Optional[Path] = None):
        if trud_codes_path is not None:
            if trud_codes_path.is_file():
                self.trud_codes_path: Path = trud_codes_path
                self.db: pd.DataFrame = pd.read_parquet(self.trud_codes_path)
            else:
                raise FileNotFoundError(
                    f"Error: Read2 code file '{trud_codes_path}' does not exist. Please ensure you have installed TRUD correctly"
                )

        self.name: str = name

    def raise_exception(self, ex: Exception):
        """Raises an exception inside a lambda function. Python does not allow using raise statement inside lambda because lambda can only contain expressions, not statements. Using raise_exception not raise_ as it's more explict"""
        raise ex

    def in_database(
        self, codes: pd.DataFrame, db: pd.DataFrame, col: str
    ) -> pd.DataFrame:
        return codes.isin(db[col])

    def process(
        self, codes: pd.DataFrame, codes_file: Path
    ) -> Tuple[pd.DataFrame, list]:
        """identify issues that do not pass and fix them with define/d process"""
        errors = []
        # Iter through each item in check.
        for msg, cond, fix in self.checks:
            # Check if any codes fail the check to False
            if not cond(codes).all():
                # Log the number of codes that failed
                _logger.debug(
                    f"Check: {msg} {(~cond(codes)).sum()} failed, trying to fix"
                )
                # try fix errors by running lamba "process" function
                try:
                    codes = fix(codes, codes_file)
                    _logger.debug(f"Check: Fixed")
                except InvalidCodesException as ex:
                    errors.append(ex.error)
                    codes = codes[cond(codes)]  # remove codes that cannot be fixed
                    _logger.debug(f"Check: Invalid Codes Removed, no fix available")
            else:
                _logger.debug(f"Check: passed")

        return codes, errors

    def verify(self, codes: pd.DataFrame, codes_file: Path):
        """verify codes in codes file"""
        conds = np.array([])

        # Iter through each item in check.
        for msg, cond, process in self.checks:
            # run conditional check
            out = cond(codes)
            conds = np.append(conds, out.all())

        return conds


class Read2(Proto):
    """This Read2 class extends Proto, adding custom validation checks for a dataset of "Read2" codes. It ensures that the dataset is loaded, validates the codes based on several rules, and applies corrections or logs errors when necessary."""

    def __init__(self):
        super().__init__("read2", trud.PROCESSED_PATH / "read2.parquet")

        # validate checks
        self.checks = [
            (
                # check codes are not empty, if empty throw an exception
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                # check codes <5 characters, if too short pads it with . (dots) to reach 5 characters
                "Too Short",
                lambda codes: ~(codes.str.len() < 5),
                lambda codes, codes_file: codes.str.pad(
                    width=5, side="right", fillchar="."
                ),
            ),
            (
                # check codes > 5 characters, If too long, truncates them to 5 characters
                "Too Long",
                lambda codes: ~(codes.str.len() > 5),
                lambda codes, codes_file: codes.str[:5],
            ),
            (
                # checks codes contain numbers, or dots (.), if not logs invalid code error
                "Alphanumeric Dot",
                lambda codes: codes.str.match(r"^[a-zA-Z0-9.]+$"),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Illegal code format, not alphanumeric dot",
                            codes=codes,
                            codes_file=codes_file,
                            mask=codes.str.match(r"^[a-zA-Z0-9.]+$"),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                # checks code exists in self.db (the Read2 dataset). If missing log invalid codes.
                "In Database",
                lambda codes: self.in_database(codes, self.db, self.name),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Codes do not exist in database",
                            codes=codes,
                            codes_file=codes_file,
                            mask=self.in_database(codes, self.db, self.name),
                            code_type=self.name,
                        )
                    )
                ),
            ),
        ]


class Read3(Proto):
    def __init__(self):
        super().__init__("read3", trud.PROCESSED_PATH / "read3.parquet")

        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Too Short",
                lambda codes: ~(codes.str.len() < 5),
                lambda codes, codes_file: codes.str.pad(
                    width=5, side="right", fillchar="."
                ),
            ),
            (
                "Too Long",
                lambda codes: ~(codes.str.len() > 5),
                lambda codes, codes_file: codes.str[:5],
            ),
            (
                "Alphanumeric Dot",
                lambda codes: codes.str.match(r"^[a-zA-Z0-9.]+$"),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Alphanumeric Dot",
                            codes=codes,
                            codes_file=codes_file,
                            mask=codes.str.match(r"^[a-zA-Z0-9.]+$"),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "In Database",
                lambda codes: self.in_database(codes, self.db, self.name),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA In Database",
                            codes=codes,
                            codes_file=codes_file,
                            mask=self.in_database(codes, self.db, self.name),
                            code_type=self.name,
                        )
                    )
                ),
            ),
        ]


class Icd10(Proto):
    def __init__(self):
        super().__init__("icd10", trud.PROCESSED_PATH / "icd10.parquet")

        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty {codes_file}",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Too Short",
                lambda codes: ~(codes.str.len() < 3),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Too Short",
                            codes=codes,
                            codes_file=codes_file,
                            mask=~(codes.str.len() < 3),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Has Dot",
                lambda codes: ~(codes.str.match(r".*\..*")),  # check if contains dot
                lambda codes, codes_file: codes.str.replace(
                    ".", ""
                ),  # delete any dots in string
                # lambda codes : codes.str.split('\.').apply(lambda ls: ls[0]) #only get part before dot
            ),
            (
                "Alphanumeric Capital",
                lambda codes: codes.str.match(r"^[A-Z0-9]+$"),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Alphanumeric Capital",
                            codes=codes,
                            codes_file=codes_file,
                            mask=codes.str.match(r"^[A-Z0-9]+$"),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "In Database",
                lambda codes: ~(
                    ~self.in_database(codes, self.db, self.name)
                    & ~self.in_database(codes, self.db, self.name + "_alt")
                ),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA In Database",
                            codes=codes,
                            codes_file=codes_file,
                            mask=~(
                                ~self.in_database(codes, self.db, self.name)
                                & ~self.in_database(codes, self.db, self.name + "_alt")
                            ),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            # 			(
            # 				"ICD10 Regex",
            # 				lambda codes : codes.str.match("[a-zA-Z][0-9][0-9]\.?[a-zA-Z0-9]*$"), #Alpha, Num, Num , Dot?, 4xAlphNum*
            # 				lambda codes : lc.log_invalid_code(codes,
            # 												codes.str.match("[a-zA-Z][0-9][0-9]\.?[a-zA-Z0-9]*$"), #Log non-matching rows
            # 												code_type="icd10",
            #
            # 			)
        ]


class Snomed(Proto):
    def __init__(self):
        super().__init__("snomed", trud.PROCESSED_PATH / "snomed.parquet")

        self.checks = [
            # (
            # 	"Not Empty",
            # 	lambda codes : pd.Series([len(codes) > 0]),
            # 	lambda codes : raise_exception(Exception("Code List is Empty"))
            # ),
            (
                "Too Short",
                lambda codes: ~(codes.str.len() < 6),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Too Short",
                            codes=codes,
                            codes_file=codes_file,
                            mask=~(codes.str.len() < 6),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Too Long",
                lambda codes: ~(codes.str.len() > 18),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Too Long",
                            codes=codes,
                            codes_file=codes_file,
                            mask=~(codes.str.len() > 18),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Is Integer",
                lambda codes: ~codes.str.contains("."),
                lambda codes, codes_file: codes.str.split(".")
                .str[0]
                .astype(str),  # Convert from float to integer and back to string
            ),
            (
                "Numeric",
                lambda codes: codes.str.match(r"[0-9]+$"),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Numeric",
                            codes=codes,
                            codes_file=codes_file,
                            mask=codes.str.match(r"[0-9]+$"),
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "In Database",
                lambda codes: self.in_database(codes, self.db, self.name),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA In Database",
                            codes=codes,
                            codes_file=codes_file,
                            mask=self.in_database(codes, self.db, self.name),
                            code_type=self.name,
                        )
                    )
                ),
            ),
        ]


class Opcs4(Proto):
    def __init__(self):
        super().__init__("opcs4", trud.PROCESSED_PATH / "opcs4.parquet")

        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "In Database",
                lambda codes: self.in_database(codes, self.db, self.name),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA In Database",
                            codes=codes,
                            codes_file=codes_file,
                            mask=self.in_database(codes, self.db, self.name),
                            code_type=self.name,
                        )
                    )
                ),
            ),
        ]


class Atc(Proto):
    def __init__(self):
        super().__init__("atc", trud_codes_path=None)
        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            ),
            (
                "Alphanumeric Capital",
                lambda codes: codes.str.match(r"^[A-Z0-9]+$"),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"QA Alphanumeric Capital",
                            codes=codes,
                            codes_file=codes_file,
                            mask=codes.str.match(r"^[A-Z0-9]+$"),
                            code_type=self.name,
                        )
                    )
                ),
            ),
        ]


class Med(Proto):
    def __init__(self):
        super().__init__("med", trud_codes_path=None)
        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            )
        ]


class Cprd(Proto):
    def __init__(self):
        super().__init__("cprd", trud_codes_path=None)
        self.checks = [
            (
                "Not Empty",
                lambda codes: pd.Series([len(codes) > 0]),
                lambda codes, codes_file: self.raise_exception(
                    InvalidCodesException(
                        CodesError(
                            f"Code list is empty",
                            codes=codes,
                            codes_file=codes_file,
                            mask=None,
                            code_type=self.name,
                        )
                    )
                ),
            )
        ]


class CodeTypeParser:
    """A class used in InvalidCodesException to report an error if a code parser check fails"""

    def __init__(self, trud_processed_dir: Path = trud.PROCESSED_PATH):
        if not trud_processed_dir.exists() or not trud_processed_dir.is_dir():
            raise FileNotFoundError(
                f"Cannot initialise parsers as the TRUD processed directory {trud_processed_dir} does not exist, please check that TRUD has been installed: acmc trud install"
            )

        self.code_types = {
            "read2": Read2(),
            "read3": Read3(),
            "icd10": Icd10(),
            "snomed": Snomed(),
            "opcs4": Opcs4(),
            "atc": Atc(),
            "med": Med(),
            "cprd": Cprd(),
        }
