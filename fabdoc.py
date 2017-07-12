import os, sys, getopt, hashlib, math, base64, time
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO, BaseNamespace
from PIL import Image
from cStringIO import StringIO
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from urllib import quote_plus

import capture
import threading

size = 480, 480
socket = None
strPath = None
observer = None

# ===== generate MD5 =====
# m = hashlib.md5()
# m.update("000005fab4534d05api_key9a0554259914a86fb9e7eb014e4e5d52permswrite")
# print m.hexdigest()

# ===== resize to the base64 =====
# output = StringIO()
# im.save(output, format='JPEG')
# im_data = output.getvalue()
# data_url = 'data:image/jpg;base64,' + base64.b64encode(im_data)

strHelpText = """
Usage:
    fabdoc <command> [options]

Commands:
    commit                    To start pre-commit process through socketIO.

Options:
    -h, --help                Show help.
    -s, --source <path>       Source path, default current path.
    -H, --host <hostname>     Host name, defaults to localhost.
    -p, --port <port>         Port, default 80.
    -t, --token <token>       Access Token, required.

"""

# def genHashCode(u, p):
# 	strFirstHash = ""
# 	strLong = ""
# 	strShort = ""
# 	if len(u) > len(p):
# 		strLong = u
# 		strShort = p
# 	else:
# 		strLong = p
# 		strShort = u
# 	# fisrt hash
# 	intLongLen = len(strLong)
# 	intShortLen = len(strShort)
# 	intUnit = int(round(float(intLongLen) / float(intShortLen)))
# 	for idx in range(intShortLen + 1):
# 		strFirstHash = strFirstHash + strLong[(idx * intUnit):((idx + 1) * intUnit)]
# 		if idx != intShortLen:
# 			strFirstHash = strFirstHash + strShort[idx]
# 	# secondary hash
# 	strLeft = strFirstHash[:len(strFirstHash)/2]
# 	strRight = strFirstHash[len(strFirstHash)/2:]
# 	strLeftHash = ""
# 	strRightHash = ""
# 	intLeftLen = len(strLeft)
# 	intRightLen = len(strRight)
# 	while intLeftLen:
# 		if intLeftLen % 2:
# 			intLeftMid = int(math.floor(intLeftLen / 2))
# 		else:
# 			intLeftMid = intLeftLen / 2
# 		strLeftHash = strLeftHash + strLeft[intLeftMid]
# 		strLeft = strLeft[:intLeftMid] + strLeft[intLeftMid+1:]
# 		intLeftLen = len(strLeft)
# 	while intRightLen:
# 		if intRightLen % 2:
# 			intRightMid = int(math.floor(intRightLen / 2))
# 		else:
# 			intRightMid = intRightLen / 2
# 		strRightHash = strRightHash + strRight[intRightMid]
# 		strRight = strRight[:intRightMid] + strRight[intRightMid+1:]
# 		intRightLen = len(strRight)
# 	strManualResult = strLeftHash + strRightHash
# 	# ===== generate MD5 =====
# 	m = hashlib.md5()
# 	m.update(strManualResult)
# 	return m.hexdigest()

