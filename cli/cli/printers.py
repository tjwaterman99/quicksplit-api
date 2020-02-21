from click import style, echo
from typing import List, Dict
from terminaltables import SingleTable
from click import echo


class Printer(SingleTable):
    """
    Handles printing a list of json objects.

    TODO:
    - validate that all items in the data have the same keys
    """

    def __init__(self, table_data_json: List[Dict], title=None,
                 order=None, bold_header=True, color="bright_magenta",
                 rename=None):
        self.table_data_json = table_data_json
        if len(self.table_data_json) == 0 or self.table_data_json[0] == {}:
            raise AttributeError("Can not print table with no data")

        self.rename = rename
        self.order = order if order else []
        self.bold_header = bold_header
        self.color = color
        super().__init__(self.formatted_table_data, title=title)

    def echo(self):
        echo(self.table)

    @property
    def formatted_table_data(self):
        return [self.columns] + list(self.rows)

    @property
    def columns(self):
        if self.order:
            keys = self.order.copy()
        else:
            keys = list(self.table_data_json[0].keys())
        if self.rename:
            keys_copy = keys.copy()
            for current, future in self.rename.items():
                for n, key in enumerate(keys_copy):
                    if key == current:
                        keys[n] = future
        if self.bold_header or self.color:
            keys = [style(k.capitalize(), bold=self.bold_header, fg=self.color) for k in keys]
        return keys

    @property
    def rows(self):
        for d in self.table_data_json:
            if self.order:
                dcopy = {k: d[k] for k in self.order}
            else:
                dcopy = d
            yield ['' if v==None else v for k,v in dcopy.items()]
