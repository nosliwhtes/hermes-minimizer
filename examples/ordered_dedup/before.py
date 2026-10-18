def unique_names(names: list[str]) -> list[str]:
    if not isinstance(names, list):
        raise TypeError("names must be a list")
    if any(not isinstance(name, str) for name in names):
        raise TypeError("names must contain only strings")
    seen = set()
    result = []
    for name in names:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result
