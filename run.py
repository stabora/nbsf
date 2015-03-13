#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
from app import app

app.run(
    debug=True,
    host='0.0.0.0',
    port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000
)
