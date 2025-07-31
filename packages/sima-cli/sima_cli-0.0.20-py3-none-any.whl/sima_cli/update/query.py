import re
import requests
from sima_cli.utils.config_loader import load_resource_config, artifactory_url
from sima_cli.utils.config import get_auth_token

ARTIFACTORY_BASE_URL = artifactory_url() + '/artifactory'

def _list_available_firmware_versions_internal(board: str, match_keyword: str = None):
    fw_path = f"{board}" 
    aql_query = f"""
                items.find({{
                    "repo": "soc-images",
                    "path": {{
                        "$match": "{fw_path}/*"
                    }},
                    "type": "folder"
                }}).include("repo", "path", "name")
                """.strip()

    aql_url = f"{ARTIFACTORY_BASE_URL}/api/search/aql"
    headers = {
        "Content-Type": "text/plain",
        "Authorization": f"Bearer {get_auth_token(internal=True)}"
    }

    response = requests.post(aql_url, data=aql_query, headers=headers)
    if response.status_code != 200:
        return None

    results = response.json().get("results", [])

    # Reconstruct full paths and remove board prefix
    full_paths = {
        f"{item['path']}/{item['name']}".replace(fw_path + "/", "")
        for item in results
    }

    # Extract top-level folders
    top_level_folders = sorted({path.split("/")[0] for path in full_paths})

    if match_keyword:
        match_keyword = match_keyword.lower()
        top_level_folders = [
            f for f in top_level_folders if match_keyword in f.lower()
        ]

    return top_level_folders

def _list_available_firmware_versions_external(board: str, match_keyword: str = None):
    """
    Construct and return a list containing a single firmware download URL for a given board.
    
    If match_keyword is provided and matches a 'major.minor' version pattern (e.g., '1.6'),
    it is normalized to 'major.minor.patch' format (e.g., '1.6.0') to ensure consistent URL construction.

    Args:
        board (str): The name of the hardware board.
        match_keyword (str, optional): A version string to match (e.g., '1.6' or '1.6.0').

    Returns:
        list[str]: A list containing one formatted firmware download URL.
    """
    fwtype = 'yocto'
    cfg = load_resource_config()
    download_url_base = cfg.get('public').get('download').get('download_url')

    if match_keyword:
        if re.fullmatch(r'\d+\.\d+', match_keyword):
            match_keyword += '.0'

    firmware_download_url = (
        f'{download_url_base}SDK{match_keyword}/devkit/{board}/{fwtype}/'
        f'simaai-devkit-fw-{board}-{fwtype}-{match_keyword}.tar.gz'
    )
    return [firmware_download_url]


def list_available_firmware_versions(board: str, match_keyword: str = None, internal: bool = False):
    """
    Public interface to list available firmware versions.

    Parameters:
    - board: str – Name of the board (e.g. 'davinci')
    - match_keyword: str – Optional keyword to filter versions (case-insensitive)
    - internal: bool – Must be True to access internal Artifactory

    Returns:
    - List[str] of firmware version folder names, or None if access is not allowed
    """
    if not internal:
        return _list_available_firmware_versions_external(board, match_keyword)

    return _list_available_firmware_versions_internal(board, match_keyword)
