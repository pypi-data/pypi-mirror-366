from .types import ParamsType, ParamChange
import pandas


def _build_line_to_add(
    obj: str,
    daily: bool,
    monthly: bool,
    yearly: bool,
    avann: bool
) -> str:

    '''
    Helper function to format lines for `print.prt` file
    '''

    print_periodicity = {
        'daily': daily,
        'monthly': monthly,
        'yearly': yearly,
        'avann': avann,
    }

    arg_to_add = obj.ljust(29)
    for value in print_periodicity.values():
        periodicity = 'y' if value else 'n'
        arg_to_add += periodicity.ljust(14)

    return arg_to_add.rstrip() + '\n'


def _apply_param_change(
    df: pandas.DataFrame,
    param_name: str,
    change: ParamChange
) -> None:

    '''
    Apply parameter change to a DataFrame
    '''

    value = change['value']
    change_type = change['change_type'] if 'change_type' in change else 'absval'
    filter_by = change.get('filter_by')

    mask = df.query(filter_by).index if filter_by else df.index

    if change_type == 'absval':
        df.loc[mask, param_name] = value
    elif change_type == 'abschg':
        df.loc[mask, param_name] += value
    elif change_type == 'pctchg':
        df.loc[mask, param_name] *= (1 + value / 100)


def _validate_params(
    params: ParamsType
) -> None:

    '''
    Validate the structure and values of SWAT+ parameter modification input.
    '''

    if params is None:
        return

    if not isinstance(params, dict):
        raise TypeError("'params' must be a dictionary mapping filenames to parameter specs.")

    valid_change_types = ["absval", "abschg", "pctchg"]

    for filename, file_params in params.items():
        if not isinstance(file_params, dict):
            raise TypeError(f"Expected a dictionary for file '{filename}', got {type(file_params).__name__}")

        for key, value in file_params.items():
            if key == "has_units":
                if not isinstance(value, bool):
                    raise TypeError(f"'{key}' for file '{filename}' must be a boolean.")
                continue

            # For any other key, value should NOT be bool
            if isinstance(value, bool):
                raise TypeError(f"Unexpected bool value for key '{key}' in file '{filename}'")

            param_changes = value if isinstance(value, list) else [value]

            for change in param_changes:
                if not isinstance(change, dict):
                    raise TypeError(f"'{key}' for file '{filename}' must be either a dictinary or a list of dictionaries, got {type(change).__name__}")

                if "value" not in change:
                    raise ValueError(f"Missing 'value' key for '{key}' in file '{filename}'.")

                if not isinstance(change["value"], (int, float)):
                    raise TypeError(f"'value' for '{key}' in file '{filename}' must be numeric.")

                change_type = change.get("change_type", "absval")
                if change_type not in valid_change_types:
                    raise ValueError(
                        f"Invalid 'change_type' value '{change_type}' for '{key}' in file '{filename}'. Expected one of: {', '.join(valid_change_types)}."
                    )

                filter_by = change.get("filter_by")
                if filter_by is not None and not isinstance(filter_by, str):
                    raise TypeError(f"'filter_by' for '{key}' in file '{filename}' must be a string.")
