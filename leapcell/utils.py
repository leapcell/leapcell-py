from urllib.parse import urljoin, quote_plus
from leapcell.version import VERSION

def multi_urljoin(*parts):
    return urljoin(parts[0], "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:]))

def build_header(token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Leapcell Python-Client/{}".format(
            VERSION,
        ),
    }
    return headers