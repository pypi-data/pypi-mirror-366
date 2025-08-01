# Villog is a simple python utility tool for your everyday projects.

Can be installed with [pip](https://pypi.org/project/villog/).

## Modules
- Logger
- Excel generator
- Excel reader
- MSSQL handler
- PDF generator
- Mail sender

### Logger
```
from villog.log import Logger

l: Logger = Logger(file_path = "example.log")

l.log(content = "example_content")
```

### Write Excel
```
from villog.writexcel import WorkSheet, WorkBook

sheet_1: WorkSheet = WorkSheet(name = "Sheet1",
                               header = ["header_1", "header_2", "header_3"],
                               data = [["data_1", "data_2", "data_3"],
                                       ["data_4", "data_5", "data_6"]])

sheet_2: WorkSheet = WorkSheet(name = "Sheet2",
                               header = ["header_1", "header_2", "header_3"],
                               data = [["data_1", "data_2", "data_3"],
                                       ["data_4", "data_5", "data_6"]])

book: WorkBook = WorkBook(name = "Book1",
                          sheets = [sheet_1, sheet_2])

book.xlsx_create(file_path = "example.xlsx")
```

### Read Excel
> [!IMPORTANT]
> ReadExcel is under refactor.

```
from villog.readexcel import ReadExcel

excel: ReadExcel = ReadExcel(path = "example.xlsx")

excel.read()

for sheet_name in read_excel.get_sheet_names():
    for row in excel.get_sheet_content_to_list(sheet_name):
        for elem in row:
            print(elem, end = "\t")

```

### VillSQL
```
from villog.mssql import SQLConfig, VillSQL, Table

sql_config: SQLConfig = SQLConfig(server = "server_name",
                                  database = "database_name",
                                  username = "user_name",
                                  password = "password")

sql_client: VillSQL = VillSQL(sql_config = sql_config)

egt: Table = sql_client.get_table("EXAMPLE_TABLE",
                                  raw_filter="col_1 = "example",
                                  order_by = ["col_1","ASC",
                                              "col_3","DESC"],
                                  # kwargs:
                                  COL_4 = 1)

egt.set_filter(column_names = ["col_1, "col_2"])

print("COLUMNS:")
for column in egt.columns():
    print(column, end = "\t")
print("\nROWS:)
for row in egt.rows:
    for elem in row:
        print(elem, end = "\t")
"""
Output:
    COLUMNS:
    col_1   col_2
    ROWS:
    val_1_1 val_1_2
    val_2_1 val_2_2
    val_3_1 val_3_2
"""

villsql_client.close()

```

### PDF generator
> [!IMPORTANT]
> To use PDF generator on Windows, you need some [configuration](https://stackoverflow.com/a/78749746).
```
from villog.pdf import generate as generate_pdf

generate_pdf(html_string = "html_string",
             output_path = "example.pdf",
             css_string = "css_string")
```

### Mail man
```
from villog.mail_man import MailMan

mail: MailMan = MailMan(
    smtp_server="smtp.example.com",
    smtp_login="example@example.com",
    smtp_port=465,
    smtp_password="example_password",
    name="Example Name"
)

mail.send(
    subject = "Example subject",
    body = "Example body",
    send_to = ["example_1@example.com", "example_2@example.com"],
    files = ["example.xlsx"],
    images = None
)
```