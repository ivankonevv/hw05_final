from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post, Group, User, Follow


class UrlsAndViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.second_user = User.objects.create_user(username='ivan')
        self.client = Client()
        self.second_client = Client()
        self.client.force_login(self.user)
        self.second_client.force_login(self.second_user)
        self.anonym = Client()
        self.new_group = Group.objects.create(title='TestGroup',
                                              slug='TestGroup',
                                              description='Тест',
                                              )

    def test_homepage(self):
        response = self.anonym.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_new_page(self):
        response = self.anonym.get(reverse('new_post'), follow=False)
        self.assertRedirects(response,
                             reverse('login') + '?next=' +
                             reverse('new_post'),
                             status_code=302, target_status_code=200)

    def test_new_post(self):
        cache.clear()
        new_group = self.new_group
        count = Post.objects.count()
        response = self.client.post(reverse('new_post'),
                                    {'text': 'Новый пост',
                                     'group': self.new_group.pk},
                                    follow=True
                                    )
        post = response.context['page'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertEqual(post.author, self.user,
                         'Пользователь не является автором этого поста.')
        self.assertEqual(post.group, new_group,
                         'Выбранная группа не существует.')
        self.assertEqual(post.text, 'Новый пост',
                         'Текст не соответсвтует созданному в запросе.')

    def test_new_profile_page_view(self):
        response = self.anonym.get(reverse('profile',
                                   kwargs={'username': self.user}))
        self.assertEqual(
            response.status_code,
            200,
            'Профайл пользователя не создается после регистрации'
        )

    def test_show_post(self):
        cache.clear()
        new_post_orm = Post.objects.create(
            text='Это текст публикации',
            author=self.user,
            group=self.new_group,
        )
        urls = (
            reverse('index'),
            reverse('profile',
                    kwargs={
                        'username': self.user
                    }),
            reverse('post',
                    kwargs={
                        'username': self.user,
                        'post_id': new_post_orm.id
                    }),
            reverse('group',
                    kwargs={
                        'slug': new_post_orm.group.slug,
                    }),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                paginator = response.context.get('paginator')
                if paginator is not None:
                    self.assertEqual(paginator.count, 1)
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertEqual(response.status_code, 200)
                self.assertEqual(post.author, new_post_orm.author)
                self.assertEqual(post.text, new_post_orm.text)
                self.assertEqual(post.group, new_post_orm.group)
    
    def test_404(self):
        response = self.client.get(reverse('404'))
        self.assertEqual(response.status_code, 404)

    def test_post_form_img_file(self):
        cache.clear()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        img = SimpleUploadedFile(
            "small.gif",
            small_gif,
            content_type="image/gif"
        )
        post = Post.objects.create(
            text='Это текст публикации',
            author=self.user,
            group=self.new_group,
            image=img,
        )
        post.save()
        urls = (
            reverse('index'),
            reverse('profile',
                    kwargs={
                        'username': self.user
                        }),
            reverse('post',
                    kwargs={
                        'username': self.user,
                        'post_id': self.new_group.id,
                    }),
            reverse('group',
                    kwargs={
                        'slug': post.group.slug
                    }),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                response_unauthorized = self.anonym.get(url)
                paginator = response.context.get('paginator')
                if paginator is not None:
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertContains(response, '<img', status_code=200)

    def test_post_form_txt_file(self):
        cache.clear()
        """
        Testing create post form with txt file
        """
        post_text = 'Текст'
        response = self.client.post(
            reverse('new_post'),
            {'text': post_text,
             'group': self.new_group.pk,
             'image': SimpleUploadedFile(name='test_txt.txt',
                                         content=b'These are the file contents',
                                         content_type='text/plain'),
             },)
        self.assertFalse(Post.objects.filter(text__exact=post_text).exists(),
                         'Post was created with txt file instead image')
        self.assertFormError(
            response, 'form', 'image',
            ['Загрузите правильное изображение. Файл, который вы загрузили, '
             'поврежден или не является изображением.'],
            msg_prefix='New-post form is valid with .txt file')
        self.assertEqual(
            response.context['form'].cleaned_data['text'], post_text,
            'Retry option is impossible. The PostForm is broken')

    def test_cash(self):
        first = self.anonym.get(reverse('index'))
        Post.objects.create(text='Cache check', author=self.user)
        second = self.anonym.get(reverse('index'))
        cache.clear()
        third = self.anonym.get(reverse('index'))
        self.assertEqual(first.content, second.content)
        self.assertNotEqual(second.content, third.content)

    def test_auth_comment(self):
        post1 = Post.objects.create(
            text='Пост1',
            author=self.user,
            group=self.new_group,)
        comment_text = 'Какой-то текст'
        response = self.client.post(
            reverse('add_comment', args=[post1.author.username,
                                         post1.pk]),
            {'text': comment_text},
            follow=True)
        self.assertIn(
            comment_text,
            [comment.text for comment in response.context['comments']]
        )

    def test_view_post_with_follow(self):
        self.client.get(reverse(
            'profile_follow', kwargs={'username': self.second_user.username}))
        self.assertTrue(
            Follow.objects.filter(author=self.second_user,
                                  user=self.user).exists())

    def test_followed_authors_post_appears_in_follow_list(self):
        test_post = Post.objects.create(
            text='Новый Текст', author=self.second_user)
        Follow.objects.create(author=self.second_user,
                              user=self.user)
        with self.subTest(
                msg='Check followed author post at follow_index page'):
            response = self.client.get(reverse('follow_index'))
            self.assertIn(
                test_post, response.context['page'])
        with self.subTest(
                msg='Check unfollowed author post at follow_index page'):
            Follow.objects.filter(
                author=self.second_user,
                user=self.user).delete()
            response = self.client.get(reverse('follow_index'))
            self.assertNotIn(
                test_post, response.context['page'])

    def unfollow_test(self):
        self.client.get(
            reverse('profile_unfollow', args=[self.second_user.username]))
        self.assertFalse(
            Follow.objects.filter(author=self.second_user,
                                  user=self.user).exists())
