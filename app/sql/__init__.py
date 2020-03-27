"""
Custom sql for when the ORM doesn't generate sensible queries.

The .sql files in this directory are set as attributes on this package.

So if you create a file named 'experiment_results.sql' in this directory
then you can import the sql directly by using

    from app.sql import experiment_results
"""

import os
import sys


sql_directory = os.path.dirname(__file__)

for fn in os.listdir(sql_directory):
    if fn.endswith('.sql'):
        sql_file_path = os.path.join(sql_directory, fn)
        with open(sql_file_path, 'r') as f:
            setattr(sys.modules[__name__], fn.replace('.sql', ''), f.read())
