def setup_mcp_client(url, delo_key_id, delo_secret):
    from fastmcp import Client as FastMcpClient

    config = {
        "mcpServers": {
            "server_name": {
                "transport": "sse",
                "url": url,
                "headers": {
                    "X-DeceptionLogic-KeyId": delo_key_id,
                    "X-DeceptionLogic-SecretKey": delo_secret,
                },
            }
        }
    }

    return FastMcpClient(config)


def find_index(needle: str, haystack: list):
    for index, dictionary in enumerate(haystack):
        for value in dictionary.values():
            if type(value) is not str:
                continue
            if needle in value:
                return index
    return -1


def get_guid(resp, needle):
    import json

    f_resp = json.loads(resp[0].text)
    index = find_index(needle, f_resp)
    return f_resp[index]["guid"]
