import unittest
from network.models import Post, User
from selenium import webdriver
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


driver = webdriver.Chrome()

class WebpageTests(StaticLiveServerTestCase):
    # Define some constants
    NUM_TEST_POSTS = 21
    USERNAMES = ["Alice", "Bob"]
    URL_FOLLOW = "/following"
    URL_HOME = ""
    URL_LOGIN = "/login"

    @classmethod
    def setUp(self):
        self.server = self.live_server_url

        # Create users
        for u in self.USERNAMES:
            user = User.objects.create_user(username=u, email=f"{u}@example.com", password=u[0].lower())
            user.save()

        # Save the first two users as reusable objects and setup a following relationship between them
        self.UserA = User.objects.get(username=self.USERNAMES[0])
        self.UserB = User.objects.get(username=self.USERNAMES[1])
        self.UserA.following.add(self.UserB)

        # Save the user profile url for each
        self.profile_userA = f"/user/{self.UserA.id}"
        self.profile_userB = f"/user/{self.UserB.id}"

        # Create posts
        for i in range(self.NUM_TEST_POSTS):
            # Alternate between the users: will need a "my post" to check edit and "someone else's post" to check like
            # Note: user IDs are incrementing between tests, for some reason, so you can't rely on it always being IDs 1, 2, 3, etc.
            if i == 0:
                poster = self.UserA
            elif poster == self.UserA:
                poster = self.UserB
            else:
                poster = self.UserA

            post = Post(poster=poster, content=f"Blah blah rofflecakes #{i}")
            post.save()
        
    @classmethod
    def tearDownClass(self):
        driver.quit()
        super().tearDownClass()
  

    def test_index_title(self):
        """Check the title is ok on the homepage"""
        self.login(self.UserA)
        driver.get('%s%s' % (self.server, ""))
        self.assertEqual(driver.title, "Starfleet Secure Comms")

    def test_index_like_counter(self):
        """Check the like counter works on the homepage"""
        self.login(self.UserA)
        self.like_counter("")

    def test_index_like_btn_class(self):
        """Check the like button's CSS class is toggling on the homepage"""
        self.login(self.UserA)
        self.like_button_class("")

    def test_index_edit(self):
        """Check the edit button works on the homepage"""
        self.login(self.UserA)
        self.edit_button("")



    def test_following_title(self):
        """Check the following page has the correct title"""
        self.login(self.UserA)
        driver.get('%s%s' % (self.server, self.URL_FOLLOW))
        self.assertEqual(driver.title, "Starfleet Secure Comms - Following")

    def test_following_like_counter(self):
        """Check the like counter works on the following page"""
        self.login(self.UserA)
        self.like_counter(self.URL_FOLLOW)

    def test_following_like_btn_class(self):
        """Check the like button's CSS class is toggling on the following page"""
        self.login(self.UserA)
        self.like_button_class(self.URL_FOLLOW)


    def test_profile_title(self):
        """Check a profile page has the correct title """
        self.login(self.UserA)
        driver.get('%s%s' % (self.server, self.profile_userA))
        self.assertEqual(driver.title, f"Starfleet Secure Comms - Profile for {self.UserA.username}")

    def test_profile_like_counter(self):
        """Check the like counter works on profile pages (must not be logged-in user) """
        self.login(self.UserA)
        self.like_counter(self.profile_userB)

    def test_profile_like_btn_class(self):
        """Check the like button's CSS class is toggling on profile pages (must not be logged-in user)"""
        self.login(self.UserA)
        self.like_button_class(self.profile_userB)

    def test_profile_edit(self):
        """Check the edit button works on a profile (must be the logged-in user)"""
        self.login(self.UserA)
        self.edit_button(self.profile_userA)

    def test_profile_follow_toggle(self):
        """
        Check the follower toggle is incrementing/decrementing successfully
        (must not be logged-in user)
        """
        self.login(self.UserA)
        driver.get('%s%s' % (self.server, self.profile_userB))
        time.sleep(2)

        # Find the element
        count_ele = driver.find_element_by_id("num-followers")
        btn_ele = driver.find_element_by_id("follower_toggle_react")

        count_at_start = int(count_ele.text)
        btn_at_start = btn_ele.text

        if btn_at_start == 'following'.upper():
            count_post_click = count_at_start - 1
            btn_post_click = 'not following'.upper()
        else:
            count_post_click = count_at_start + 1
            btn_post_click = 'following'.upper()

        btn_ele.click()
        time.sleep(1)
        self.assertEqual(int(count_ele.text), count_post_click)
        self.assertEqual(btn_ele.text, btn_post_click)

        btn_ele.click()
        time.sleep(1)
        self.assertEqual(int(count_ele.text), count_at_start)
        self.assertEqual(btn_ele.text, btn_at_start)



    def login(self, logger):
        driver.get('%s%s' % (self.server, self.URL_LOGIN))
        driver.find_element_by_name("username").send_keys(logger.username)
        driver.find_element_by_name("password").send_keys(logger.username[0].lower())
        driver.find_element_by_id("login-btn").submit()

    def like_counter(self, url):
        """ Test that the like counter increments and decrements correctly"""
        # Find a like button
        driver.get('%s%s' % (self.server, url))
        time.sleep(2)
        like_btn = driver.find_element_by_class_name("like-btn")

        # Grab its status and the post ID. Use the post_id to grab the corresponding counter and save the init value
        status_before = like_btn.get_attribute("data-status")
        post_id = like_btn.get_attribute("data-id")
        like_counter = driver.find_element_by_id(f"num_likes_{post_id}")
        init_count = int(like_counter.text)

        # Set toggling expectations
        if status_before == "true":
            toggled_count = init_count - 1
    
        elif status_before == "false":
            toggled_count = init_count + 1

        else:
            # It should be true or false, so if it somehow isn't check the type then run an assert that'll tell me what it /is/.
            self.assertTrue(type(status_before), type("str"))
            self.assertTrue(status_before in ["true", "false"])

        # Click the button and give the page a moment to actually make the changes
        like_btn.click()
        time.sleep(1)

        # Check the counter changed as expected
        like_counter = driver.find_element_by_id(f"num_likes_{post_id}")
        self.assertEqual(int(like_counter.text), toggled_count)

        # Click the button and wait again
        like_btn.click()
        time.sleep(1)

        # Check it de-toggled
        like_counter = driver.find_element_by_id(f"num_likes_{post_id}")
        self.assertEqual(int(like_counter.text), init_count)        


    def like_button_class(self, url):
        """Check the like toggle is setting CSS class correctly"""
        CLASS_NAMES = ["liked", "unliked"]
        driver.get('%s%s' % (self.server, url))
        time.sleep(2)

        # Find a like button. Like buttons should have "class='like-btn lcars-btn liked'" or "class='like-btn lcars-btn unliked'"
        like_btn = driver.find_element_by_class_name("like-btn")
        status_before = like_btn.get_attribute("data-status")
        classes_before = like_btn.get_attribute("class").split(" ")

        # Define toggle status at the start
        if status_before == "true":
            start_id = 0
            toggle_id = 1

        elif status_before == "false":
            start_id = 1
            toggle_id = 0
        
        else:
            # It should be true or false, so if it somehow isn't check the type then run an assert that's sort of a print statement.
            self.assertTrue(type(status_before) == str)
            self.assertEqual("should be true or false", status_before)

        # Check the start class is correct
        self.assertTrue(CLASS_NAMES[start_id] in classes_before)
        
        # Click the button and give it a moment to Do The Thing
        like_btn.click()
        time.sleep(1)

        # Check it's toggled
        classes_after = like_btn.get_attribute("class").split(" ")
        self.assertTrue(CLASS_NAMES[toggle_id] in classes_after)

        # Put it back
        like_btn.click()
        time.sleep(1)

        # Check that worked ok
        classes_end = like_btn.get_attribute("class").split(" ")
        self.assertTrue(CLASS_NAMES[start_id] in classes_end)


    def edit_button(self, url):
        driver.get('%s%s' % (self.server, url))
        time.sleep(2)

        # Find an edit button, its associated content div and the original message and size.
        edit_btn = driver.find_element_by_class_name("edit-btn")
        post_id = edit_btn.get_attribute("data-id")
        cont_div = driver.find_element_by_id(f"post_content_{post_id}")
        text_start = cont_div.text

        # Click the edit button and give the page a chance to respond
        edit_btn.click()
        time.sleep(1)

        # Textarea and save button should have appeared in the same div as the edit button. Grab them.
        txta = driver.find_element_by_xpath(f"//div[@id='post_content_{post_id}']//textarea[1]")
        save_btn = driver.find_element_by_xpath(f"//div[@id='post_content_{post_id}']//input[1]")

        # Check the textarea contains the message
        self.assertEqual(text_start, txta.text)

        # Edit the text
        text_addition = " [edit]"
        txta.clear()
        txta.send_keys(text_start + text_addition)
        save_btn.click()
        time.sleep(1)

        # Check that the new text appears in the div
        self.assertEqual(cont_div.text, text_start + text_addition)

        # Reset it
        edit_btn.click()
        time.sleep(1)

        txta = driver.find_element_by_xpath(f"//div[@id='post_content_{post_id}']//textarea[1]")
        save_btn = driver.find_element_by_xpath(f"//div[@id='post_content_{post_id}']//input[1]")
        txta.clear()
        txta.send_keys(text_start)
        save_btn.click()
        time.sleep(1)

        # Check the message is back
        self.assertEqual(cont_div.text, text_start)


if __name__ == "__main__":
    unittest.main()