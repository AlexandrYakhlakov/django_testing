import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

from .conftest import UrlConst


@pytest.fixture
def comment_list_for_news(comment_list,
                          news,
                          author,
                          not_author):
    news = news
    comment_list(author, news, 5)
    comment_list(not_author, news, 5)
    return news, news.comment_set.all()


@pytest.fixture
def news_list_home(news_list):
    return news_list(settings.NEWS_COUNT_ON_HOME_PAGE + 5)


@pytest.fixture
def home_page_object_list(news_list_home, client):
    url = reverse(UrlConst.HOME_URL)
    response = client.get(url)
    object_list = response.context['object_list']
    return object_list


@pytest.mark.django_db
def test_news_count(home_page_object_list):
    news_count = len(home_page_object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(home_page_object_list):
    news_dates = [news.date for news in home_page_object_list]
    sorted_dates = sorted(news_dates, reverse=True)
    assert news_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comment_list_for_news):
    news, comment_list = comment_list_for_news
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
    assert comment_list.count() == all_comments.count()


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, is_logged',
                         ((pytest.lazy_fixture('author_client'), True),
                          (pytest.lazy_fixture('client'), False)))
def test_detail_page_contains_form(news, parametrized_client, is_logged):
    url = reverse(UrlConst.DETAIL_NEWS_PAGE, args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == is_logged
    if is_logged:
        assert isinstance(response.context['form'], CommentForm)