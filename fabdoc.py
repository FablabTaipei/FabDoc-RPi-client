import os, sys, getopt, hashlib, math, base64, time
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO
from PIL import Image
from cStringIO import StringIO

size = 480, 480
socket = None
strPath = None

# ===== Generate Thumbnail =====
# def genThumbnail(strFileIn):
#     outfile = os.path.splitext(strFileIn)[0] + ".thumbnail"
#     if (strFileIn != outfile) :  # and (os.path.isfile(outfile) != True) :
#         try:
#             im = Image.open(strFileIn)
#             im.thumbnail(size)
#             im.save(outfile, "JPEG")
#             return 1
#         except IOError:
#             print "cannot create thumbnail for", strFileIn
#     return 0        

# def genThumbnailForDirectory(strFilePathIn):
#     print " Create thumbnail for: ", strFilePathIn
#     intCount=0
#     for root, dirs, files in os.walk(strFilePathIn):
#         for file in files:
#             if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".PNG") or file.endswith(".bmp") or file.endswith(".BMP"):
#                  print(intCount)
#                  strFileName = os.path.join(root, file)
#                  print(strFileName)
#                  intCount = intCount + genThumbnail(strFileName)
#     print "Thumbnail generated: ", intCount
#     return intCount

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

def on_connect_error(error):
	print 'Connect Error:', error

def on_error(error):
	print 'Error:', error

def walk_pass_images(path):
	for root, dirs, files in os.walk(os.path.abspath(path)):
		for file in files:
			if file.endswith((".jpg",".JPG",".jpeg",".JPEG",".png",".PNG",".bmp",".BMP")):
				strFileName = os.path.join(root, file)
				# wait 2 seconds
				# resize and generate base64
				# pass to server
				try:
					output = StringIO()
					im = Image.open(strFileName)
					im.thumbnail(size)
            		# im.save(outfile, "JPEG")
					im.save(output, format='PNG')
					im_data = output.getvalue()
					# data_url = 'data:image/png;base64,' + base64.b64encode(im_data)
					if socket is not None:
						base64Data = base64.b64encode(im_data)
						socket.emit("pass_compressed_image", { 'base64': base64Data, 'type': 'image/png' } )
				except IOError:
					print "cannot generate base64 for: ", strFileName
				time.sleep(2)

def on_connect():
	if strPath is not None:
		walk_pass_images(strPath)

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
		elif opt in ("-H", "--host"):
			strHost = arg
		elif opt in ("-p", "--port"):
			strPort = arg
		elif opt in ("-t", "--token"):
			hashcode = arg
	if len(opts) == 0 or hashcode == "":
		print strHelpText
		sys.exit(2)

	# generate hash
	# hashcode = genHashCode(strUser, strPassword)

	print "token: ", hashcode

	try:
		# SocketIO(
		#     localhost, 8000,
		#     params={'q': 'qqq'},
		#     headers={'Authorization': 'Basic ' + b64encode('username:password')},
		#     cookies={'a': 'aaa'},
		#     proxies={'https': 'https://proxy.example.com:8080'})
	    socket = SocketIO(strHost, int(strPort), wait_for_connection=False, params={ 'token': hashcode } )
	    socket.on('connect_error', on_connect_error)
	    socket.on('error', on_error)
	    socket.on('connect', on_connect)
	    socket.wait()
	except ConnectionError:
	    print('The server is down. Try again later.')


if __name__ == "__main__":
	main(sys.argv[1:])
