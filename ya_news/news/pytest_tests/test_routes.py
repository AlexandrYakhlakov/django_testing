from http import HTTPStatus
from django.urls import reverse
import pytest
from .conftest import UrlConst
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client',
                         ((pytest.lazy_fixture('client'),
                           pytest.lazy_fixture('author_client')
                           )))
@pytest.mark.parametrize('url, news_data',
                         ((UrlConst.HOME_URL, None),
                          (UrlConst.DETAIL_NEWS_PAGE,
                           pytest.lazy_fixture('news')),
                          (UrlConst.LOGIN_URL, None),
                          (UrlConst.REGISTRATION_URL, None)))
def test_pages_availability_for_all_users(parametrized_client, url, news_data):
    url = reverse(url, args=(news_data.id,)
                  if news_data is not None else ())
    response = parametrized_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, status',
                         ((pytest.lazy_fixture('author_client'),
                           HTTPStatus.OK),
                          (pytest.lazy_fixture('not_author_client'),
                           HTTPStatus.NOT_FOUND)))
@pytest.mark.parametrize('url_name',
                         ((UrlConst.EDIT_COMMENT_PAGE,
                           UrlConst.DELETE_COMMENT_PAGE)))
def test_availability_for_comment_edit_and_delete(parametrized_client,
                                                  status,
                                                  url_name,
                                                  author_comment):
    author_comment, _ = author_comment
    url = reverse(url_name, args=(author_comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize('url_name',
                         ((UrlConst.EDIT_COMMENT_PAGE,
                           UrlConst.DELETE_COMMENT_PAGE)))
def test_redirect_for_anonymous_client(url_name, client, author_comment):
    author_comment, _ = author_comment
    login_url = reverse('users:login')
    url = reverse(url_name, args=(author_comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
