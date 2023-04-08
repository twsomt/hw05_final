from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutUrlsTestCase(TestCase):
    '''Проверка Url основных страниц и HTML шаблонов.'''

    def test_author_url_resolves_to_author_url(self):
        '''Страница об авторе.'''
        url = '/about/author/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_url_resolves_to_tech_url(self):
        '''Страница примененных технологий.'''
        url = '/about/tech/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'about/tech.html')


class AboutViewsTestCase(TestCase):
    '''Проверка View основных страниц и HTML шаблонов.'''

    def test_tech_view_resolves_to_author_view(self):
        '''Страница об авторе.'''
        url = 'about:author'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_view_resolves_to_tech_view(self):
        '''Страница примененных технологий.'''
        url = 'about:tech'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'about/tech.html')
