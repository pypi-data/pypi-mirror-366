'''
    Excel reader module
'''

from dataclasses import dataclass, field
import pandas
import numpy

class ReadExcelException(Exception):
    '''
        ReadExcel's general exception
    '''
    def __init__(self,
                 message: str = "General exception") -> None:
        '''
            ReadExcel's general exception

            :param message: :class:`str` Exception's message
        '''
        super().__init__(message)


@dataclass(slots = False)
class Sheet:
    '''
        Excel sheet
    '''
    name: str
    data: list[list[any]] = field(default_factory = list)


class ReadExcel:
    '''
        Excel reader class
    '''
    def __init__(self,
                 file_path: str) -> None:
        '''
            Excel reader class

            :param file_path: :class:`str` Excel file's path
        '''
        self.file_path: str = file_path
        self.__sheet_names: list[str] = pandas.ExcelFile(self.file_path).sheet_names
        self.data: list[Sheet] = []
        for sheet_name in self.__sheet_names:
            sheet_data = pandas.read_excel(self.file_path,
                                           sheet_name = sheet_name,
                                           header = None).replace({numpy.nan: None}).values.tolist()
            sheet: Sheet = Sheet(name = sheet_name,
                                 data = sheet_data or [])
            self.data.append(sheet)


    def get_sheet_by_id(self,
                        sheet_id: int | str ) -> Sheet | None:
        '''
            Get sheet by ID

            :param sheet_id: :class:`Union(int, str)`
        '''
        if isinstance(sheet_id, float):
            sheet_id = int(round(sheet_id, 0))
        if isinstance(sheet_id, int):
            if sheet_id in range(len(self.data)):
                return self.data[sheet_id]
        if isinstance(sheet_id, str):
            for sheet in self.data:
                if sheet.name == sheet_id:
                    return sheet
        if type(sheet_id) not in [float, int, str]:
            raise ReadExcelException(message = f"sheet_id '{type(sheet_id)}' type is not supported.") # pylint: disable=line-too-long
        raise ReadExcelException(message = f"sheet_id not found for '{sheet_id}'")


    def get_data_by_id(self,
                       sheet_id: int | str ) -> list[list[any]] | None:
        '''
            Get sheet data by ID

            :param sheet_name: :class:`Union(int, str)` Sheet's ID
        '''
        found_sheet: Sheet | None = self.get_sheet_by_id(sheet_id = sheet_id)
        return found_sheet.data if found_sheet else None


    def remove_sheets_except_id(self,
                                sheet_id: int | str) -> None:
        '''
            Remove sheets from data, except ID

            :param sheet_id: :class:`Union(int, str)`
        '''
        self.data = [self.get_sheet_by_id(sheet_id = sheet_id)]


    def remove_sheet_by_id(self,
                           sheet_id: int | str ) -> None:
        '''
            Removes sheet by ID

           :param sheet_id: :class:`Union(int, str)`
        '''
        sheet_to_pop: Sheet = self.get_sheet_by_id(sheet_id = sheet_id)
        for i, _ in enumerate(self.data):
            if self.data[i].name == sheet_to_pop.name:
                self.data.pop(i)
                break
