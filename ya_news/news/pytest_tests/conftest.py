import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


class UrlConst:
    HOME_URL = 'news:home'
    DETAIL_NEWS_PAGE = 'news:detail'
    DELETE_COMMENT_PAGE = 'news:delete'
    EDIT_COMMENT_PAGE = 'news:edit'
    LOGIN_URL = 'users:login'
    LOGOUT_URL = 'users:logout'
    REGISTRATION_URL = 'users:signup'


@pytest.fixture
def user(django_user_model):
    def _user(username):
        return django_user_model.objects.create(username=username)
    return _user


@pytest.fixture
def author(user):
    return user('Автор')


@pytest.fixture
def not_author(user):
    return user('Не Автор')


@pytest.fixture
def auth_client():
    def _auth_client(user):
        client = Client()
        client.force_login(user)
        return client
    return _auth_client


@pytest.fixture
def author_client(author, auth_client):
    return auth_client(author)


@pytest.fixture
def not_author_client(not_author, auth_client):
    return auth_client(not_author)


@pytest.fixture
def news_list():
    def _news_list(count=1):
        all_news = []
        today = timezone.now().date()
        for index in range(count):
            news = News(title=f'Новость {index}',
                        text='Просто текст',
                        date=today - timezone.timedelta(days=index))
            all_news.append(news)
        News.objects.bulk_create(all_news)
        return News.objects.all()
    return _news_list


@pytest.fixture
def news(news_list):
    return news_list()[0]


@pytest.fixture
def comment_list():
    def _comment_list(user, news, count=1):
        all_comments = []
        for _ in range(count):
            comment = Comment(news=news,
                              author=user,
                              text='Текст комментария')
            all_comments.append(comment)
        Comment.objects.bulk_create(all_comments)
        return Comment.objects.filter(author=user).all()
    return _comment_list


@pytest.fixture
def author_comment(comment_list, news, author):
    comment = comment_list(author, news)[0]
    return comment, news


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
