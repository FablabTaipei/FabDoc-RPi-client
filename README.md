# FabDoc-RPi-client
To capture time-lapse pictures as pre-commits, this script helps you stream pictures taken by **Raspberry Pi Zero (W)** and **camera module** through socketIO to your own browser, hosted by [FabDoc-console](https://github.com/FablabTaipei/FabDoc-console).

### Progress
- [x] Write help text and parse parameters
- [x] Generate MD5 for user and password
- [x] Handle images for scale down and encode to base64
- [x] Connect with remote server
- [x] Detect file changes and pass the images to server
- [x] Login into your account by scanning QR code token on your browser.
- [ ] To commit, receive image upload request from browser via WebSocket, and pass original images into db
- [ ] Solve reconnection situation
  - Get index list of preview images which have been sent to server
- [ ] Support IMU input to control and capture videos or GIFs by head motion.

### Dependency
```
pip install -U socketIO-client
pip install picamera watchdog zbarlight scipy
```

### Usage
```
python fabdoc.py -H IP_ADDRESS -p PORT -s IMAGE_PATH -t TOKEN
```



## Examples
##### Without QR code token
```
python fabdoc.py -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
python fabdoc.py -H 123.12.12.12 -p 5000 -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
```
##### With QR code token
```
python fabdoc.py -H 123.12.12.12 -p 5000 -s ./test/
```
![](https://cdn.hackaday.io/images/5865411493623390927.png)
