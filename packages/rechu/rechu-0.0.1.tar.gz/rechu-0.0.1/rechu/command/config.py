"""
Subcommand to generate an amalgamate settings file.
"""

import tomlkit
from tomlkit.items import Item, Table
from .base import Base
from ..settings import Settings

@Base.register("config")
class Config(Base):
    """
    Obtain settings file representation.
    """

    subparser_keywords = {
        'help': 'Obtain settings representation',
        'description': 'Generate settings TOML representation with comments.'
    }
    subparser_arguments = [
        (('section',), {
            'metavar': 'SECTION',
            'nargs': '?',
            'help': 'Optional table section name to filter on'
        }),
        (('key',), {
            'metavar': 'KEY',
            'nargs': '?',
            'help': 'Optional settings key to filter on'
        }),
        (('-f', '--file'), {
            'help': 'Generate based on specific TOML file'
        }),
        (('-p', '--prefix'), {
            'nargs': '+',
            'default': (),
            'help': 'Section prefixes in specific TOML file to look up'
        })
    ]

    def __init__(self) -> None:
        super().__init__()
        self.section: str = ''
        self.key: str = ''
        self.file: str = ''
        self.prefix: tuple[str, ...] = ()

    def run(self) -> None:
        if self.file:
            document = Settings(path=self.file, environment=False,
                                prefix=self.prefix).get_document()
        else:
            document = self.settings.get_document()

        if self.section:
            table = document.get(self.section)
            container = tomlkit.table()
            if isinstance(table, Table):
                table.trivia.indent = ''
                if self.key:
                    if self.key not in table:
                        print()
                        return

                    table = self._wrap_setting(table[self.key], self.key)

                container[self.section] = table

            print(container.as_string())
        else:
            print(document.as_string())

    def _wrap_setting(self, item: Item, key: str) -> Table:
        comments = self.settings.get_comments()
        table = tomlkit.table()
        for comment in comments.get(self.section, {}).get(key, []):
            table.add(tomlkit.comment(comment))
        table[key] = item
        return table
