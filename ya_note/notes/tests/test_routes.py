from http import HTTPStatus

from django.urls import reverse

from .base_tests_settings import BaseTestCase, UrlsConst


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = cls.create_notes(cls.author)[0]

    def test_pages_availability_for_all_users(self):
        url_names = (
            UrlsConst.HOME_PAGE,
            UrlsConst.LOGIN_URL,
            UrlsConst.LOGOUT_URL,
            UrlsConst.REGISTRATION_URL)
        users = (None, self.auth_user)

        for user in users:
            if user:
                self.client.force_login(user)
            for url in url_names:
                with self.subTest():
                    url = reverse(url)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
            self.client.logout()

    def test_pages_availability_for_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.auth_user, HTTPStatus.NOT_FOUND),
        )
        url_names = (
            UrlsConst.NOTE_READ,
            UrlsConst.NOTE_UPDATE_URL,
            UrlsConst.NOTE_DELETE)
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in url_names:
                with self.subTest():
                    url = reverse(url, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anon_user(self):
        login_url = reverse(UrlsConst.LOGIN_URL)
        url_names = (
            (UrlsConst.NOTES_LIST, None),
            (UrlsConst.NOTE_DONE, None),
            (UrlsConst.NOTE_CREATE_URL, None),
            (UrlsConst.NOTE_READ, self.note.slug),
            (UrlsConst.NOTE_UPDATE_URL, self.note.slug),
            (UrlsConst.NOTE_DELETE, self.note.slug)
        )
        for url, args in url_names:
            with self.subTest():
                url = reverse(url, args=(args,) if args else ())
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
