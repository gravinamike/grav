#! python2
#File: transfer.py

import os
import sys
import shutil
import errno
import stat

from send2trash import send2trash

import transfer_settings


def transfer_stick(direction=None, location=None, duplicate='yes',
                   overwrite='no', configuration=None):
    # Downloads or uploads from one set of directories to another.

    direction_names = ['up', 'down']
    opposite_direction_names = {'up': 'down', 'down': 'up'}

    # Try different approaches to getting all 4 parameters.
    while not (
                direction in direction_names
                and location in ['prep1', 'prep2', 'work', 'home']
                and duplicate in ['yes', 'no']
                and overwrite in ['yes', 'no']
                ):

        # If configuration was not specified,
        if configuration == None:
            # Try to get configuration from user to specify parameters.
            configuration = input('Configuration? (1 - 6): ')
            try:
                configuration = int(configuration)
            except ValueError:
                configuration = None

        if configuration in transfer_settings.configs.keys():
            direction, location, duplicate, overwrite = transfer_settings.configs[configuration]

        # If no valid configuration, ask user for parameters one at a time.
        else:
            print 'direction =', direction, ', location =', location, ', duplicate =', duplicate, 'overwrite =', overwrite
            print 'Parameters not all entered correctly when script called and no valid configuration selected.'
            direction = input('Enter direction (up or down): ')
            location = input('Enter location (home or work): ')
            duplicate = input('Enter whether to duplicate (yes or no): ')
            overwrite = input('Enter overwrite permission (yes or no): ')

    # Construct a list of directories for transfer.
    directories = {
                   direction_name: [transfer_settings.paths[direction_name][location]]
                   for direction_name in direction_names
                   }
    print ''
    print 'Directories to copy: '
    print directories

    # Get a list of directories to skip transferring.
    skiplist = transfer_settings.skip_array[direction][location]
    print ''
    print 'Items to skip: '
    print skiplist


    # Transfer the files.
    print ''
    print "Downloading..." if direction == 'down' else "Uploading..."

    for i, directory in enumerate(directories[opposite_direction_names[direction]]):
        transfer_tree(
                      dir_src=directory,
                      dir_dst=directories[direction][i],
                      skiplist=skiplist,
                      overwrite=overwrite,
                      duplicate=duplicate,
                      )

    print ''
    print "Transfer complete."



def handleRemoveReadonly(func, path, exc):
    # Handles readonly errors by setting files to readable.
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise



class ProgressCount:
    # Tracks progress of a process operating over a list.

    def __init__(self, listlength, milestonesize = 25):
        self.listlength = listlength
        self.milestonesize = milestonesize
        self.progress = 0
        self.milestone = 0

    def increment(self):
        self.progress += 1
        progress_percent = (self.progress / self.listlength) * 100
        if progress_percent >= self.milestone:
            if progress_percent < 100:
                print round(progress_percent), '% ... '
            else:
                print '100%'
            self.milestone = self.milestone + self.milestonesize



def transfer_tree(dir_src, dir_dst, skiplist=[], overwrite='no', duplicate='no',
                  symlinks=False, ignore=None):
    # Transfers tree and files from dir_src to dir_dst.

    # Initialize progress trackers.
    counter_copy = ProgressCount(len(os.listdir(dir_src)))
    counter_delete = ProgressCount(len(os.listdir(dir_src)))

	# Checks for duplicate files and folders at destination. If such exist,
    # checks overwrite variable and either deletes originals in prep for
    # overwrite or aborts.
    print ''
    print 'Checking', dir_dst, 'for duplicate files and folders...'

    # Construct a list of duplicate paths.
    deletelist = []
    for item in os.listdir(dir_src):
        d = os.path.join(dir_dst, item)
        if (os.path.exists(d)) and (d not in skiplist):
            deletelist.append(d)

    # Either delete the duplicates or report skip.
    if len(deletelist) > 0:
        if overwrite == 'yes':
            print 'File or folder exists at destination and overwrite set to True.'
            print 'Deleting', len(deletelist), 'files and/or folders.'
            counter_overwrite = ProgressCount(len(deletelist))
            for item in deletelist:
                send2trash(item)
                '''if os.path.isdir(item):
                    shutil.rmtree(item, ignore_errors=False, onerror=handleRemoveReadonly)
                else:
                    os.remove(item)'''
                counter_overwrite.increment()
        else:
            print 'File or folder exists at destination and overwrite set to False.'
            print 'Transfer aborted.'
            sys.exit()

    # Copy files over to destination.
    print ''
    print 'Copying', dir_src, 'to', dir_dst

    for item in os.listdir(dir_src):
        s = os.path.join(dir_src, item)
        d = os.path.join(dir_dst, item)
        if s not in skiplist:
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        counter_copy.increment()

    # Delete source files.
    if duplicate == 'no':
        print ''
        print "Deleting original..."

        for item in os.listdir(dir_src):
            s = os.path.join(dir_src, item)
            if s not in skiplist:
                send2trash(s)
                '''if os.path.isdir(s):
                    shutil.rmtree(s, ignore_errors=False, onerror=handleRemoveReadonly)
                else:
                    os.remove(s)'''
            counter_delete.increment()




if __name__ == "__main__":
    #transfer_stick()
    key = 2
    for config in transfer_settings.config_sets[key]:
        transfer_stick(configuration=config)
