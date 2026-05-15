def parse_url(url):
    parts = url.split("://")
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def is_secure(url):
    return url.startswith("https://")


def get_path(url):
    return url.split("/", 3)[3]
