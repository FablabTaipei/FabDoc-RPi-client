# FabDoc-python-client
To capture time-lapse pictures as pre-commits, this script helps you stream pictures taken by Raspberry Pi Zero (W) and camera module through socketIO to your own browser, hosted by [FabDoc-console](https://github.com/FablabTaipei/FabDoc-console).

### Progress
- Write help text and parse parameters. (done)
- Generate MD5 for user and password. (done)
- Handle images for scale down and encode to base64. (done)
- Connect with remote server. (done)
- Detect file changes and pass the image to server. (done)
- Login into your account by scanning QR code token on your browser. (done)
- Make "commit" command works. (pending)
- Bind the socket events for communicate with server.
  - In "reconnecting" situation: (Maybe use the same way in first time connection)
    - Pass file list to server.
    - Get index range and which image has sent from server. (ex: index 21 to 40 of 2234 images)
    - Pass thumbnail of that unsent images.
    - Still keep file change detection.
- Support IMU input to control and capture videos or GIFs by head motion.

### Before use...
```
pip install -U socketIO-client
pip install picamera watchdog zbarlight scipy
```

### Usage

```
python fabdoc.py -H IP_ADDRESS -p PORT -s IMAGE_PATH -t TOKEN
```

### Examples
##### Without QR code token
```
python fabdoc.py -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
python fabdoc.py -H 123.12.12.12 -p 5000 -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
```
##### With QR code token
![](https://cdn.hackaday.io/images/5865411493623390927.png)
```
python fabdoc.py -H 123.12.12.12 -p 5000 -s ./test/
```
