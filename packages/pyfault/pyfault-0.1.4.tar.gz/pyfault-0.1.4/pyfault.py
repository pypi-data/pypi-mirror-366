import json
import os
import sys

import requests

from _vendor.tblib import Traceback
from _vendor.tblib import __version__ as tblib_version

from ._version import version as pyfault_version


def custom_exception_handler(exc_type, exc_value, exc_traceback, host="127.0.0.1:8787"):
    try:

        def get_locals_limited(frame):
            result = {}
            total_size = 0
            for k, v in frame.f_locals.items():
                if isinstance(v, (str, int, float, bool, type(None))):
                    item_size = sys.getsizeof(k) + sys.getsizeof(v)
                    if total_size + item_size <= 4096:
                        result[k] = v
                        total_size += item_size
            return result

        tb = Traceback(
            exc_traceback,
            get_locals=get_locals_limited,
        )
        signature_data = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "tblib_version": tblib_version,
            "pyfault_version": pyfault_version,
            "traceback": tb.to_dict(),
            "exc_value": str(exc_value),
            "exc_doc": str(exc_type.__doc__),
        }
        payload = {
            "signature": json.dumps(signature_data),
            "crash": True,
            "reason": exc_type.__name__,
            "program": os.path.basename(exc_traceback.tb_frame.f_code.co_filename),
            "source": "PYFAULT",
            "log_file_name": None,
            "compression": None,
        }
        response = requests.post(f"http://{host}/v1/trace/save", json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Memfaultd API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Failed to send trace via HTTP API: {e}")

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def init(host="127.0.0.1:8787"):
    sys.excepthook = lambda exc_type, exc_value, exc_traceback: custom_exception_handler(
        exc_type, exc_value, exc_traceback, host
    )
