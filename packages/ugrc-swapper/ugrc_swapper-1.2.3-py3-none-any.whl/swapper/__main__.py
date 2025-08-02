#!/usr/bin/env python
# * coding: utf8 *
"""
swapper

Usage:
    swapper swap <tables>...
    swapper copy_and_replace <source_table_path> <destination_table_path> <destination_workspace_owner> <users>...
    swapper compare [--swap]

Arguments:
    tables:                         One or more fully qualified table names DB.SCHEMA.Table
                                    (e.g. SGID.HEALTH.SmallAreas_ObesityAndActivity) separated by spaces.
    source_table_path:              A path to a source feature class or table
    destination_table_path:         A path to a destination feature class or table
    destination_workspace_owner:    A path to a connection file for the database owner (sde).
    users:                          A space-separated list of users that you want view access granted to.

Examples:
    swapper swap sgid.health.health_areas sgid.boundaries.counties      Swaps the health_areas and counties tables from
                                                                        SGID to SGID10.
    swapper compare --swap                                              Compares tables between SGID & SGID10 and swaps
                                                                        them if needed.
    swapper copy_and_replace /fgdb.gdb/landownership /database.sde/sgid.cadastre.landownership /owner.sde
"""
from pathlib import Path

from docopt import docopt

from .swapper import compare, copy_and_replace, swap_sgid_data


def main():
    """Main entry point for program. Parse arguments and route to top level methods."""
    args = docopt(__doc__, version="1.1.0")

    def swap_tables(tables):
        for table in tables:
            print(f"updating table: {table}")
            swap_sgid_data(table)

    if args["swap"] and args["<tables>"]:
        swap_tables(args["<tables>"])
    elif args["<source_table_path>"]:
        copy_and_replace(
            Path(args["<source_table_path>"]),
            Path(args["<destination_table_path>"]),
            Path(args["<destination_workspace_owner>"]),
            args["<users>"],
        )
    elif args["compare"]:
        tables_needing_update = compare()
        print(f"tables_needing_update: {(tables_needing_update)}")

        if args["--swap"]:
            swap_tables(tables_needing_update)


if __name__ == "__main__":
    main()
