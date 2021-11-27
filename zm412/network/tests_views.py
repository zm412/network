from django.test import TestCase, Client
from network.models import Post, User, UserFollowing
from datetime import timedelta, datetime
from network.views import func_for_save, Add_post, Upd_post
from django.urls import reverse


# Create your tests here.


class ViewsTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='TestUser1', password='123taz@111', email='test@mail.ru')
        self.user2 = User.objects.create(username='TestUser2', password='223taz@222', email='test2@mail.ru')
        self.post1 = Post.objects.create(title='TitleTest1', author=self.user1, body='test1test1')
        self.post2 = Post.objects.create(title='TitleTest2', author=self.user2, body='test2test2')
        self.post3 = Post.objects.create(title='TitleTest3', author=self.user1, body='test3test3')
        self.post4 = Post.objects.create(title='TitleTest4', author=self.user2, body='test4test4')
        self.post5 = Post.objects.create(title='TitleTest5', author=self.user1, body='test5test5')
        self.chain = UserFollowing.objects.create(follower_user=self.user1, following_user=self.user2)
        self.client = Client()
        self.req = self.client.force_login(self.user2, backend=None)


    def test_create_correct_fields(self):
        self.assertEqual(self.post1.body, 'test1test1')
        self.assertEqual(self.post2.body, 'test2test2')
        self.assertEqual(self.post1.author, self.user1)
        self.assertEqual(self.user1.following.get(id=self.user2.id).id, self.user2.id)
        self.assertEqual(self.user2.followers.get(id=self.user1.id).id, self.user1.id)

    def test_model_func(self):
        self.assertEqual(self.chain.get_followers(), {'id': self.user1.id, 'username': self.user1.username})
        self.assertEqual(self.chain.get_followings(), {'id': self.user2.id, 'username': self.user2.username})
        self.assertEqual(self.chain.serialize(), {
            'follower': {
                'id': self.user1.id,
                'username': self.user1.username
            },
            'following': {
                'id': self.user2.id,
                'username': self.user2.username
            },
            'created': self.chain.created
        })
        self.assertEqual(self.post1.serialize(), {
            'id': self.post1.id,
            'status': 'draft',
            'title': self.post1.title,
            'author_name': self.post1.author.username,
            'author_id': self.post1.author.id,
            'body': self.post1.body,
            "publish": self.post1.publish.strftime("%b %d %Y, %I:%M %p"),
            "created": self.post1.created.strftime("%b %d %Y, %I:%M %p"),
            "updated": self.post1.updated.strftime("%b %d %Y, %I:%M %p"),
            'likers': []
        })

        #views testing

    def test_login_user(self):
        login_get = self.client.get('/')
        self.assertEqual(login_get.status_code, 200)

        response_login = self.client.get('/login')

        self.assertEqual(response_login.status_code, 200)
        self.login_in_system = self.client.post('/login', {
            'username': 'TestUser1',
            'password': '123taz@111',
        })
        self.assertEqual(self.login_in_system.status_code, 200)

    def test_add_post_success(self):
        obj = { 'title': 'addedPost', 'body': 'bodyNewAddedPost' }
        add_post = self.client.post('/save_post/0', obj, follow=True)
        post = Post.objects.get(title='addedPost')
        self.assertEqual(add_post.status_code, 200)
        self.assertEqual(post.body, obj['body'])

    def test_add_post_not_valid_title(self):
        obj = {'title': '', 'body': 'newAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBody'}
        add_post = self.client.post('/save_post/0', obj, follow=True)
        add = add_post.json()
        self.assertEqual(add_post.status_code, 200)
        self.assertEqual(add['message'], 'data for add is not valid')
        self.assertEqual(add['status'], False)

    def test_add_post_not_valid_body(self):
        obj = {'title': 'TitleForNewPost', 'body': ''}
        add_post = self.client.post('/save_post/0', obj, follow=True)
        add = add_post.json()
        self.assertEqual(add['message'], 'data for add is not valid')
        self.assertEqual(add['status'], False)
        self.assertEqual(add_post.status_code, 200)


    def test_upd_post_success(self):
        obj = {'body': 'UpdatedPost'}
        upd_post = self.client.post(f'/save_post/{self.post5.id}', obj, follow=True)
        upd = upd_post.json()
        updated_post = Post.objects.get(id = self.post5.id)
        self.assertEqual(upd_post.status_code, 200)
        self.assertEqual(upd['message'], 'Successfully updated')
        self.assertEqual(upd['status'], True)
        self.assertEqual(updated_post.body, obj['body'])


    def test_upd_post_not_valid_body(self):
        obj = {'body': ''}
        answ = func_for_save(obj, self.user1, Upd_post,'upd', self.post5.id)
        upd_post = self.client.post(f'/save_post/{self.post5.id}', obj, follow=True)
        upd = upd_post.json()
        self.assertEqual(upd_post.status_code, 200)
        self.assertEqual(upd['message'], 'data for update is not valid')
        self.assertEqual(upd['status'], False)


    def test_success_added(self):
        obj = {'title': 'newAdding', 'body': 'newAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBody'}
        answ = func_for_save(obj, self.user1, Add_post,'add')
        self.post6 = Post.objects.get(title='newAdding')
        self.assertEqual(answ['message'], 'Successfully added')
        self.assertEqual(answ['ok'], True)
        self.assertEqual(self.post6.body, obj['body'])

    def test_not_valid_title_add(self):
        obj = {'title': '', 'body': 'newAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBodynewAddingBody'}
        answ = func_for_save(obj, self.user1, Add_post,'add')
        self.assertEqual(answ['message'], 'data for add is not valid')
        self.assertEqual(answ['ok'], False)

    def test_not_valid_body_add(self):
        obj = {'title': 'newAdding', 'body': ''}
        answ = func_for_save(obj, self.user1, Add_post,'add')
        self.assertEqual(answ['message'], 'data for add is not valid')
        self.assertEqual(answ['ok'], False)

    def test_success_updated(self):
        obj = {'body': 'UpdatedPost'}
        answ = func_for_save(obj, self.user1, Upd_post,'upd', self.post5.id)
        updated_post = Post.objects.get(id = self.post5.id)
        self.assertEqual(answ['message'], 'Successfully updated')
        self.assertEqual(answ['ok'], True)
        self.assertEqual(updated_post.body, obj['body'])

    def test_not_valid_data_for_update(self):
        obj = {'body': ''}
        answ = func_for_save(obj, self.user1, Upd_post,'upd', self.post5.id)
        updated_post = Post.objects.get(id = self.post5.id)
        self.assertEqual(answ['message'], 'data for update is not valid')
        self.assertEqual(answ['ok'], False)

    def test_there_is_nothing_to_update(self):
        obj = {'body': self.post5.body}
        answ = func_for_save(obj, self.user1, Upd_post,'upd', self.post5.id)
        updated_post = Post.objects.get(id = self.post5.id)
        self.assertEqual(answ['message'], 'there is nothing to update')
        self.assertEqual(answ['ok'], False)

    def test_add_and_remove_like(self):
        add_like = self.client.get('/posts/'+str(self.post1.id), follow=True)
        like_add_message = add_like.json()['message']
        userUsername = self.post1.likes_list_users.get(username='TestUser2')
        quantity_of_likes_after_add = self.post1.likes_list_users.all().count()

        self.assertEqual(add_like.status_code, 200)
        self.assertEqual(userUsername.username, self.user2.username)
        self.assertEqual(like_add_message, 'Like is added')
        self.assertEqual(quantity_of_likes_after_add, 1)

        remove_like = self.client.get('/posts/'+str(self.post1.id), follow=True)
        like_remove_message = remove_like.json()['message']
        quantity_of_likes_after_remove = self.post1.likes_list_users.all().count()

        self.assertEqual(add_like.status_code, 200)
        self.assertEqual(userUsername.username, self.user2.username)
        self.assertEqual(like_remove_message, 'like is removed')
        self.assertEqual(quantity_of_likes_after_remove, 0)


    def test_user_follow(self):
        url = f'/follow/{self.user1.id}/follow'
        add_user_to_followers = self.client.get(url, follow=True)
        add_user = add_user_to_followers.json()
        following_chain = UserFollowing.objects.get(follower_user=self.user2)
        self.assertEqual(add_user_to_followers.status_code, 200)
        self.assertEqual(add_user['status'], True)
        self.assertEqual(add_user['message'], f'the current user is the  subscriber of {self.user1.username}')

    def test_user_unfollow(self):
        url = f'/follow/{self.user1.id}/unfollow'
        remove_user_to_followers = self.client.get(url, follow=True)
        remove_user = remove_user_to_followers.json()
        self.assertEqual(remove_user_to_followers.status_code, 200)
        self.assertEqual(remove_user['status'], True)
        self.assertEqual(remove_user['message'], f'the current user is not the  subscriber of {self.user1.username} anymore')

    def test_user_follow_with_not_valid_id(self):
        url = f'/follow/500/follow'
        add_user_to_followers = self.client.get(url, follow=True)
        add_user = add_user_to_followers.json()
        self.assertEqual(add_user_to_followers.status_code, 200)
        self.assertEqual(add_user['status'], False)
        self.assertEqual(add_user['message'], 'data is not valid')


    def test_user_follow_with_not_valid_action(self):
        url = f'/follow/{self.user1.id}/not_valid_data'
        add_user_to_followers = self.client.get(url, follow=True)
        add_user = add_user_to_followers.json()
        self.assertEqual(add_user_to_followers.status_code, 200)
        self.assertEqual(add_user['status'], False)
        self.assertEqual(add_user['message'], 'data is not valid')

    def test_get_user_info_if_is_not_following(self):
        user_info = self.client.get('/user_info/'+str(self.user1.id), follow=True)
        status = user_info.json()
        self.assertEqual(user_info.status_code, 200)
        self.assertEqual(status['is_following'], False)


    def test_get_user_info_if_is_following(self):
        url = f'/follow/{self.user1.id}/follow'
        add_user_to_followers = self.client.get(url, follow=True)
        following_chain = UserFollowing.objects.get(follower_user=self.user2)

        user_info = self.client.get('/user_info/'+str(self.user1.id), follow=True)
        status = user_info.json()
        self.assertEqual(user_info.status_code, 200)
        self.assertEqual(status['is_following'], True)

    def test_get_posts_of_user1(self):
        url = f'/posts/?post_owner_id={self.user1.id}&start=0&end=3'
        get_posts = self.client.get(url, follow=True)
        context = get_posts.json()

        self.assertEqual(get_posts.status_code, 200)
        self.assertEqual(context['quantity'], 3)
        self.assertEqual(context['author'], 'TestUser1')
        self.assertEqual(len( context['posts'] ), 3)


    def test_get_posts_of_all_users(self):
        url = f'/posts/?post_owner_id=0&start=0&end=3'
        get_posts = self.client.get(url, follow=True)
        context = get_posts.json()

        self.assertEqual(get_posts.status_code, 200)
        self.assertEqual(context['quantity'], 5)
        self.assertEqual(context['author'], 'TestUser2')
        self.assertEqual(len( context['posts'] ), 3)

        

   






