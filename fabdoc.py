import sys, getopt, hashlib, math
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO
from PIL import Image
from cStringIO import StringIO

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
    -U, --user <username>     Website username.
    -P, --pass <password>     Website password.

"""

def genHashCode(u, p):
	strFirstHash = ""
	strLong = ""
	strShort = ""
	if len(u) > len(p):
		strLong = u
		strShort = p
	else:
		strLong = p
		strShort = u
	# fisrt hash
	intLongLen = len(strLong)
	intShortLen = len(strShort)
	intUnit = int(round(float(intLongLen) / float(intShortLen)))
	for idx in range(intShortLen + 1):
		strFirstHash = strFirstHash + strLong[(idx * intUnit):((idx + 1) * intUnit)]
		if idx != intShortLen:
			strFirstHash = strFirstHash + strShort[idx]
	# secondary hash
	strLeft = strFirstHash[:len(strFirstHash)/2]
	strRight = strFirstHash[len(strFirstHash)/2:]
	strLeftHash = ""
	strRightHash = ""
	intLeftLen = len(strLeft)
	intRightLen = len(strRight)
	while intLeftLen:
		if intLeftLen % 2:
			intLeftMid = int(math.floor(intLeftLen / 2))
		else:
			intLeftMid = intLeftLen / 2
		strLeftHash = strLeftHash + strLeft[intLeftMid]
		strLeft = strLeft[:intLeftMid] + strLeft[intLeftMid+1:]
		intLeftLen = len(strLeft)
	while intRightLen:
		if intRightLen % 2:
			intRightMid = int(math.floor(intRightLen / 2))
		else:
			intRightMid = intRightLen / 2
		strRightHash = strRightHash + strRight[intRightMid]
		strRight = strRight[:intRightMid] + strRight[intRightMid+1:]
		intRightLen = len(strRight)
	strManualResult = strLeftHash + strRightHash
	# ===== generate MD5 =====
	m = hashlib.md5()
	m.update(strManualResult)
	return m.hexdigest()

#Main
def main(argv):
	strPath = "./" # current path
	strHost = "localhost"
	strPort = "80"
	strUser = ""
	strPassword = ""
	try:
		opts, args = getopt.getopt(argv,"hs:H:p:U:P:",["help","source","host","port","user","pass"])
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
		elif opt in ("-U", "--user"):
			strUser = arg
		elif opt in ("-P", "--pass"):
			strPassword = arg
	if len(opts) == 0 or strUser == "" or strPassword == "":
		print strHelpText
		sys.exit(2)

	# generate hash
	hashcode = genHashCode(strUser, strPassword)
	print hashcode

	# try:
	#     socket = SocketIO(strHost, int(strPort), wait_for_connection=False)
	#     socket.wait()
	# except ConnectionError:
	#     print('The server is down. Try again later.')


if __name__ == "__main__":
	main(sys.argv[1:])
