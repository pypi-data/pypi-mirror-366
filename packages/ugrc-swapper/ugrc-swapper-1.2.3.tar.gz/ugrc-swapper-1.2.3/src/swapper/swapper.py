#!/usr/bin/env python
# * coding: utf8 *
"""
swapper.py
Main module for swapper package.
"""
from os import getenv
from pathlib import Path
from textwrap import dedent

import arcpy
import pyodbc
from dotenv import load_dotenv
from xxhash import xxh64

TEMP_EXTENSION = "_temp"

load_dotenv()


def delete_locks(fc_owner, fc_name, db_owner):
    """delete locks for the specified table
    fc_owner (string): owner of feature class
    fc_name (string): name of feature class (e.g. LandOwnership)
    db_owner (string): path to connection file with owner creds
    """
    if not Path(db_owner).exists():
        print(f"{db_owner} does not exist")

        return

    db_connect = arcpy.ArcSDESQLExecute(db_owner)

    sql = dedent(
        f"""SELECT * FROM sde.SDE_process_information
        WHERE SDE_ID IN(SELECT SDE_ID FROM sde.SDE_table_locks
        WHERE registration_id = (SELECT registration_id FROM sde.SDE_table_registry
        WHERE UPPER(table_name) = UPPER('{fc_name}') AND UPPER(owner) = UPPER('{fc_owner}')));
    """
    )

    db_return = db_connect.execute(sql)

    if db_return is True:
        print("no locks to delete")

        return

    for user in db_return:
        print(f"deleted lock {user[0]}")
        arcpy.DisconnectUser(db_owner, user[0])


def swap_sgid_data(sgid_feature_class_name):
    """replaces sgid_feature_class_name in SGID10 with the SGID version"""
    owner = sgid_feature_class_name.split(".")[1].upper()
    table_name = sgid_feature_class_name.split(".")[2].strip()

    sgid_path = (
        Path(getenv("SWAPPER_CONNECTION_FILE_PATH"))
        / "SGID_internal"
        / f"SGID_{owner.title()}.sde"
        / f"SGID.{owner}.{table_name}"
    )
    sgid10_path = (
        Path(getenv("SWAPPER_CONNECTION_FILE_PATH"))
        / "SGID10"
        / f"SGID10_{owner.title()}.sde"
        / f"SGID10.{owner}.{table_name}"
    )

    db_owner = str(Path(getenv("SWAPPER_CONNECTION_FILE_PATH")) / "SGID10" / "SGID10_sde.sde")
    copy_and_replace(sgid_path, sgid10_path, db_owner)


def copy_and_replace(  #: pylint: disable=dangerous-default-value too-many-statements
    source_feature_class, destination_feature_class, db_owner_connection_file, view_users=["internal"]
):
    """replaces destination_feature_class with source_feature_class
    source_feature_class (pathlib.Path)
    destination_feature_class (pathlib.Path): must be an SDE feature class, and the name must be fully qualified
    db_owner_connection_file (pathlib.Path): path to connection file for db owner
    view_users: array of users that you want view access granted (default is for SGID10 database)
    """
    source_workspace = source_feature_class.parent
    if not source_workspace.exists():
        raise Exception(f"{source_workspace} does not exist")

    destination_workspace = destination_feature_class.parent
    if not destination_workspace.exists():
        raise Exception(f"{destination_workspace} does not exist")

    source_workspace = str(source_workspace)
    source_feature_class_name = str(source_feature_class.name)
    source_feature_class = str(source_feature_class)

    destination_workspace = str(destination_workspace)
    destination_feature_class_name = str(destination_feature_class.name)
    destination_feature_class = str(destination_feature_class)

    def check_table_existence(workspace, table_name):
        with arcpy.EnvManager(workspace=workspace):
            if not arcpy.Exists(table_name):
                raise FileNotFoundError(f"{table_name} does not exist in {workspace}")

    check_table_existence(source_workspace, source_feature_class_name)

    empty_destination = False
    try:
        check_table_existence(destination_workspace, destination_feature_class_name)
    except FileNotFoundError:
        empty_destination = True

    with arcpy.EnvManager(workspace=destination_workspace):
        if empty_destination:
            temp_feature_class = destination_feature_class
        else:
            temp_feature_class = f"{destination_feature_class_name}{TEMP_EXTENSION}"

        if arcpy.Exists(temp_feature_class):
            print(f"{temp_feature_class} already exists in {destination_workspace}, deleting...")

            arcpy.management.Delete(temp_feature_class)

        describe = arcpy.da.Describe(source_feature_class)
        is_table = describe["datasetType"] == "Table"
        try:
            if is_table:
                arcpy.management.CopyRows(source_feature_class, temp_feature_class)
            else:
                arcpy.management.CopyFeatures(source_feature_class, temp_feature_class)
            print(f"copied {source_feature_class} to {temp_feature_class}")
        except Exception as e:
            raise Exception(f"could not copy to {destination_workspace}: {str(e)}")

        try:
            delete_locks(
                destination_feature_class_name.split(".")[1],
                destination_feature_class_name.split(".")[-1],
                str(db_owner_connection_file),
            )
        except Exception:
            raise Exception("could not delete table locks")

        if not empty_destination:
            try:
                arcpy.management.Delete(destination_feature_class_name)
                print(f"deleted {destination_feature_class}")
            except Exception:
                raise Exception(f"could not delete {destination_feature_class}")

            try:
                arcpy.management.Rename(temp_feature_class, destination_feature_class_name)

                #: fix metadata title since it will still have the _temp suffix on it
                metadata = arcpy.metadata.Metadata(destination_feature_class_name)
                metadata.title = destination_feature_class_name
                metadata.save()
                print(f"renamed {temp_feature_class}")
            except Exception:
                raise Exception(f"could not rename {temp_feature_class}")

        try:
            for user in view_users:
                arcpy.management.ChangePrivileges(destination_feature_class_name, user, "GRANT", "AS_IS")
        except Exception:
            raise Exception(f"could not update privileges to {destination_feature_class_name}")


