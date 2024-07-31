from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .conftest import UrlConst


@pytest.fixture
def form_data():
    return {'text': 'fasdg'}


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, is_logged, comment_count',
                         ((pytest.lazy_fixture('author_client'), True, 1),
                          (pytest.lazy_fixture('client'), False, 0)))
def test_user_can_create_comment(parametrized_client,
                                 is_logged,
                                 comment_count,
                                 news,
                                 author,
                                 form_data):
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    parametrized_client.post(url, data=form_data)
    assert Comment.objects.count() == comment_count
    if is_logged:
        comment = Comment.objects.get()
        assert comment.text == form_data['text']
        assert comment.news == news
        assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, form_data):
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    form_data['text'] = form_data['text'] + BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('parametrized_client, status, is_author',
                         ((pytest.lazy_fixture('author_client'),
                           HTTPStatus.FOUND,
                           True),
                          (pytest.lazy_fixture('not_author_client'),
                           HTTPStatus.NOT_FOUND,
                           False)))
def test_can_delete_comment(parametrized_client,
                            status,
                            author_comment,
                            is_author):
    comment, news = author_comment
    url = reverse(UrlConst.DELETE_COMMENT_PAGE, args=(comment.id,))
    response = parametrized_client.post(url)
    if is_author:
        redirect_url = reverse(UrlConst.DETAIL_NEWS_PAGE,
                               args=(news.id,)) + '#comments'
        assert response.status_code == status
        assertRedirects(response, redirect_url)
        assert Comment.objects.count() == 0
    else:
        assert response.status_code == status
        assert Comment.objects.count() == 1


@pytest.mark.parametrize('parametrized_client, status, is_author',
                         ((pytest.lazy_fixture('author_client'),
                           HTTPStatus.FOUND,
                           True),
                          (pytest.lazy_fixture('not_author_client'),
                           HTTPStatus.NOT_FOUND,
                           False)))
def test_author_can_edit_comment(parametrized_client,
                                 status,
                                 author_comment,
                                 is_author):
    comment, news = author_comment
    form_data = {'text': 'new_text'}
    url = reverse(UrlConst.EDIT_COMMENT_PAGE, args=(comment.id,))
    response = parametrized_client.post(url, data=form_data)
    comment.refresh_from_db()
    if is_author:
        redirect_url = reverse(UrlConst.DETAIL_NEWS_PAGE,
                               args=(news.id,)) + '#comments'
        assertRedirects(response, redirect_url)
        assert response.status_code == status
        assert comment.text == form_data['text']
    else:
        assert response.status_code == status
        assert comment.text != form_data['text']
