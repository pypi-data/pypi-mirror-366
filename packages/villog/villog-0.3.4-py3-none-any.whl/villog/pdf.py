'''
    This module is responsible for generating PDF files from HTML and CSS files.
'''

try:
    from weasyprint import HTML, CSS

    def generate(html_string: str,
                 output_path: str,
                 css_string: str | None = None) -> None:
        '''
            Generate a PDF file from a HTML and CSS file.

            .. code-block:: python
                generate(html_string = "<html><body>test</body></html>",
                         output_path = "example.pdf,
                         css_string = "body { color: red; }")

            :param html_string: :class:`str` HTML string
            :param output_path: :class:`str` Output path for the .pdf file
            :param css_string: :class:`Optional(Union(str, None))` CSS string. Defaults to `None`
        '''
        HTML(string = html_string).write_pdf(output_path,
                                            stylesheets = [CSS(string = css_string or "")]) # pylint: disable = line-too-long
except Exception as e: # pylint: disable=broad-exception-caught
    print(e)
