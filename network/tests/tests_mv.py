from django.test import Client, TestCase

from django.db.models import Max
from django.core.paginator import Paginator
from django.urls import reverse

import json
import math
import datetime

from network.models import User, Post
from network.views import MAX_POSTS_PER_PAGE
from network.forms import NewPostForm

class ModelsAndViewsTestCase(TestCase):
    NUM_TEST_POSTS = 27
    USERNAMES = ["Alice", "Bob", "Chloe", "David"]

    def setUp(self):
        # Create users
        for u in self.USERNAMES:
            user = User.objects.create_user(username=u, email=f"{u}@example.com", password=u[0])
            user.save()

        # Create posts
        for i in range(self.NUM_TEST_POSTS):
            poster = User.objects.get(id= (i % len(self.USERNAMES)) + 1)
            post = Post(poster=poster, content=f"Blah blah rofflecakes #{i}")
            post.save()


    # Test setup
    def test_setup_users_loaded(self):
        self.assertEqual(len(self.USERNAMES), User.objects.all().count())

    def test_setup_user1_exists(self):
        self.assertEqual(self.USERNAMES[0], User.objects.get(id=1).username)

    def test_setup_posts_loaded(self):
        self.assertEqual(self.NUM_TEST_POSTS, Post.objects.all().count())



    # Test models
    def test_post_likescounter(self):
        p = Post.objects.all().first()
        self.assertEqual(p.likes.count(), p.count_likes())

    def test_post_displaystr(self):
        p = Post.objects.all().first()
        expected_name = f"Post #{p.id}: {p.poster.username} @ {p.created_on - datetime.timedelta(microseconds=p.created_on.microsecond)}"
        self.assertEqual(str(p), expected_name)



    # Test views
    def test_index_page1_numposts(self):
        c = Client()
        response = c.get("/")

        if MAX_POSTS_PER_PAGE < self.NUM_TEST_POSTS:
            target_num_page1 = MAX_POSTS_PER_PAGE
            self.assertTrue(response.context["page"].has_other_pages())
        else:
            target_num_page1 = self.NUM_TEST_POSTS

        self.assertEqual(len(response.context["page"]), target_num_page1)
        

    def test_index_lastpage_numposts(self):
        c = Client()
        target_num_lastpage = self.NUM_TEST_POSTS % MAX_POSTS_PER_PAGE

        last_page = math.floor(self.NUM_TEST_POSTS / MAX_POSTS_PER_PAGE)
        if target_num_lastpage > 0:
            last_page += 1

        response = c.get(f"/?page={last_page}")
        self.assertEqual(len(response.context["page"]), target_num_lastpage)




    def test_profile_valid_id(self):
        c = Client()
        max_id = User.objects.all().aggregate(Max("id"))["id__max"]
        response = c.get(reverse("profile", kwargs={"user_id": max_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "network/profile.html")


    def test_profile_invalid_id(self):
        c = Client()
        max_id = User.objects.all().aggregate(Max("id"))["id__max"]
        response = c.get(reverse("profile", kwargs={"user_id": max_id + 1}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "network/error.html")


    def test_profile_expected_following_vars(self):
        # Create a follower relationship, then check it worked
        user = User.objects.get(id=1)
        profile_subject = User.objects.all().exclude(id=user.id).first()
        user.following.add(profile_subject)
        self.assertEqual(1, user.following.count())

        # Log in and go to the profile page of the followed-one
        self.client.force_login(user)
        response = self.client.get(reverse("profile", kwargs={"user_id": profile_subject.id}))

        # Check that the passed data is all as expected
        self.assertEqual(response.context["following_count"], 0)
        self.assertEqual(response.context["followers_count"], 1)
        self.assertTrue(response.context["is_following"])


    def test_profile_expected_name(self):
        profile_subject = User.objects.all().first()
        response = self.client.get(reverse("profile", kwargs={"user_id": profile_subject.id}))
        self.assertEqual(response.context["profile_user"], profile_subject)
        

    def test_profile_pagination(self):
        profile_subject = User.objects.all().first()
        num_setup_posts = Post.objects.filter(poster=profile_subject).count()

        # Make sure there are enough posts for pagination to occur
        if num_setup_posts < MAX_POSTS_PER_PAGE:
            last_page = 2
            posts_on_last_page = 1
            posts_needed = MAX_POSTS_PER_PAGE + 1 - num_setup_posts
            for i in range(posts_needed):
                p = Post(poster=profile_subject, content=f"Blah blah, I have a profile, #{i}")
                p.save()
        else:
            last_page = math.floor(num_setup_posts / MAX_POSTS_PER_PAGE)
            posts_on_last_page = num_setup_posts % MAX_POSTS_PER_PAGE
        
        response = self.client.get(reverse("profile", kwargs={"user_id": profile_subject.id}))
        self.assertEqual(len(response.context["page"]), MAX_POSTS_PER_PAGE)

        response = self.client.get(f"/user/{profile_subject.id}?page={last_page}")
        self.assertEqual(len(response.context["page"]), posts_on_last_page)


    def test_add_post_success(self):
        self.client.login(username=self.USERNAMES[3], password=self.USERNAMES[3][0])
        num_posts_before = Post.objects.all().count()
        response =  self.client.post(reverse("posts"), data={"content": "This is some content for a new post."})
        num_posts_after = Post.objects.all().count()
        self.assertEqual(num_posts_before + 1, num_posts_after)
        self.assertRedirects(response, reverse("index"))


    def test_add_post_failure_anon(self):
        """
        Test an anonymous user adding a post
        """
        num_posts_before = Post.objects.all().count()
        response = self.client.post(reverse("posts"), data={"content": "This is some content for a new post."})
        num_posts_after = Post.objects.all().count()
        self.assertEqual(num_posts_before, num_posts_after)
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, "network/error.html")


    def test_edit_success(self):
        """
        Test a successful edit
        """
        # Make a new post and check it has length = 1
        user = User.objects.get(username=self.USERNAMES[0])
        new_post = Post(poster=user, content="A")
        new_post.save()
        self.assertEqual(1, len(new_post.content))

        # Log in as the poster then attempt to edit the content to a two-character post
        self.client.force_login(user)
        response = self.client.put(reverse("posts"), data=json.dumps({"id": new_post.id, "editted_content": "AA"}))
        edit_post_cont = Post.objects.get(id=new_post.id)
        self.assertEqual(2, len(edit_post_cont.content))


    def test_edit_failure_anon(self):
        """
        Test a failed edit due to not being logged in
        """
        # Make a new post as User[0] and check it has length 1
        user = User.objects.get(username=self.USERNAMES[0])
        new_post = Post(poster=user, content="A")
        new_post.save()
        self.assertEqual(1, len(new_post.content))

        # Attempt to edit the post without logging in
        response = self.client.put(reverse("posts"), data=json.dumps({"id": new_post.id, "editted_content": "AA"}))
        edit_post_cont = Post.objects.get(id=new_post.id)
        self.assertEqual(1, len(edit_post_cont.content))
        self.assertTemplateUsed(response, "network/error.html")


    def test_edit_failure_notowner(self):
        """
        Test a failed edit due to not owning the post
        """
        # Make a new post as User[0] and check it has length 1
        user = User.objects.get(username=self.USERNAMES[0])
        new_post = Post(poster=user, content="A")
        new_post.save()
        self.assertEqual(1, len(new_post.content))

        # Attempt to edit the post while logged in as User[1]
        userB = User.objects.get(username=self.USERNAMES[1])
        self.client.force_login(userB)
        response = self.client.put(reverse("posts"), data=json.dumps({"id": new_post.id, "editted_content": "AA"}))
        edit_post_cont = Post.objects.get(id=new_post.id)
        self.assertEqual(1, len(edit_post_cont.content))
        self.assertEqual(response.status_code, 403)



    def test_follow_success(self):
        """
        Test a successful following and un-following
        """
        # Check that user does not already follow the target
        user = User.objects.get(username=self.USERNAMES[0])
        follow_target = User.objects.get(username=self.USERNAMES[3])
        self.assertFalse(user.following.filter(id=follow_target.id).exists())

        # Follow the target and check it worked
        self.client.force_login(user)
        response = self.client.put(reverse("follow", kwargs={"user_id": follow_target.id}), data=json.dumps({"toggled_status": True}))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(user.following.filter(id=follow_target.id).exists())
        
        # Unfollow the target and check it worked
        response = self.client.put(reverse("follow", kwargs={"user_id": follow_target.id}), data=json.dumps({"toggled_status": False}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.following.filter(id=follow_target.id).exists())


    def test_like_success(self):
        """
        Test a successful liking and un-following
        """
        # Check that user does not already like the target
        liker = User.objects.get(username=self.USERNAMES[0])
        like_target = Post.objects.exclude(poster=liker).first()
        self.assertFalse(liker.liked.filter(id=like_target.id).exists())

        # Like the target and check it worked
        self.client.force_login(liker)
        response = self.client.put(reverse("likes", kwargs={"post_id": like_target.id}), data=json.dumps({"toggled_status": True}))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(liker.liked.filter(id=like_target.id).exists())

        # Unlike the target and check it worked
        response = self.client.put(reverse("likes", kwargs={"post_id": like_target.id}), data=json.dumps({"toggled_status": False}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(liker.liked.filter(id=like_target.id).exists())


