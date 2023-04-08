from http import HTTPStatus

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from users.tests.data import DataForTests


class StaticViewsTests(DataForTests):
    '''Тестируем views приложения users'''

    def test_templates_and_pages_status(self):
        '''Проверка доступности основных страниц и соответствия шаблонов.'''

        for test in self.TEST_DATA:
            with self.subTest(test['title']):

                if test.get('need_authorization'):
                    current_client = self.another_client
                else:
                    current_client = self.client

                if test.get('args'):
                    url = reverse(test['reverse_name'], kwargs=test['args'])
                else:
                    url = reverse(test['reverse_name'])

                response = current_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, test['html_template'])

    def test_signup_page_context_contains_user_creation_form(self):
        '''На страницу регистрации передается форма UserCreationForm.'''
        url = reverse('users:signup')
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], UserCreationForm)
