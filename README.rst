========
anibooru
========

A batch downloader script for danbooru_.

.. _danbooru: http://danbooru.donmai.us/

.. contents::

Usage
=====

At the very least, the ``anibooru.py`` script requires 3 bits of information:

- Your username on danbooru
- The API key on your account
- At least 1 tag name (used to search for posts)

An example command that will download all posts under the ``one_piece`` tag::

    $ anibooru.py --username myusername --api-key 12345 one_piece

There are many other options that can be used to customize batch downloading
operations. Simply type ``anibooru.py --help`` for full documentation.

.. NOTE::
   I do not test my script without providing the ``--username`` and ``--api-key``
   options. The script might work, but you will most likely hit limitations.
   You're at least guaranteed to **not** receive full size resolution images without
   proper authentication.

Features
========

Brief list of features provided:

- Subdirectories created in destination directory with search tags as name for
  easy organization.
- Script will not attempt to redownload files that already exist
- Can set a limit on # of posts downloaded

It's important to note that this script has been hardcoded to only work with
danbooru's website. Even if the API is the same on other domains, I haven't
had a need to support them. If you want support for other sites, feel free to
put in a feature request or (better yet) a pull request!