# Harvard's CS50w: Project 4, "Network", by Alex Symonds

## Introduction
A Twitter-like social network site in Python (Django), JavaScript, HTML, and CSS.

## Specification and Provided Materials
Students were given:
* New Django project
* Log in, log out, register pages (views, URL and HTML templates)
* Index URL; mostly empty boiler-plate view and HTML template
* Layout template

Students were required to:
* Add a "new post" feature to either the index page or a separate "new post" page
* "All posts" page displaying all posts from all users, newest first
* Profile page, accessed by clicking a username. Displays number of followers and followed, all the user's posts and, conditionally, a follow/unfollow button
* Following page, displaying only posts from users "followed" by the current user
* Pagination (10 posts per page for all pages displaying posts)
* Edit post (shouldn't reload the page; should prevent a user from editing another user's post)
* Like / unlike buttons (without reloading the page)

[Detailed specification is here.](https://cs50.harvard.edu/web/2020/projects/4/network/)

## Beyond the Specification
* React: the like button is implemented in vanilla JavaScript, the follow button in React (for learning and comparison purposes)
* Unit testing: I setup some unit tests using Django's library and Selenium
* CSS: while previous projects also used CSS, in this project I decided to try something a bit more complicated, taking inspiration from the control panels in the 90s Star Trek series

## Pages
* Log in, register
* Index / All Posts
* Profile
* Following
* Error

## Learning Comments
* Django CSRF protection when you're not using a form and so can't use {% csrf_token %}
* Avoidance of unwanted page reloads
* Pagination
* Getting Selenium to cooperate with Django's built-in unit testing library
* Making use of the "cascading" part of CSS


