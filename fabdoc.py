import os, sys, getopt, hashlib, math, base64, time
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO, BaseNamespace
from PIL import Image
from cStringIO import StringIO
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from urllib import quote_plus

import capture
from threading import Thread
from Queue import Queue

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

imageQueue = Queue()

class AutoEmitImage(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.daemon = True
		self.start()

	def run(self):
		while True:
			global imageQueue
			global socket
			if not imageQueue.empty() and socket is not None and socket.connected:
				p = imageQueue.get()
				pass_thumbnail_image(p)
			time.sleep(2)


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
		# push a file path into queue
		global imageQueue
		imageQueue.put(event.src_path)

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
			print strFilePath, "passed"
	except IOError:
		print "cannot generate base64 for: ", strFullFilePath

# wait 2 seconds and pass thumbnail image to server for each image file
def walk_pass_images(path):
	global imageQueue
	for root, dirs, files in os.walk(os.path.abspath(path)):
		for file in files:
			if file.endswith((".jpg",".JPG",".jpeg",".JPEG",".png",".PNG",".bmp",".BMP")):
				toPassPath = strPath + file
				# push a file path into queue
				imageQueue.put(toPassPath)
				print "Push", toPassPath, "into queue"


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
		print 'connected'

	def on_disconnect(*data):
	    print 'disconnect'

	def on_reconnect(*data):
		print 'reconnect'


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

	# Make a queue of image paths for socket emit
	AutoEmitImage()

	# Detect file changes from input path and pass path to queue
	observer_start(strPath)
	
	# Pass current files in input path to queue
	walk_pass_images(strPath)

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

