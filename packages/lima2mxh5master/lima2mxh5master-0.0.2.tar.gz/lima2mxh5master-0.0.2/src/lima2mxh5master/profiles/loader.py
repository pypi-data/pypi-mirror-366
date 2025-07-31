import importlib
import importlib.resources
import json


def load_profile(profile_name: str) -> dict:
    """Load the JSON schema for a given profile.

    This function dynamically locates a schema file within the installed
    package's `profiles` directory using `importlib.resources`.

    Parameters
    ----------
    profile_name : str
        The name of the profile whose schema should be loaded (e.g., 'eiger').

    Returns
    -------
    dict
        The JSON schema loaded into a Python dictionary.

    Raises
    ------
    ValueError
        If the schema for the specified profile cannot be found.
    """
    profile_package = f"lima2mxh5master.profiles.{profile_name}"
    schema_filename = f"schema_{profile_name}.json"

    try:
        schema_path = importlib.resources.files(profile_package) / schema_filename
        with schema_path.open("r") as f:
            schema = json.load(f)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise ValueError(
            f"Could not load schema for profile '{profile_name}'. Error: {e}"
        )

    return schema
