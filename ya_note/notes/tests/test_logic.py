from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base_tests_settings import BaseTestCase, UrlsConst


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
        note_count_before = self.get_note_count()
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        note = Note.objects.last()
        note_count_after = self.get_note_count()

        self.assertNotEqual(note_count_before, note_count_after)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(self.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        note_count_before = self.get_note_count()
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.LOGIN_URL)
        expected_url = f'{redirect_url}?next={self.url}'
        note_count_after = self.get_note_count()

        self.assertEqual(note_count_after, note_count_before)
        self.assertRedirects(response, expected_url)

    def test_not_unique_slug(self):
        note = self.create_notes(self.author)[0]
        note_count_before = self.get_note_count()
        self.form_data['slug'] = note.slug
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        note_count_after = self.get_note_count()

        self.assertEqual(note_count_before, note_count_after)
        self.assertFormError(response, 'form', 'slug', errors=(
            note.slug + WARNING))

    def test_empty_slug(self):
        note_count_before = self.get_note_count()
        self.form_data['slug'] = ''
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.assertRedirects(response, redirect_url)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        note_count_after = self.get_note_count()
        self.assertNotEqual(note_count_before, note_count_after)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        note = self.create_notes(self.author)[0]
        note_count_before = self.get_note_count()
        url = reverse(UrlsConst.NOTE_DELETE, args=(note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        note_count_after = self.get_note_count()
        redirect_url = reverse(UrlsConst.NOTE_DONE)
        self.assertNotEqual(note_count_before, note_count_after)
        self.assertRedirects(response, redirect_url)

    def test_other_user_cant_delete_note(self):
        note = self.create_notes(self.author)[0]
        note_count_before = self.get_note_count()
        url = reverse(UrlsConst.NOTE_DELETE, args=(note.slug,))
        self.client.force_login(self.auth_user)
        response = self.client.post(url)
        note_count_after = self.get_note_count()
        self.assertEqual(note_count_before, note_count_after)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_edit_note(self):
        note = self.create_notes(self.author)[0]
        url = reverse(UrlsConst.NOTE_UPDATE_URL, args=(note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse(UrlsConst.NOTE_DONE))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        note = self.create_notes(self.author)[0]
        url = reverse(UrlsConst.NOTE_UPDATE_URL, args=(note.slug,))
        self.client.force_login(self.auth_user)
        response = self.client.post(url, self.form_data)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)
