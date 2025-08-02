def join_urls(base: str, *args: str) -> str:
    steps = []

    for step in ([base] + [arg for arg in args if isinstance(arg, str)]):
        if step.startswith("/"):
            step = step[1:]
        if step.endswith("/"):
            step = step[:-1]
        steps.append(step)

    return "/".join(steps)
