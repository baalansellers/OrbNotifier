import websocket, json, urllib, urllib2
import threading, Queue, time
from colorificworker import ColorificWorker

OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
CHANNELALERT = '!channel'

def CleanStrUnicode(targetstr):
    return ''.join([i if ord(i) < 128 else '' for i in targetstr])

class SlackMonitorWorker(threading.Thread):
    def __init__(self, token, userid, mac):
        super(SlackMonitorWorker, self).__init__()
        self.stoprequest = threading.Event()
        self.token = token
        self.userid = CleanStrUnicode(userid)
        self.mac = mac
        self.slack_json = self.slack_auth()
        #print self.slack_json
        self.ws = websocket.create_connection(self.slack_json['url'])
        self.alert_q = Queue.Queue()
        self.cw = ColorificWorker(self.alert_q, mac)
        self.cw.start()

    def run(self):
        while not self.stoprequest.isSet():
            try:
                opcode, data = self.recv()
            except websocket.WebSocketConnectionClosedException:
                try:
                    self.close()
                except:
                    pass
                return
            msg = None
            if opcode in OPCODE_DATA:
                msg = CleanStrUnicode(data)

            if msg:
                #print(msg)
                try:
                    with open('slackmsg.log','a') as f:
                        f.write(msg + '\n')
                except:
                    pass
                
                try:
                    if self.userid in msg:
                        self.alert_q.put('alert_red')
                except UnicodeDecodeError:
                    print('Unicode Decode Error while searching msg for userid.')
                    print('userid: {0}'.format(self.userid))
                    print('msg: {0}'.format(msg))
                    continue
                
                try:
                    if CHANNELALERT in msg:
                        self.alert_q.put('alert_red')
                except UnicodeDecodeError:
                    print('Unicode Decode Error while searching msg for CHANNELALERT.')
                    continue

    def close(self, timeout=None):
        self.ws.close()
        self.cw.close()
        self.stoprequest.set()
        super(SlackMonitorWorker, self).join(timeout)

    def slack_auth(self):
        url = 'https://slack.com/api/rtm.start?'
        params = {'pretty':'1','token':self.token}
        urlparams = urllib.urlencode(params)
        response = urllib2.urlopen(url+urlparams)
        data = response.read()
        startrsp = data.decode('utf-8')
        return json.loads(startrsp)

    def recv(self):
        frame = self.ws.recv_frame()
        if not frame:
            raise websocket.WebSocketException("Not a valid frame {0}".format(frame))
        elif frame.opcode in OPCODE_DATA:
            return (frame.opcode, frame.data)
        elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
            self.ws.send_close()
            return (frame.opcode, None)
        elif frame.opcode == websocket.ABNF.OPCODE_PING:
            self.ws.pong("Hi!")

        return None, None

    
