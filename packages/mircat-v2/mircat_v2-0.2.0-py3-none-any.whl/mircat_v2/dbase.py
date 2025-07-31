import json
import sqlite3
from pathlib import Path

from loguru import logger
from mircat_v2.configs import dbase_config_file

MIRCAT_DB_TABLES = {
    "conversions": {
        "series_uid": "TEXT",
        "study_uid": "TEXT",
        "nifti": "TEXT",
        "modality": "TEXT",
        "mrn": "TEXT",
        "accession": "TEXT",
        "series_name": "TEXT",
        "series_number": "INTEGER",
        "scan_date": "TEXT",
        "original_series_name": "TEXT",
        "study_description": "TEXT",
        "ct_direction": "TEXT",
        "image_type": "TEXT",
        "sex": "TEXT",
        "age": "INTEGER",
        "birth_date": "TEXT",
        "height_m": "REAL",
        "weight_kg": "REAL",
        "pregnancy_status": "INTEGER",
        "pixel_length_mm": "REAL",
        "pixel_width_mm": "REAL",
        "slice_thickness_mm": "REAL",
        "manufacturer": "TEXT",
        "model": "TEXT",
        "kvp": "REAL",
        "sequence_name": "TEXT",
        "protocol_name": "TEXT",
        "contrast_bolus_agent": "TEXT",
        "contrast_bolus_route": "TEXT",
        "contrast_bolus_volume": "REAL",
        "dicom_folder": "TEXT",
        "conversion_date": "TEXT",
        "PRIMARY KEY": "(series_uid)",
    },
    "segmentations": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "task": "INTEGER",
        "seg_file": "TEXT",
        "seg_date": "TEXT",
        "status": "TEXT",
        "failed_error": "TEXT",
        "PRIMARY KEY": "(nifti, task, seg_date)",
    },
    "metadata": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "study_uid": "TEXT",
        "output_stats_file": "TEXT",
        "modality": "TEXT",
        "mrn": "TEXT",
        "accession": "TEXT",
        "series_name": "TEXT",
        "series_number": "INTEGER",
        "scan_date": "TEXT",
        "original_series_name": "TEXT",
        "study_description": "TEXT",
        "ct_direction": "TEXT",
        "abdominal_scan": "INTEGER",
        "chest_scan": "INTEGER",
        "correct_vertebrae_order": "INTEGER",
        "lowest_vertebra": "TEXT",
        "highest_vertebra": "TEXT",
        "image_type": "TEXT",
        "sex": "TEXT",
        "age": "INTEGER",
        "birth_date": "TEXT",
        "height_m": "REAL",
        "weight_kg": "REAL",
        "pregnancy_status": "INTEGER",
        "pixel_length_mm": "REAL",
        "pixel_width_mm": "REAL",
        "slice_thickness_mm": "REAL",
        "manufacturer": "TEXT",
        "model": "TEXT",
        "kvp": "REAL",
        "sequence_name": "TEXT",
        "protocol_name": "TEXT",
        "contrast_bolus_agent": "TEXT",
        "contrast_bolus_route": "TEXT",
        "contrast_bolus_volume": "REAL",
        "dicom_folder": "TEXT",
        "conversion_date": "TEXT",
        "PRIMARY KEY": "(nifti)",
    },
    "vol_int": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "structure": "TEXT",
        "volume_cm3": "REAL",
        "hu_mean": "REAL",
        "hu_std_dev": "REAL",
        "PRIMARY KEY": "(nifti, structure)",
    },
    "contrast": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "phase": "TEXT",
        "probability": "REAL",
        "pi_time": "REAL",
        "pi_time_std": "REAL",
        "PRIMARY KEY": "(nifti)",
    },
    "vertebrae": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "vertebra": "TEXT",
        "midline": "INTEGER",
        "PRIMARY KEY": "(nifti, vertebra)",
    },
    "aorta_metrics": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "region": "TEXT",
        "entire_region": "INTEGER",
        "length_mm": "REAL",
        "tortuosity_index": "REAL",
        "icm": "REAL",
        "n_inflections": "INTEGER",
        "peria_volume_cm3": "REAL",
        "peria_ring_volume_cm3": "REAL",
        "peria_fat_volume_cm3": "REAL",
        "peria_hu_mean": "REAL",
        "peria_hu_std": "REAL",
        "calc_volume_mm3": "REAL",
        "calc_agatston": "REAL",
        "calc_count": "INTEGER",
        "is_120_kvp": "INTEGER",
        "mean_diameter_mm": "REAL",
        "mean_roundness": "REAL",
        "mean_flatness": "REAL",
        "PRIMARY KEY": "(nifti, region)",
    },
    "aorta_diameters": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "region": "TEXT",
        "measure": "TEXT",
        "mean_diameter_mm": "REAL",
        "major_diameter_mm": "REAL",
        "minor_diameter_mm": "REAL",
        "area_mm2": "REAL",
        "roundness": "REAL",
        "flatness": "REAL",
        "rel_distance": "REAL",
        "entire_region": "INTEGER",
        "PRIMARY KEY": "(nifti, region, measure)",
    },
    "tissues_volumetric": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "region": "TEXT",
        "structure": "TEXT",
        "volume_cm3": "REAL",
        "hu_mean": "REAL",
        "hu_std_dev": "REAL",
        "PRIMARY KEY": "(nifti, region, structure)",
    },
    "tissues_vertebral": {
        "nifti": "TEXT",
        "series_uid": "TEXT",
        "vertebra": "TEXT",
        "structure": "TEXT",
        "measurement": "TEXT",
        "value": "REAL",
        "PRIMARY KEY": "(nifti, vertebra, structure, measurement)",
    },
}


