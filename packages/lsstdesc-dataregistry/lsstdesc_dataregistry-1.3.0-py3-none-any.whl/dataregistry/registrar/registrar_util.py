import hashlib
import os
import re
import warnings
from shutil import copyfile, copytree, rmtree

from sqlalchemy import select

__all__ = [
    "_parse_version_string",
    "_bump_version",
    "_form_dataset_path",
    "get_directory_info",
    "_name_from_relpath",
    "_copy_data",
    "_relpath_from_name",
]
VERSION_SEPARATOR = "."
_nonneg_int_re = "0|[1-9][0-9]*"


def _parse_version_string(version):
    """
    Parase a version string into its components.

    Parameters
    ----------
    version : str
        Version string

    Returns
    -------
    d : dict
        Dict with keys "major", "minor", "patch"
    """

    cmp = version.split(VERSION_SEPARATOR)
    if len(cmp) != 3:
        raise ValueError("Version string must have 3 components")
    for c in cmp:
        if not re.fullmatch(_nonneg_int_re, c):
            raise ValueError(f"Version component {c} is not non-negative int")
    d = {"major": cmp[0]}
    d["minor"] = cmp[1]
    d["patch"] = cmp[2]

    return d


def _form_dataset_path(owner_type, owner, relative_path, schema=None, root_dir=None):
    """
    Construct full (or relative) path to dataset in the data registry.

    When schema and root_dir are not None, the full path is returned:
        <root_dir>/<schema>/<owner_type>/<owner>/<relative_path>

    When schema and root_dir are ommited, the relative path is returned:
        <owner_type>/<owner>/<relative_path>

    Parameters
    ----------
    owner_type : str
        Type of dataset
    owner : str
        Owner of dataset
    relative_path : str
        Relative path within the data registry
    schema : str, optional
        Schema we are connected to
    root_dir : str, optional
        Root directory of data registry
    dialect : str, optional
        SQL dialect, e.g postgres or sqlite

    Returns
    -------
    to_return : str
        Full (or relative) path of dataset in the data registry
    """

    if owner_type == "production":
        owner = "production"
    to_return = os.path.join(owner_type, owner, relative_path)
    if schema:
        to_return = os.path.join(schema, to_return)
    if root_dir:
        to_return = os.path.join(root_dir, to_return)
    return to_return


def get_directory_info(path):
    """
    Get the total disk space used by a directory and the total number of files
    in the directory (includes subdirectories):

    Parameters
    ----------
    path : str
        Location of directory

    Returns
    -------
    num_files : int
        Total number of files in dir (including subdirectories)
    total_size : float
        Total disk space (in bytes) used by directory (including subdirectories)
    """

    num_files = 0
    total_size = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                num_files += 1
                total_size += entry.stat().st_size
            elif entry.is_dir():
                subdir_num_files, subdir_total_size = get_directory_info(entry.path)
                num_files += subdir_num_files
                total_size += subdir_total_size
    return num_files, total_size


