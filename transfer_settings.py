#! python2
#File: transfer_settings.py


# User settings.

# Numbered sets of parameters for easy use of the script in different contexts.
configs = {
           1: ['down', 'work', 'yes', 'yes'],
           2: ['up', 'work', 'yes', 'yes'],
           3: ['down', 'home', 'yes', 'yes'],
           4: ['up', 'home', 'yes', 'yes']
           }

# Location of the transfer folder in each context.
path_base = {
            'up': {
                   'home': 'E:\\',
                   'work': 'D:\\'
                   },
            'down': {
                     'home': 'C:\\Users\\Grav\\Desktop\\',
                     'work': 'C:\\Users\\Michael Gravina\\Desktop\\'
                     }
            }

# Name of the transfer folders in each context.
path_end = {
            'up': ['Transfer\\'],
            'down': ['Transfer\\']
            }

# Lists of folders to skip in each context.
skip_array = {
             'up': {
                    'home': [],
                    'work': ['']
                    },
             'down': {
                      'home': ['E:\\Transfer\\CompMem'],
                      'work': []
                      }
             }
