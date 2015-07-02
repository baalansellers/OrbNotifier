import websocket, json, urllib, urllib2
import threading, Queue, time
from colorificworker import ColorificWorker

OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
ALANTAG = '@usertag here'
CHANNELALERT = '!channel'

class SlackMonitorWorker(threading.Thread):
    def __init__(self):
        super(SlackMonitorWorker, self).__init__()
        self.stoprequest = threading.Event()
        self.slack_json = self.slack_auth()
        #print self.slack_json
        self.ws = websocket.create_connection(self.slack_json['url'])
        self.alert_q = Queue.Queue()
        self.cw = ColorificWorker(self.alert_q)
        self.cw.start()

    def run(self):
        while not self.stoprequest.isSet():
            opcode, data = self.recv()
            msg = None
            if opcode in OPCODE_DATA:
                msg = "< %s" % data

            if msg:
                print(msg)
                if ALANTAG in msg:
                    self.alert_q.put('alert_red')

                if CHANNELALERT in msg:
                    self.alert_q.put('alert_red')

    def close(self, timeout=None):
        self.ws.close()
        self.cw.close()
        self.stoprequest.set()
        super(SlackMonitorWorker, self).join(timeout)

    def slack_auth(self):
        url = 'https://slack.com/api/rtm.start?'
        params = {'pretty':'1','token':'your slack api token here'}
        urlparams = urllib.urlencode(params)
        response = urllib2.urlopen(url+urlparams)
        data = response.read()
        startrsp = data.decode('utf-8')
        return json.loads(startrsp)

    def recv(self):
        frame = self.ws.recv_frame()
        if not frame:
            raise websocket.WebSocketException("Not a valid frame %s" % frame)
        elif frame.opcode in OPCODE_DATA:
            return (frame.opcode, frame.data)
        elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
            self.ws.send_close()
            return (frame.opcode, None)
        elif frame.opcode == websocket.ABNF.OPCODE_PING:
            self.ws.pong("Hi!")

        return None, None

    
