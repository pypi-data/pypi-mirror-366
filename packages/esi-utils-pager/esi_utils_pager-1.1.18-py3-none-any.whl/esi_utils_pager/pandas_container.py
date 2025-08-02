import pandas as pd


class PandasContainer(object):
    def __init__(self, excelfile):
        # excel file with multiple tabs
        self._excelfile = excelfile
        self._excelfile = pd.ExcelFile(excelfile)

    def getDataFrame(self, name):
        if name not in self._excelfile.sheet_names:
            raise LookupError((f"Dataframe {name} not in {self._excelfile}"))
        return self._excelfile.parse(name)
