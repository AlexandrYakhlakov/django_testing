from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import UrlConst


FORM_DATA = {'text': 'fasdg'}


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, is_logged',
                         ((pytest.lazy_fixture('author_client'), True),
                          (pytest.lazy_fixture('client'), False)))
def test_user_can_create_comment(parametrized_client,
                                 is_logged,
                                 news,
                                 author):
    comment_count_before = Comment.objects.count()
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    parametrized_client.post(url, data=FORM_DATA)
    comment_count_after = Comment.objects.count()
    if is_logged:
        comment = Comment.objects.get()
        assert comment.text == FORM_DATA['text']
        assert comment.news == news
        assert comment.author == author
        assert comment_count_after != comment_count_before
    else:
        assert comment_count_after == comment_count_before


def test_user_cant_use_bad_words(author_client, news):
    comment_count_before = Comment.objects.count()
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    FORM_DATA['text'] = FORM_DATA['text'] + BAD_WORDS[0]
    response = author_client.post(url, data=FORM_DATA)
    comment_count_after = Comment.objects.count()
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    assert comment_count_before == comment_count_after


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
    comment_count_before = Comment.objects.count()
    url = reverse(UrlConst.DELETE_COMMENT_PAGE, args=(comment.id,))
    response = parametrized_client.post(url)
    comment_count_after = Comment.objects.count()
    if is_author:
        redirect_url = reverse(UrlConst.DETAIL_NEWS_PAGE,
                               args=(news.id,)) + '#comments'
        assert response.status_code == status
        assertRedirects(response, redirect_url)
        assert comment_count_before != comment_count_after
    else:
        assert response.status_code == status
        assert comment_count_before == comment_count_after


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
