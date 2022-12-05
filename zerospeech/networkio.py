import json
import sys
import warnings
from datetime import datetime

from .settings import get_settings
from .out import console, error_console
from .model import repository

import requests
from pydantic import ValidationError

st = get_settings()


def update_repo_index():
    """ Updates the repositories index from remote """
    r = requests.get(st.repo_origin)
    data = r.json()
    try:
        _ = repository.RepositoryIndex(**data)
    except ValidationError:
        error_console.log(f"The given repository @ {st.repository_index} is not valid")
        error_console.log(f"Please contact the administrator to resolve this issue...")
        sys.exit(1)

    with st.repository_index.open('w') as fp:
        json.dump(data, fp)
    console.log("RepositoryIndex has been updated successfully !!")


def check_update_repo_index() -> bool:
    """ Checks if local repo is out of date """
    # no need to check for updates more than once a week
    if st.repository_index.is_file():
        created_dt = datetime.fromtimestamp(st.repository_index.stat().st_mtime).date()
        now = datetime.now().date()
        if (now - created_dt).days > 7:
            return False
    else:
        # if file not preset always update
        return True

    # if
    try:
        r = requests.get(st.repo_origin)
        if r.status_code != 200:
            raise ValueError("Failed to find online repo")
        last_update_online = datetime.fromisoformat(r.json().get('last_modified'))
    except ValueError:
        warnings.warn("Failed to connect to online repository index !!")
        return False

    try:
        with st.repository_index.open() as fp:
            last_update_local = datetime.fromisoformat(json.load(fp).get('last_modified'))
    except ValueError:
        warnings.warn("Local index missing or corrupted !!!")
        return False

    return last_update_online > last_update_local
