from zone.utils.dsx import as_list


def normalize(s):
    return s.lower().replace("_", "").replace("-", "")


def normalize_components(comps=None):
    norm_dict = [
        "canstack",
        # "can_stack",
        "canparser",
        # "can_parser",
        "linstack",
        # "lin_stack",
        "linparser",
        # "lin_parser",
    ]
    if comps is None or comps == ["all"]:
        return norm_dict
    if isinstance(comps, str):
        comps = as_list(comps)
    normalized_targets = [normalize(x) for x in comps]
    result = [
        item for item in norm_dict if normalize(item) in normalized_targets
    ]
    return result
