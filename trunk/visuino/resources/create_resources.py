import os

SUPPORTED_EXTENSIONS = ['png', 'ico', 'jpg', 'jpeg', 'bmp']

IMAGES_PATH = '.'
QRC_FILENAME = 'images.qrc'
OUTPUT_FILENAME = 'images.py'

START_QRC = \
"""<!DOCTYPE RCC><RCC version="1.0">
<qresource prefix="/">"""
END_QRC = \
"""</qresource>
<!-- compile this from the command line "pyrcc4 -py3 images.qrc -o images.py" -->
</RCC> 
"""
qrc_files = ''

image_files = [x for x in os.listdir(IMAGES_PATH) 
               if x[x.find(os.extsep)+1:] in SUPPORTED_EXTENSIONS]

print('\n')
if not image_files:
	print('No image file found!')
	input()
	exit()
			   
for x in image_files:
	qrc_files += '\n    <file>%s</file>' % x
	print('Registred file "%s"...' % x)
	
try:
	f = open(QRC_FILENAME, 'w')
	f.write(START_QRC + qrc_files + END_QRC)
	f.close()
except:
	print('\nFailed to create the resource file "%s"!' % QRC_FILENAME)
	input()
	exit()

print('\nSucessfully created the resource file "%s"!' % QRC_FILENAME)

print('\nTrying to compile it...')
os.system("pyrcc4 -py3 %s -o %s" % (QRC_FILENAME, OUTPUT_FILENAME))
if os.access(OUTPUT_FILENAME, os.R_OK):
	print('\nResource file "%s" was compiled OK!' % QRC_FILENAME)
	print('Output file "%s" was created sucessfully!' % OUTPUT_FILENAME)
else:
	print('\nFailed to compile the "%s" file!' % QRC_FILENAME)
	print('Output "%s" was not created!' % OUTPUT_FILENAME)
	
input()