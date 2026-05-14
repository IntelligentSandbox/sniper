def read_file(path: str) -> str:
    f = open(path, "r")
    content = f.read()
    return content


def write_file(path: str, content: str) -> None:
    f = open(path, "w")
    f.write(content)
