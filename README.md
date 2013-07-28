anibooru
========
A batch downloader script for danbooru.

NOTE that this script is still a work in progress. If you find a bug,
please create an issue on github and I'll fix them :) Thanks!

Features
--------
- Subdirectories created in destination directory with search tags as
  name for easy organization.
- Script will not attempt to redownload files that already exist
- Can set a limit on # of posts downloaded

How To Use
----------
This script requires Python v3. To understand the command line parameters,
simply type 'anibooru.py --help'.

Roadmap
-------
Features that I plan to work on in the future (in no certain order):
- Allow searching of pools
- More customization of filenames (such as tags in filenames, post ID, etc)
- Look into ways to improve HTTP request times?
