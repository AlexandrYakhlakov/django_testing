from django.urls import reverse

from .base_tests_settings import BaseTestCase, UrlsConst
from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify

# TODO: написать тесты на редактирование
class TestNoteCreation(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.url = reverse(UrlsConst.NOTE_CREATE_URL)

    @BaseTestCase.assert_model_count_change
    def test_auth_user_can_create_note(self):
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(self.author, self.author)

    @BaseTestCase.assert_model_count_change(expected_change=False)
    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.LOGIN_URL)
        expected_url = f'{redirect_url}?next={self.url}'
        self.assertRedirects(response, expected_url)

    def test_not_unique_slug(self):
        note = self.create_notes(self.author)[0]
        num_objects_before = Note.objects.count()
        self.form_data['slug'] = note.slug
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        num_objects_after = Note.objects.count()
        self.assertEqual(num_objects_before, num_objects_after)
        self.assertFormError(response, 'form', 'slug', errors=(
            note.slug + WARNING))

    @BaseTestCase.assert_model_count_change()
    def test_empty_slug(self):
        self.form_data['slug'] = ''
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.assertRedirects(response, redirect_url)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
