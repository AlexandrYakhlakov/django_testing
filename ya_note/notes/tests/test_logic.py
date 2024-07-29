from django.urls import reverse

from .base_tests_settings import BaseTestCase, UrlsConst
from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify


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

    def test_auth_user_can_create_note(self):
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)

        self.assertRedirects(response, redirect_url)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(self.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.LOGIN_URL)
        expected_url = f'{redirect_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = self.create_notes(self.author)[0]
        self.form_data['slug'] = note.slug
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(
            note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data['slug'] = ''
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
