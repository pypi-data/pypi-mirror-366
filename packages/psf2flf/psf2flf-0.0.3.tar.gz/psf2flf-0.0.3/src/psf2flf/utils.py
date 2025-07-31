def print_dict(data: dict, prefix: str = ""):
    """Recursively prints the key-value pairs of a dictionary."""
    for key, value in data.items():
        new_prefix = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            print_dict(value, new_prefix)
        else:
            print(f"{new_prefix}: {value}")
