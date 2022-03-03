# Harvard's CS50w: Project 4, "Network", by Alex Symonds

## Introduction
The assignment was to create a Twitter-like social network site, where users could post messages, follow other users, and like posts. This was to be done using Python (Django), JavaScript, HTML, and CSS. [Detailed specification is here.](https://cs50.harvard.edu/web/2020/projects/4/network/)

In addition to meeting the specification of the project, I took the opportunity to experiment with two new topics that had arisen in recent lectures: React and unit testing.
* React: the like button is impleneted in vanilla JavaScript, the follow button in React (for learning and comparison purposes)
* Unit testing: I setup some unit tests using Django's library and Selenium

Since the specification lacked criteria relating to design, I decided to take inspiration from the control panels in the 90s Star Trek series.

## Pages
* All posts / home page
* Following (showing only posts by users you've followed)
* User profiles (showing posts by that user and followed by / following stats)
* Log in / log out / register

## Features
* Create, read and update posts
* Follow and unfollow other users
* Like and unlike individual posts
* Pagination
* Prevents users from editing other users' posts at the backend
* Limited access for anonymous users