def _bump_version(name, v_string, dataset_table, engine):
    """
    Bump version of dataset automatically if user has supplied a special
    version string during register.

    Parameters
    ----------
    name : str
        Name of the dataset
    v_string : str
        Special version string "major", "minor", "patch"
    dataset_table : SQLAlchemy Table object
    engine : SQLAlchemy Engine object

    Returns
    -------
    v_fields : dict
        Updated version dict with keys "major", "minor", "patch"
    """

    # Find the previous dataset based on the name and version
    stmt = select(
        dataset_table.c["version_major", "version_minor", "version_patch"]
    ).where(dataset_table.c.name == name)
    stmt = (
        stmt.order_by(dataset_table.c.version_major.desc())
        .order_by(dataset_table.c.version_minor.desc())
        .order_by(dataset_table.c.version_patch.desc())
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
        r = result.fetchone()
        if not r:
            old_major = 0
            old_minor = 0
            old_patch = 0
        else:
            old_major = int(r.version_major)
            old_minor = int(r.version_minor)
            old_patch = int(r.version_patch)

    # Add 1 to the relative version part.
    v_fields = {"major": old_major, "minor": old_minor, "patch": old_patch}
    v_fields[v_string] = v_fields[v_string] + 1

    # Reset fields as needed
    if v_string == "minor":
        v_fields["patch"] = 0
    if v_string == "major":
        v_fields["patch"] = 0
        v_fields["minor"] = 0

    return v_fields


def _name_from_relpath(relative_path):
    """
    Scrape the dataset name from the relative path.

    We use this when the dataset name is not explicitly defined, and we take it
    from the final directory if path.

        e.g, /root/to/dataset/dir would return "dir"

        Parameters
        ----------
        relative_path : str
                Path to dataset (can be relative or absolute)

        Returns
        -------
        name : str
                Scraped name of dataset
    """

    relpath = relative_path
    if relative_path.endswith("/"):
        relpath = relative_path[:-1]
    base = os.path.basename(relpath)
    if "." in base:
        cmp = base.split(".")
        name = ".".join(cmp[:-1])
    else:
        name = base

    return name


def _read_configuration_file(configuration_file, max_config_length):
    """
    Read a text, YAML, TOML, etc, configuration file.

    Parameters
    ----------
    configuration_file : str
        Path to configuration file
    max_config_length : int
        Maximum number of characters to read from file. Files beyond this limit
        will be truncated (with a warning message).

    Returns
    -------
    contents : str
    """

    # Make sure file exists
    if not os.path.isfile(configuration_file):
        raise FileNotFoundError(f"{configuration_file} not found")

    # Open configuration file and read up to max_config_length characters
    with open(configuration_file) as f:
        contents = f.read(max_config_length)

    if len(contents) == max_config_length:
        warnings.warn(
            "Configuration file is longer than `max_config_length`, truncated",
            UserWarning,
        )

    return contents


def _copy_data(dataset_organization, source, dest, do_checksum=False):
    """
    Copy data from one location to another (for ingesting directories and files
    into the `root_dir` shared space.

    Note prior to this, in `_handle_data`, it has already been check that
    `source` exists, so we do not have to check again.

    To ensure robustness, if overwriting data, the original file/folder is
    moved to a temporary location, then deleted if the copy was successful. If
    the copy was not successful the backup is renamed back.

    For individual files a checksum validation can be performed if
    `do_checksum=True`, there is no such check for directories.

    Parameters
    ----------
    dataset_organization : str
        The dataset organization, either "file" or "directory"
    source : str
        Path of source file or directory
    dest : str
        Destination we are copying to
    do_checksum : bool
        When overwriting files, do a checksum with the old and new file
    """

    def _compute_checksum(file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    temp_dest = dest + "_DATAREG_backup"

    try:
        # Backup original before copy
        if os.path.exists(dest):
            os.rename(dest, temp_dest)

        # Create any intervening directories
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        # Copy a single file
        if dataset_organization == "file":
            copyfile(source, dest)

            # Checksums on the files
            if do_checksum and os.path.exists(temp_dest):
                cs_dest = _compute_checksum(dest)
                cs_dest_backup = _compute_checksum(temp_dest)

                if cs_dest != cs_dest_backup:
                    raise Exception("Checksum with backup failed")

        # Copy a single directory (and subdirectories)
        elif dataset_organization == "directory":
            copytree(source, dest, copy_function=copyfile)

        # If successful, delete the backup
        if os.path.exists(temp_dest):
            if dataset_organization == "file":
                os.remove(temp_dest)
            else:
                rmtree(temp_dest)

    except Exception as e:
        if os.path.exists(temp_dest):
            if os.path.exists(dest):
                if dataset_organization == "file":
                    os.remove(dest)
                else:
                    rmtree(dest)
            os.rename(temp_dest, dest)

        print(
            "Something went wrong during data copying, aborting."
            "Note an entry in the registry database will still have"
            f"been created ({e})"
        )

        raise Exception(e)


def _relpath_from_name(name, version, old_location):
    """
    Construct a relative path from the name and version of a dataset.
    We use this when the `relative_path` is not explicitly defined.

    Every automatically generated `relative_path` is prefixed with
    `.gen_paths/`, meaning that all automatically generated `relative_paths` go
    into this top level folder. This is to prevent clashes with user specified
    `relative_path`'s.

    The auto-generated `relative_path` will be a directory that contains the
    name and version, which is where the ingested data (from `old_location`)
    will eventually reside. If the data being ingested is a single file, the
    `relative_path` will be the full path to the file within the registry, not
    just the directory that contains the file.

    Parameters
    ----------
    name : str
        Dataset name
    version : str
        Dataset version
    old_location : str
        Path the data is coming from (needed to parse filename)

    Returns
    -------
    relative_path : str
        Automatically generated `relative_path`
    """

    # For single files, scrape the filename and add it to the `relative_path`
    if (old_location is not None) and os.path.isfile(old_location):
        return os.path.join(
            ".gen_paths", f"{name}_{version}", os.path.basename(old_location)
        )
    else:
        # For directories, only need the autogenerated directory name
        return os.path.join(".gen_paths", f"{name}_{version}")
