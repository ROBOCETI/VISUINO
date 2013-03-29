import os

BUILD_PATH = 'build/exe.win32-3.3'

os.system("python setup_exe.py build")

if os.name == 'nt':
	BUILD_PATH = BUILD_PATH.replace('/', '\\')

if os.access(BUILD_PATH, os.R_OK):
	os.startfile(BUILD_PATH)

print("\nFinished! Press any key to quit...")
str(input())