def unique_names(names: list[str]) -> list[str]:
    if not isinstance(names, list):
        raise TypeError("names must be a list")
    if any(not isinstance(name, str) for name in names):
        raise TypeError("names must contain only strings")
    return list(dict.fromkeys(names))
