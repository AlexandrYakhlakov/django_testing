from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class UrlsConst:
    HOME_PAGE = 'notes:home'
    NOTES_LIST = 'notes:list'
    NOTE_CREATE_URL = 'notes:add'
    NOTE_READ = 'notes:detail'
    NOTE_UPDATE_URL = 'notes:edit'
    NOTE_DELETE = 'notes:delete'
    NOTE_DONE = 'notes:success'
    LOGIN_URL = 'users:login'
    LOGOUT_URL = 'users:logout'
    REGISTRATION_URL = 'users:signup'


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_user = User.objects.create(username='auth-user')

    @staticmethod
    def create_notes(author: User, count: int = 1) -> list:
        notes = []
        for i in range(count):
            note = Note(
                title=f'Заголовок {author.username}',
                text='Текст заметки',
                slug=f'note-slug-{author.username}-{i}',
                author=author)
            notes.append(note)
        notes = Note.objects.bulk_create(notes)
        return notes
