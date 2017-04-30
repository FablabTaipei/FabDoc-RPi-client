# FabDoc-python-client
Pass images through socketIO on device. (alpha)

### Progress
- Write help text and parse parameters. (done)
- Make "commit" command works. (pending)
- Generate MD5 for user and password. (done)
- Handle images for scale down and encode to base64. (done)
- Connect with remote server. (done)
- Bind the socket events for communicate with server.
  - In "reconnecting" situation: (Maybe use the same way in first time connection)
    - Pass file list to server.
    - Get index range and which image has sent from server. (ex: index 21 to 40 of 2234 images)
    - Pass thumbnail of that unsent images.
    - Still keep file change detection.
- Detect file changes and pass the image to server. (done)
- (thinking...)

### Before use...
```
pip install -U socketIO-client
pip install watchdog
```

### Usage

```
python fabdoc.py -s yourpath -t yourtoken
```

##### Examples
```
python fabdoc.py -s ./test/ -p 5000 -t e25339f8697bd2c3574931c93ecbb721
python fabdoc.py -H 123.12.12.12 -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
```
