from django.contrib.auth.models import User
from django.test import TestCase
from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
# Создаём тестовую запись в БД# и сохраняем ее в качестве переменной класса
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test1',
            description='Описание тестовой группы'
        )
        cls.user = User.objects.create_user(
            'john',
            'john@mail.ru',
            'johnpassword'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст для теста',
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Содержание поста',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите что-нибудь!',
            'group': 'Выберите группу!'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str_method_post(self):
        """вывод метода __str__ модели post совпадает с ожидаемым."""
        expected_post = 'Тестовый текст '
        self.assertEqual(
            str(PostModelTest.post),
            expected_post,
            'Что-то с методом str модели post не так!')

    def test_str_method_group(self):
        """вывод метода __str__ модели group совпадает с ожидаемым."""
        expected_group = 'Тестовая группа'
        self.assertEqual(
            str(PostModelTest.group),
            expected_group,
            'Что-то с методом str модели group не так!')
