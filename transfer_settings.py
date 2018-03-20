#! python2
#File: transfer_settings.py


# User settings.

# Numbered sets of parameters for easy use of the script in different contexts.## TODO - Rename these and configs to something more descriptive
config_sets = {
           1: [1],
           2: [5, 6, 2],
           3: [3],
           4: [4],
           }

# Numbered sets of parameters for easy use of the script in different contexts.
configs = {
           1: ['down', 'work', 'yes', 'yes'],
           2: ['up', 'work', 'yes', 'yes'],
           3: ['down', 'home', 'yes', 'yes'],
           4: ['up', 'home', 'yes', 'yes'],
           5: ['down', 'prep1', 'yes', 'yes'],
           6: ['down', 'prep2', 'yes', 'yes'],
           }

# Location of the transfer folder in each context.
paths = {
            'up': {
                   'prep1': 'C:\\Users\\Michael Gravina\\Desktop\\LifeSeahorse_test\\', # Treating grid folder as "upstream"
                   'prep2': 'C:\\Anaconda2\\Lib\\seahorse\\', # Treating seahorse folder as "upstream"
                   #
                   'work': 'D:\\Transfer\\',
                   'home': 'E:\\Transfer\\',
                   },
            'down': {
                     'prep1': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\',
                     'prep2': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\seahorse\\',
                     #
                     'work': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\',
                     'home': 'C:\\Users\\Grav\\Desktop\\Transfer\\',
                     },
            }

# Lists of folders to skip in each context.
skip_array = {
             'up': {
                    'prep1': [],
                    'prep2': [],
                    #
                    'home': [],
                    'work': ['']
                    },
             'down': {
                      'prep1': [],
                      'prep2': [],
                      #
                      'home': ['E:\\Transfer\\CompMem'],
                      'work': []
                      }
             }
