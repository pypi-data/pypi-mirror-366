'''
    Logger
'''

import os
import datetime
import uuid

def gen_uuid() -> str:
    '''
        Generates a UUID
    '''
    return str(uuid.uuid4())


class LoggerError(Exception):
    '''
        LogerError general exception
    '''
    def __init__(self,
                 message: str = "General exception") -> None:
        '''
            LogerError general exception

            :param message: :class:`str` Exception message. Defaults to `General exception`
        '''
        super().__init__(message)


class Logger:
    '''
        Logger class
    '''

    __slots__: list[str] = ["file_path",
                            "encoding",
                            "time_format",
                            "separator",
                            "__silent",
                            "__enable_remove",
                            "__strip_content"]

    def __init__(self,
                 file_path: str | None = None,
                 encoding: str = "utf-8-sig",
                 time_format: str = "%Y.%m.%d %H:%M:%S",
                 separator: str = "\t",
                 silent: bool = False,
                 enable_remove: bool = False,
                 strip_content: bool = False) -> None:
        '''
            Logger class

            .. code-block:: python
                demo_logger = Logger(file_path = "example.log",
                                     strip_content = True)

            :param file_path: :class:`Optional(Union(str, None))` File's path. Defaults to `None`
            :param encoding: :class:`Optional(str)` File's encoding. Defaults to `"utf-8-sig"`
            :param time_format: :class:`Optional(str)` Log's time format. Defaults to `"%Y.%m.%d %H:%M:%S"`
            :param spearator: :class:`Optional(str)` Log's separator betwen the time and the content. Defaults to `"\\t"`
            :param silent: :class:`Optional(bool)` If set to `True` then won't print to console. Defaults to `False`
            :param enable_remove: :class:`Optional(bool)` If set to `True` then it enables removing content. Defaults to `False`
            :param strip_content: :class:`Optional(bool)` If set to `True` then strips content before logging it. Defaults to `False`
        ''' # pylint: disable=line-too-long
        self.file_path: str = file_path if file_path else os.path.join(os.getcwd(),
                                                                       f"{gen_uuid()}.log")
        self.encoding: str = encoding
        self.time_format: str = time_format
        self.separator: str = separator
        self.__silent: bool = silent
        self.__enable_remove: bool = enable_remove
        self.__strip_content: bool = strip_content


    def __error(self,
                message: str | None = None) -> LoggerError:
        '''
            Prints error message

            Parameters:
                message (str): error message
        '''
        raise LoggerError(message = str(message or ""))


    def __str_time(self) -> str:
        '''
            Returns the current time as a string
        '''
        current_time: datetime.datetime = datetime.datetime.now()
        try:
            return current_time.strftime(format = self.time_format)
        except Exception as e: # pylint: disable=broad-except
            print(f"Error: {e}")
            return current_time.strftime(format = "%Y.%m.%d %H:%M:%S")


    def __log_to_file(self,
                      content: any) -> None:
        '''
            Appends file

            :param content: :class:`any` Content to log
        '''
        try:
            with open(file = self.file_path,
                      mode = "a+",
                      encoding = self.encoding) as file:
                file.write(str(content))
        except Exception as e:
            raise LoggerError(f"Error writing to file: {self.file_path}, error: {e}") from e


    def __strip(self,
                content: str) -> str:
        '''
            Strips the content

            :param content: :class:`str` Content to strip
        '''
        return content.strip() if self.__strip_content else content


    def log(self,
            content: any = None) -> None:
        '''
            Logs content to file

            .. code-block:: python
                demo_logger.log(content = "Example")

            :param content: :class:`Optional(any)` Content to log. Defaults to `None`
        '''
        self.__log(content = content if content is not None else "")


    def change_path(self,
                    file_path: str) -> None:
        '''
            Changes the log file path

            .. code-block:: python
                demo_logger.change_path(file_path = "example.log")

            :param file_path: :class:`str` New path to the log file
        '''
        self.__change_path(file_path = file_path)


    def change_encoding(self,
                        encoding: str) -> None:
        '''
            Changes the log file encoding

            .. code-block:: python
                demo_logger.change_encoding(encoding = "utf-8-sig")

            :param encoding: :class:`str` New encoding to the log file
        '''
        self.__change_encoding(encoding = encoding)


    def change_time_format(self,
                           time_format: str) -> None:
        '''
            Changes the time format

            .. code-block:: python
                demo_logger.change_time_format(time_format = "%Y.%m.%d %H:%M:%S")

            :param time_format: :class:`str` New time format for the log file
        '''
        self.__change_time_format(time_format = time_format)


    def change_separator(self,
                         separator: str) -> None:
        '''
            Changes the separator
            
            .. code-block:: python
                demo_logger.change_separator(separator = "\\t")

            :param separator: :class:`str` New separator for the log file
        '''
        self.__change_separator(separator = separator)


    def clear(self) -> None:
        '''
            Clears the log file
        '''
        self.__clear()


    def remove(self) -> None:
        '''
            Removes the log file
        '''
        self.__remove()


    def __log(self,
              content: any = None) -> None:
        '''
            Logs content to file

            :param content: :class:`Optional(any)` Content to log. Defaults to `None`
        '''
        content = f"{self.__str_time()}{self.separator}{self.__strip(content) if isinstance(content, str) else content}\n" # pylint: disable=line-too-long
        if not self.__silent:
            print(content.strip())
        self.__log_to_file(content = content)


    def __change_path(self,
                      file_path: str) -> None:
        '''
            Changes the log file path

            :param file_path: :class:`str` New path to the log file
        '''
        self.file_path = file_path
        print(f"Changed path from {self.file_path} to {file_path}")


    def __change_encoding(self,
                          encoding: str) -> None:
        '''
            Changes the log file encoding

            :param encoding: :class:`str` New encoding to the log file
        '''
        self.encoding = encoding
        print(f"Changed encoding to {encoding}")


    def __change_time_format(self,
                             time_format: str) -> None:
        '''
            Changes the time format

            .. code-block:: python
                demo_logger.change_time_format(time_format = "%Y.%m.%d %H:%M:%S")

            :param time_format: :class:`str` New time format for the log file
        '''
        self.time_format = time_format
        print(f"Changed time format to {time_format}")


    def __change_separator(self,
                           separator: str) -> None:
        '''
            Changes the separator

            :param separator: :class:`str` New separator for the log file
        '''
        self.separator = separator
        print(f"Changed separator to {separator}")


    def __clear(self) -> None:
        '''
            Clears the log file
        '''
        if self.__enable_remove:
            if os.path.exists(self.file_path):
                with open(self.file_path,
                          "w",
                          encoding = self.encoding) as _:
                    print(f"Log file cleared ({self.file_path})")
            self.__error(message = f"Log file does not exist ({self.file_path})")
        self.__error(message = "Removal is not enabled")


    def __remove(self) -> None:
        '''
            Removes the log file
        '''
        if self.__enable_remove:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                print(f"Log file removed ({self.file_path})")
            self.__error(message = f"Log file does not exist ({self.file_path})")
        self.__error(message = "Removal is not enabled")
