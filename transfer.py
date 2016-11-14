#! python3
#File: transfer.py

def handleRemoveReadonly(func, path, exc):
    """Handles readonly errors by setting files to readable."""

    #Import modules---
    import errno, os, stat, shutil
    #-----------------

    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise

class ProgressCount:
    """Tracks progress of a process operating over a list."""

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

def transfer_tree(dir_src, dir_dst, skiplist=[], overwrite='no', duplicate='no', symlinks=False, ignore=None):
    """Transfers tree and files from dir_src to dir_dst."""

    #Note that this variation of the copytree isn't entirely consistent with the
    #standard copytree:
    #   *it doesn't honor symlinks and ignore parameters for the root directory of the
    #	 src tree;
    #   *it doesn't raise shutil.Error for errors at the root level of src;
    #   *in case of errors during copying of a subtree, it will raise shutil.Error for
    #	 that subtree instead of trying to copy other subtrees and raising single
    #    combined shutil.Error.

    #Import modules---
    import os, shutil
    from send2trash import send2trash
    #-----------------

    #Variables---

    #------------

    counter_copy = ProgressCount(len(os.listdir(dir_src)))
    counter_delete = ProgressCount(len(os.listdir(dir_src)))

	# Checks for duplicate files and folders at destination. If such exist, checks
    # overwrite variable and either deletes originals in prep for overwrite or aborts.
    print 'Checking', dir_dst, 'for duplicate files and folders...'

    deletelist = []
    for item in os.listdir(dir_src):
        d = os.path.join(dir_dst, item)
        if (os.path.exists(d)) and (d not in skiplist):
            deletelist.append(d)
    if len(deletelist) > 0:
        if overwrite == 'yes':
            print 'File or folder exists at destination and overwrite set to True. \
            \nDeleting', len(deletelist), 'files and/or folders.'
            counter_overwrite = ProgressCount(len(deletelist))
            for item in deletelist:
                send2trash(item)
                '''if os.path.isdir(item):
                    shutil.rmtree(item, ignore_errors=False, onerror=handleRemoveReadonly)
                else:
                    os.remove(item)'''
                counter_overwrite.increment()
        else:
            print 'File or folder exists at destination and overwrite set to False. \
            \nTransfer aborted.'
            import sys
            sys.exit()

    # Copies files over to destination.
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

    # Deletes source files.
    if duplicate == 'no':
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


def transfer_stick(direction=None, location=None, duplicate='yes', overwrite='no'):
    """Downloads or uploads from one set of directories to another."""

    #Import modules---
    import os
    #-----------------

    #Variables---
    configs = {
    1: ['down', 'work', 'yes', 'yes'],
    2: ['up', 'work', 'yes', 'yes'],
    3: ['down', 'home', 'yes', 'yes'],
    4: ['up', 'home', 'yes', 'yes']
    }
    pathbase = {
    'up':
    {'home': 'E:\\', 'work': 'D:\\'},
    'down':
    {'home': 'C:\\Users\\Grav\\Desktop\\', 'work': 'C:\\Users\\Michael Gravina\\Desktop\\'}
    }
    pathend = {'up': ['Transfer\\'],
    'down': ['Transfer\\']}
    skiparray = {
    'up':
    {'home': [], 'work': ['']},
    'down':
    {'home': ['E:\\Transfer\\CompMem'], 'work': []}
    }

    while not(direction in ['up', 'down'] and location in ['home', 'work'] and
    duplicate in ['yes', 'no'] and overwrite in ['yes', 'no']):
        configuration = input('Configuration? (1 - 4): ')
        try:
            configuration = int(configuration)
        except ValueError:
            configuration = None
        if configuration in [1, 2, 3, 4]:
                direction, location, duplicate, overwrite = configs[int(configuration)]
        else:
            print 'direction =', direction, ', location =', location, ', duplicate =',
            duplicate, 'overwrite =', overwrite
            direction = input('Parameters not all entered correctly when script called' +
            ' and no valid configuration selected. \nEnter direction (up or down): ')
            location = input('Enter location (home or work): ')
            duplicate = input('Enter whether to duplicate (yes or no): ')
            overwrite = input('Enter overwrite permission (yes or no): ')

    dir_up = [None] * len(pathend['up'])
    for i, j in enumerate(pathend['up']):
        dir_up[i] = os.path.join(pathbase['up'][location], j)

    dir_dwn = [None] * len(pathend['down'])
    for i, j in enumerate(pathend['down']):
        dir_dwn[i] = os.path.join(pathbase['down'][location], j)

    skiplist = skiparray[direction][location]
    print 'Items to skip: ', skiplist
    #------------

    if direction == 'down':
        print "Downloading from stick..."
        for item in dir_up:
            index = dir_up.index(item)
            transfer_tree(dir_src=dir_up[index], dir_dst=dir_dwn[index], skiplist=skiplist, overwrite=overwrite, duplicate=duplicate)

    if direction == 'up':
        print "Uploading to stick..."
        for item in dir_dwn:
            index = dir_dwn.index(item)
            transfer_tree(dir_src=dir_dwn[index], dir_dst=dir_up[index], skiplist=skiplist, overwrite=overwrite, duplicate=duplicate)

    print "Transfer complete."


#Code to make module into script-----------
if __name__ == "__main__":
    transfer_stick()
    #transfer_stick(sys.argv[1])
#------------------------------------------
