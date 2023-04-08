from http import HTTPStatus

from users.tests.data import DataForTests


class StaticURLTests(DataForTests):
    '''Тестируем urls приложения users'''

    def test_templates_and_pages_status(self):
        '''Проверка доступности основных страниц и соответствия шаблонов.'''
        for test in self.TEST_DATA:
            with self.subTest(test['title']):

                if test.get('need_authorization'):
                    current_client = self.another_client
                else:
                    current_client = self.client

                response = current_client.get(test['url_name'])
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, test['html_template'])
