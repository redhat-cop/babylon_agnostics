#!/usr/bin/env python

import json
import base64

def convert_secret(data):
    result = { k: base64.b64decode(v).decode('utf-8') for (k, v) in data.items() }

    for k, v in result.items():
        try:
            result[k] = json.loads(v)
        except json.decoder.JSONDecodeError:
            pass
    return result

class FilterModule(object):
    filter_map = {
        'convert_secret': convert_secret,
    }

    def filters(self):
        return self.filter_map
