from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

from .base_tests_settings import BaseTestCase, UrlsConst


class TestContent(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_notes(cls.author, 5)
        cls.create_notes(cls.auth_user, 5)

    def get_data_from_response_context(self, url, key):
        response = self.client.get(url)
        return response.context.get(key)

    def test_notes_list_for_different_users(self):
        url = reverse(UrlsConst.NOTES_LIST)
        notes_author = Note.objects.filter(author=self.author)

        with self.subTest(msg='Отдельная заметка в списке заметок'):
            self.client.force_login(self.author)
            object_list = self.get_data_from_response_context(url,
                                                              'object_list')
            self.assertIn(notes_author.first(), object_list)

        with self.subTest(msg='Чужие заметки в списке заметок автора'):
            self.client.force_login(self.auth_user)
            object_list = self.get_data_from_response_context(url,
                                                              'object_list')
            self.assertNotIn(notes_author, object_list)

    def test_pages_contains_form(self):
        url_names = (
            (UrlsConst.NOTE_CREATE_URL, None),
            (UrlsConst.NOTE_UPDATE_URL, Note.objects.filter(
                author=self.author).first().slug)
        )
        self.client.force_login(self.author)
        for url, args in url_names:
            with self.subTest():
                url = reverse(url, args=(args,) if args else ())
                form = self.get_data_from_response_context(url, 'form')
                self.assertIsNotNone(form)
                self.assertIsInstance(form, NoteForm)
