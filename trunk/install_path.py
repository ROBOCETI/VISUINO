import os, site

DIRECTORY_TO_ADD = os.getcwd()
PATH_FILENAME = "visuino.pth"

if not os.path.isdir(site.USER_SITE):
    os.makedirs(site.USER_SITE)

path_file = os.path.join(site.USER_SITE, PATH_FILENAME)

with open(path_file, "a") as f:
    f.write('\n' + DIRECTORY_TO_ADD)

if os.listdir(site.USER_SITE).count(PATH_FILENAME):
    print('INSTALLATION SUCCESSFULL!\n')
    print('The following directory was added to the PYTHONPATH:')
    print(DIRECTORY_TO_ADD)
    print('\nRegistered in the file \'%s\' on site.USER_SITE path:' % PATH_FILENAME)
    print(site.USER_SITE)
else:
    print('INSTALLATION FAIL!\n')
    print('ERROR: The following directory couldn\'t be added to de PYTHONPATH:')
    print(DIRECTORY_TO_ADD)

input()
