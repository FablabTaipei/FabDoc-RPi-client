# FabDoc-python-client
Pass images through socketIO on device. (alpha)

### Progress
- Write help text and parse parameters. (done)
- Make "commit" command works.
- Generate MD5 for user and password. (done)
- Handle images for scale down and encode to base64.
- Connect with remote server.
- Bind the socket events for communicate with server.
- (thinking...)

### Usage

```
python fabdoc.py -s yourpath -t yourtoken
```

##### Examples
```
python fabdoc.py -s ./test/ -p 5000 -t e25339f8697bd2c3574931c93ecbb721
python fabdoc.py -H 123.12.12.12 -s ./test/ -t e25339f8697bd2c3574931c93ecbb721
```