# file detection
class FileDetectionHandler(PatternMatchingEventHandler):
	patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
	def process(self, event):
		"""
		event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
		# the file will be processed there
		print event.src_path, event.event_type
	def on_modified(self, event):
		self.process(event)
	def on_created(self, event):
		self.process(event)
		pass_thumbnail_image(event.src_path)

	def on_deleted(self, event):
		self.process(event)

# resize and generate base64
def pass_thumbnail_image(strFilePath):
	global socket
	try:
		# generate thumbnail
		output = StringIO()
		strFullFilePath = os.path.abspath(strFilePath)
		im = Image.open(strFullFilePath)
		im.thumbnail(size)
		im.save(output, format='PNG')

		# resize to the base64, dataurl format: 'data:image/png;base64,{base64_encoded_string}'
		im_data = output.getvalue()
		if socket is not None:
			base64Data = base64.b64encode(im_data)
			# pass to server
			socket.emit("pass_compressed_image", { 'base64': base64Data, 'type': 'image/png', 'filepath': quote_plus(strFilePath) } )
	except IOError:
		print "cannot generate base64 for: ", strFullFilePath

# wait 2 seconds and pass thumbnail image to server for each image file
def walk_pass_images(path):
	for root, dirs, files in os.walk(os.path.abspath(path)):
		for file in files:
			if file.endswith((".jpg",".JPG",".jpeg",".JPEG",".png",".PNG",".bmp",".BMP")):
				pass_thumbnail_image(strPath + file)
				time.sleep(2)

def observer_abort():
	global observer
	if observer is not None:
		observer.stop()
		observer.join()
		observer = None

def observer_start(p):
	global observer
	observer = Observer()
	observer.schedule(FileDetectionHandler(), path=p)
	observer.start()

# Socket event collection namespace
class SocketEventsNamespace(BaseNamespace):
	def on_connect_error(*errors):
		print 'Connect Error:', "%s" % list(errors)

	def on_error(*errors):
		print 'Error:', "%s" % list(errors)

	def on_connect(opt):
		global strPath
		if strPath is not None:
			observer_start(strPath)
			walk_pass_images(strPath)

	def on_disconnect(*data):
	    print 'disconnect'
	    observer_abort()

	def on_reconnect(*data):
		global strPath
		print 'reconnect'
		observer_abort()
		if strPath is not None:
			observer_start(strPath)


#Main
def main(argv):
	global strPath;
	global socket;

	strPath = "./" # current path
	strHost = "localhost"
	strPort = "80"
	# strUser = ""
	# strPassword = ""
	# try:
	# 	opts, args = getopt.getopt(argv,"hs:H:p:U:P:",["help","source","host","port","user","pass"])
	# except getopt.GetoptError:
	# 	print strHelpText
	# 	sys.exit(2)
	# print opts
	# for opt, arg in opts:
	# 	if opt in ("-h", "--help"):
	# 		print strHelpText
	# 		sys.exit(2)
	# 	elif opt in ("-s", "--source"):
	# 		strPath = arg
	# 	elif opt in ("-H", "--host"):
	# 		strHost = arg
	# 	elif opt in ("-p", "--port"):
	# 		strPort = arg
	# 	elif opt in ("-U", "--user"):
	# 		strUser = arg
	# 	elif opt in ("-P", "--pass"):
	# 		strPassword = arg
	# if len(opts) == 0 or strUser == "" or strPassword == "":
	# 	print strHelpText
	# 	sys.exit(2)

	hashcode = ""

	try:
		opts, args = getopt.getopt(argv,"hs:H:p:t:",["help","source","host","port","token"])
	except getopt.GetoptError:
		print strHelpText
		sys.exit(2)
	print opts
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print strHelpText
			sys.exit(2)
		elif opt in ("-s", "--source"):
			strPath = arg
			if not strPath.endswith("/"):
				strPath = strPath + "/"
		elif opt in ("-H", "--host"):
			strHost = arg
		elif opt in ("-p", "--port"):
			strPort = arg
		elif opt in ("-t", "--token"):
			hashcode = arg
	if len(opts) == 0:
		print strHelpText
		sys.exit(2)

	# generate hash
	# hashcode = genHashCode(strUser, strPassword)

	# Capture QR code in thread
	camera = capture.Camera( path = strPath )
	camera.run()

	while(1):
		if camera.isDecoded:
			hashcode = camera.code
			print hashcode
			break

	print "token: ", hashcode

	try:
		# SocketIO(
		#     localhost, 8000,
		#     params={'q': 'qqq'},
		#     headers={'Authorization': 'Basic ' + b64encode('username:password')},
		#     cookies={'a': 'aaa'},
		#     proxies={'https': 'https://proxy.example.com:8080'})
		socket = SocketIO(strHost, int(strPort), wait_for_connection=False, params={ 'token': hashcode } )
		socket.define(SocketEventsNamespace)
		socket.wait()
	except:
		print "Error: ", sys.exc_info()[0]
		observer_abort()
		raise

if __name__ == "__main__":
	main(sys.argv[1:])

