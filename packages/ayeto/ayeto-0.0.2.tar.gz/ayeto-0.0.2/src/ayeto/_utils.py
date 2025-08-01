from __future__ import annotations
from datetime import datetime, timedelta
import time
import uuid
from typing import Optional


def timestamp_factory(from_now: Optional[timedelta] = None) -> int:
    """ Timestamp im ms """
    # future ?
    if from_now:
        if not isinstance(from_now, timedelta): return 0

        now = datetime.now()
        return int(
            (now+from_now).timestamp() * 1000
        ) 

    # return current timestamp
    return int(
        time.time() * 1000
    )

def id_factory():
    """ Returns random uuid4 """
    return uuid.uuid4()