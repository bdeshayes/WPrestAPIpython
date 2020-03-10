WP REST API Python
==================

**accessing WordPress custom post type with meta fields via a python web app**

WordPress side
--------------
Install WordPress and add the REST-API.php file in the wp-contents/plugins directory.

If you are using WordPress 5 you will need the Classic Editor plugin to disable the new Gutemberg WYSIWYG fancy editor which does not show the new meta fields we just created.

You will also need to copy the JSON Basic Authentication plugin from https://github.com/WP-API/Basic-Auth into in the wp-contents/plugins directory.

Finally you will also copy archive-press_releases.php and single-press_releases.php into your active wp-contents/themes/twentynineteen directory (or whichever active theme you have)

When you go into your dashboard via /wp-admin login you will see **two new menus.**

One called **Press Releases** (above Appearance) 

One called **PR Generator** (below Settings)

Go into the later one and click the button **GENERATE SAMPLE DATA**

After a little while (if you are online) this message will appear:

"All done - go to the menu Press Releases to see the result"

Our REST-API plugin just went over to https://www.prurgent.com/news/rss.php and copied a swad of press releases into our custom post type (aptly called press releases) which you can now see in the menu above Appearance.

If click Edit on one of those new posts and you scroll down to the bottom of the edit page you should see the 3 new meta fields (desk, link and topic).

I am running WAMP on Windows and my virtual host is aptly named REST-API, so by typing this url http://localhost/REST-API/press_releases/ I activate my archive-press_releases.php template which shows all those custom posts with the meta fields at the top.

if you type this url http://localhost/REST-API/wp-json/wp/v2/press_releases you will see a load of json encoded data which we will transact now from the python end.

Note: The press release posts are a different kettle of fish from the standard WordPress posts because they carry 3 extra meta fields (topic, desk and link). They won't show up on your normal homepage but on a page of their own aptly called /press_releases

Python side
-----------
I have also installed python 3.7 on my windows laptop and I can run 

C:\WPrestAPIpython>python WPrestAPI.py

INFO:root:Starting httpd on port 3000...

So by pointing my browser to http://localhost:3000/ I can see WordPress REST API Python App as well as the WordPress site running on WAMP in two separate tabs.

Let the fun begin. By clicking the **Load from WP** menu I repopulate my python side database with all the press releases grabbed from Wordpress.

If you edit one of those not only the local python database **(SQLite or MySQL)** will be updated but also the corresponding custom post on WordPress will be synchronized!

This applies also if you delete one.

If you create a new press release on the Python app we first create it in WordPress with the REST API which returns the wpid (WordPress postID) so we can create a new record on the python side with our own id - ensuring the two sides remain in sync...

I hope you like it. Enjoy!