def add_dbase_subparser(subparsers):
    # Add subcommands
    dbase_parser = subparsers.add_parser("dbase", help="Database management commands")
    dbase_subparsers = dbase_parser.add_subparsers(dest="dbase_command")

    # Add subcommand for creating a new database
    create_parser = dbase_subparsers.add_parser("create", help="Create a new database")
    create_parser.add_argument(
        "dbase_path",
        type=Path,
        help="Path to the database file",
    )
    create_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the database if it already exists",
    )
    create_parser.add_argument(
        "--no-setup",
        action="store_true",
        help="Do not set up the database schema",
    )
    create_parser.add_argument(
        "--update",
        action="store_true",
        help="Update the database schema if it already exists",
    )

    # add subcommand for querying the database
    query_parser = dbase_subparsers.add_parser("query", help="Query the database")
    query_parser.add_argument(
        "query",
        type=str,
        help="SQL query to execute",
    )


def create_database(dbase_path, update=False, overwrite=False, no_setup=False):
    """
    Create a new SQLite database at the specified path.

    Args:
        dbase_path (Path): Path to the database file.
        update (bool): If True, update the database schema if it already exists.
        overwrite (bool): If True, overwrite the database if it already exists.
        no_setup (bool): If True, do not set up the database schema.
    """
    if dbase_path.exists() and not update and not overwrite:
        raise FileExistsError(
            f"Database file {dbase_path} already exists. Use --update to update the schema or --overwrite to completely overwrite."
        )
    elif dbase_path.exists() and update:
        logger.info(f"Updating existing database at {dbase_path}")
        conn = sqlite3.connect(dbase_path)
        cursor = conn.cursor()
        create_tables_from_schema(cursor, MIRCAT_DB_TABLES)
        conn.commit()
        conn.close()
        save_config(dbase_path)
        logger.success(f"Database updated at {dbase_path}")
        return
    elif dbase_path.exists() and overwrite:
        response = input(
            "Are you sure you want to overwrite the existing database? (y/n): "
        )
        if response.lower() != "y":
            logger.info(f"Left existing database at {dbase_path} intact.")
            return
        logger.info(f"Overwriting existing database at {dbase_path}")
        dbase_path.unlink()
    # Create the database
    conn = sqlite3.connect(dbase_path)
    logger.success(f"Database created at {dbase_path}")
    cursor = conn.cursor()

    if not no_setup:
        create_tables_from_schema(cursor, MIRCAT_DB_TABLES)

    conn.commit()
    conn.close()

    save_config(dbase_path)


def save_config(dbase_path):
    config = {"dbase_path": str(dbase_path.resolve()), "tables": MIRCAT_DB_TABLES}
    with dbase_config_file.open("w") as f:
        json.dump(config, f, indent=4)
    logger.success(f"Database configuration saved to {dbase_config_file}")


def create_tables_from_schema(cursor, schema_dict):
    """Create tables from a schema dictionary."""
    for table_name, columns in schema_dict.items():
        logger
        column_defs = [
            f"{col_name} {col_type}" for col_name, col_type in columns.items()
        ]
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {", ".join(column_defs)}
            )
        """
        cursor.execute(create_table_sql)
        logger.info(f"Created table: {table_name}")


def insert_data_batch(dbase_config: dict, table: str, data_records: list[dict]):
    """Insert a batch of data into the database for a specific table."""
    if not data_records:
        return
    dbase_path = Path(dbase_config["dbase_path"])
    conn = sqlite3.connect(dbase_path)
    cursor = conn.cursor()
    try:
        # Get the columns that exist in the table
        table_schema = dbase_config["tables"].get(table)
        if not table_schema:
            raise ValueError(
                f"Table {table} does not exist in the standard MirCAT database schema."
            )
        # Check if the table exists
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        if not cursor.fetchone():
            logger.info(f"Table {table} does not exist. Creating it.")
            create_tables_from_schema(cursor, {table: table_schema})
            conn.commit()
            logger.info(f"Table {table} created successfully.")
        table_columns = list(table_schema.keys())

        # Process each record in the batch
        insert_data = []
        for metadata in data_records:
            # Filter metadata to only include columns that exist in the table and
            # put in correct order. We use get to insert null values for missing columns
            insert_data.append(
                {
                    col: metadata.get(col)
                    for col in table_columns
                    if col != "PRIMARY KEY"
                }
            )
        logger.debug("Insert data: {}", insert_data)

        if insert_data:
            # Use the first record to determine column order
            columns = list(insert_data[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            insert_sql = (
                f"REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            )

            # Prepare values for batch insert
            values_list = []
            for metadata in insert_data:
                values = [metadata.get(col) for col in columns]
                values_list.append(values)

            # Execute batch insert
            cursor.executemany(insert_sql, values_list)
            conn.commit()
            logger.success(f"Inserted {len(values_list)} records into {table} table")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting batch: {e}")
        raise
    finally:
        conn.close()
