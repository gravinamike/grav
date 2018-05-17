#! python2
#File: transfer_settings.py


# User settings.

# Numbered sets of parameters for easy use of the script in different contexts.## TODO - Rename these and configs to something more descriptive
config_sets = {
           1: [1],
           2: [5, 6, 2],
           3: [3],
           4: [4],
           5: [7],
           }

# Numbered sets of parameters for easy use of the script in different contexts.
configs = {
           1: ['down', 'work', 'yes', 'yes', 'no'],
           2: ['up', 'work', 'yes', 'yes', 'no'],
           3: ['down', 'home', 'yes', 'yes', 'no'],
           4: ['up', 'home', 'yes', 'yes', 'no'],
           5: ['down', 'prep1', 'yes', 'yes', 'no'],
           6: ['down', 'prep2', 'yes', 'yes', 'no'],
           7: ['down', 'Lifelogging', 'no', 'yes', 'yes'],
           }

# Location of the transfer folder in each context.
paths = {
            'up': {
                   'prep1': 'C:\\Users\\Michael Gravina\\Desktop\\LifeSeahorse_test\\', # Treating grid folder as "upstream"
                   'prep2': 'C:\\Anaconda2\\Lib\\', # Treating seahorse folder as "upstream"
                   #
                   'work': 'E:\\Transfer\\',
                   'home': 'D:\\Transfer\\',
		   #
                   'Lifelogging': 'E:\\VIDEO\\',
                   },
            'down': {
                     'prep1': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\',
                     'prep2': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\',
                     #
                     'work': 'C:\\Users\\Michael Gravina\\Desktop\\Transfer\\',
                     'home': 'C:\\Users\\Grav\\Desktop\\Transfer\\',
 		     #
                     'Lifelogging': 'D:\\Lifelogging_data\\',
                     },
            }

# Lists of folders to skip in each context.
skip_array = {
             'up': {
                    'prep1': [],
                    'prep2': [],
                    #
                    'home': [],
                    'work': [''],
                    #
                    'Lifelogging': [],
                    },
             'down': {
                      'prep1': [],
                      'prep2': [],
                      #
                      'home': ['E:\\Transfer\\CompMem'],
                      'work': [],
                      #
                      'Lifelogging': [],
                      }
             }

# Lists of folders to exclusively target in each context.
target_array = {
             'up': {
                    'prep1': [],
                    'prep2': ['C:\\Anaconda2\\Lib\\seahorse'],
                    #
                    'home': [],
                    'work': [],
                    #
                    'Lifelogging': [],
                    },
             'down': {
                      'prep1': [],
                      'prep2': [],
                      #
                      'home': [],
                      'work': [],
                      #
                      'Lifelogging': [],
                      }
             }
