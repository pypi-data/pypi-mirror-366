import pytest
import os

from berea.cli import CLIConfig
from berea.bible import BibleClient
from berea.utils import get_app_data_path


def translation_exists(translation):
    return os.path.isfile(f"{get_app_data_path('translations')}/{translation}.db")


# TODO: Use a fixture or module if more helpers are needed
pytest.translation_exists = translation_exists


@pytest.fixture(scope='session', autouse=True)
def download_translations():
    for translation in ['BSB', 'KJV']:
        if not translation_exists(translation):
            bible = BibleClient(translation)
            bible.create_bible_db()
    
    default_translation = CLIConfig.get_default_translation()
    
    if default_translation != 'BSB':
        CLIConfig.set_default_translation('BSB')
