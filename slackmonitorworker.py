import websocket, json, urllib, urllib2
import threading, Queue, time
from colorificworker import ColorificWorker

OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
CHANNELALERT = '!channel'

def CleanMsgUnicode(targetstr):
    if not targetstr.startswith('{"type":'): return None
    return ''.join([i if ord(i) < 128 else '' for i in targetstr]).replace('\n','')

class SlackMonitorWorker(threading.Thread):
    def __init__(self, token, mac):
        super(SlackMonitorWorker, self).__init__()
        self.stoprequest = threading.Event()
        self.token = token
        self.mac = mac
        self.slack_json = self.slack_auth()
        self.userid = self.slack_json['self']['id']
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
                msg = CleanMsgUnicode(data)
                try:
                    with open('slackmsg.log','a') as f:
                        f.write(msg + '\n')
                except:
                    pass

            if msg:
                #print(msg)
                try:
                    msgj = json.loads(msg)
                    if msgj['type'] == 'message':
                        if 'text' in msgj and self.userid in str(msgj['text']):
                            self.alert_q.put('alert_mention')
                        if 'text' in msgj and 'user' in msgj and CHANNELALERT in str(msgj['text']) and self.userid not in str(msgj['user']):
                            self.alert_q.put('alert_channel')
                        if 'channel' in msgj and 'user' in msgj and self.is_channel_im(str(msgj['channel'])) and self.userid not in str(msgj['user']):
                            self.alert_q.put('alert_im')
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
        try:
            with open('slackmsg.log','a') as f:
                f.write('SERVICE CLOSED\n')
        except:
            pass
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

    def is_channel_im(self, channelid):
        for im in self.slack_json['ims']:
            if channelid == im['id']: return True
        return False

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

    