def compare():
    """compares data sets between SGID and SGID10 and returns the tables that are different"""
    dbo_owner = Path(getenv("SWAPPER_CONNECTION_FILE_PATH")) / "SGID10" / "SGID10_sde.sde"

    if not Path(dbo_owner).exists():
        print(f"{dbo_owner} does not exist")

        return []

    tables_needing_update = []

    internal_connection = pyodbc.connect(getenv("SWAPPER_INTERNAL_DB_CONNECTION"))
    internal_hashes = get_hashes(internal_connection.cursor())
    sgid10_connection = pyodbc.connect(getenv("SWAPPER_EXTERNAL_DB_CONNECTION"))
    sgid10_hashes = get_hashes(sgid10_connection.cursor())

    tables_missing_from_internal = set(sgid10_hashes) - set(internal_hashes)
    if len(tables_missing_from_internal) > 0:
        print(f"tables_missing_from_internal: {tables_missing_from_internal}")

    tables_missing_from_sgid10 = set(internal_hashes) - set(sgid10_hashes)
    if len(tables_missing_from_sgid10) > 0:
        print(f"tables_missing_from_sgid10: {tables_missing_from_sgid10}")

    for table in set(internal_hashes) & set(sgid10_hashes):
        if internal_hashes[table] != sgid10_hashes[table]:
            tables_needing_update.append(table)

    return tables_needing_update


def get_hashes(cursor):
    """get hashes for all tables"""
    table_field_map = discover_and_group_tables_with_fields(cursor)
    table_hash_map = {}

    for table in table_field_map:
        fields = table_field_map[table]

        table_hash = create_hash_from_table_rows(table, fields, cursor)

        table_hash_map[table.replace("sgid10", "sgid")] = table_hash

    return table_hash_map


def create_hash_from_table_rows(table, fields, cursor):
    """get hash string from tables"""
    print(f"hashing: {table}")
    query = f'SELECT {",".join(fields)} FROM {table} ORDER BY OBJECTID'
    rows = cursor.execute(query).fetchall()

    hashes = ""

    for row in rows:
        hash_me = [str(value) for value in row]

        table_hash = xxh64("".join(hash_me)).hexdigest()

        hashes += table_hash

    return xxh64(hashes).hexdigest()


def discover_and_group_tables_with_fields(cursor):
    """
    get tables and fields
    """
    skip_fields = ["gdb_geomattr_data", "globalid", "global_id", "objectid_"]

    table_meta_query = """
        SELECT table_name
        FROM sde.sde_table_registry registry
        WHERE NOT (table_name like 'SDE_%' OR table_name like 'GDB_%') AND
            description IS NULL AND rowid_column = 'OBJECTID'
    """

    tables_rows = cursor.execute(table_meta_query).fetchall()
    tables = [table for table, in tables_rows]
    field_meta_query = f"""
        SELECT table_catalog as [db], table_schema as [schema], table_name as [table], column_name as [field],
            data_type as field_type
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name IN ({join_strings(tables)}) AND column_name NOT IN ({join_strings(skip_fields)})
    """
    field_meta = cursor.execute(field_meta_query).fetchall()

    table_field_map = {}

    for database, schema, table, field, field_type in field_meta:
        full_table_name = f"{database}.{schema}.{table}"
        if field_type == "geometry":
            field = f"{field}.STAsText() as {field}"

        if full_table_name not in table_field_map:
            table_field_map[full_table_name] = [field]

            continue

        table_field_map[full_table_name].append(field)

    return table_field_map


def join_strings(strings):
    """join table names for a SQL query"""
    return "'" + "','".join(strings) + "'"
