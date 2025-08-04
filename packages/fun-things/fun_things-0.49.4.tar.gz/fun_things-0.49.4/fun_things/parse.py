def bool(input):
    """
    Boolean parser.

    If not listed, uses `not not input`.

    True =
    true,
    t,
    y,
    yes

    False =
    false,
    f,
    n,
    no,
    none,
    nil
    """
    if input is None:
        return False

    if isinstance(input, str):
        input = input.lower()

        if input in ["true", "t", "y", "yes"]:
            return True

        if input in ["false", "f", "n", "no", "none", "nil"]:
            return False

    return not not input
