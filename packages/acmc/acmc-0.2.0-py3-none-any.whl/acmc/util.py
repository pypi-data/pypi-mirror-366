import yaml

"""
util.py module

This module provides general utility functions for the acmc modules

"""


class QuotedDumper(yaml.Dumper):
    """Custom Dumper to retain quotes on strings in yaml library"""

    def increase_indent(self, flow=False, indentless=False):
        return super(QuotedDumper, self).increase_indent(flow, indentless)
