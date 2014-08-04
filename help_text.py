# This file contains all help text for this command line application.

# Help text for the program itself.
program_help='A script to automate downloading images on Danbooru'

# All help text for command line arguments must be placed here.
#
# For all optional arguments, the long version of the argument
# name (minus the starting '--') is used to index into this
# dictionary.
#
# For positional arguments, the full name itself is used.
help_text = {
   'tag' :                    'One or more tags to search with',
   'username' :               'Your username on danbooru',
   'api-key' :                'Your API Key on danbooru (Can be found in your account profile)',
   'download-directory' :     'The directory in which downloaded photos will be placed. '
                              'Defaults to the current directory if unspecified.',
   'max-posts' :              'The script will not download more than this number of posts. '
                              'There is no practical limit on the number of posts that will '
                              'be downloaded if this option is unspecified.'
}