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
    NOTEST_COUNT = 5

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

    @staticmethod
    def get_note_count():
        return Note.objects.count()

    # @staticmethod
    # def assert_model_count_change(expected_change=True):
    #     def wrapper(func):
    #         def inner_wrapper(self, *args, **kwargs):
    #             num_objects_before = Note.objects.count()
    #             result = func(self, *args, **kwargs)
    #             num_objects_after = Note.objects.count()
    #             if expected_change:
    #                 assert num_objects_after != num_objects_before, (
    #                     'Количество записей в базе данных не изменилось '
    #                     f'после выполнения теста {func.__name__}')
    #             else:
    #                 assert num_objects_after == num_objects_before, (
    #                     'Количество записей в базе данных изменилось '
    #                     f'после выполнения теста {func.__name__}')
    #             return result
    #         return inner_wrapper
    #     return wrapper
