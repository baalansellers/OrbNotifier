import pexpect, numpy
import threading, Queue, time

SLEEP_SEC = 0.001

def grange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def npindex(alist, target):
    i = 0
    for x in alist:
        if numpy.array_equal(x, target): return i
        i += 1
    return None

class ColorificWorker(threading.Thread):
    RED = numpy.array([255,0,0])
    ORANGE = numpy.array([255,102,0])
    YELLOW = numpy.array([255,255,0])
    GREEN = numpy.array([0,255,0])
    AQUA = numpy.array([0,255,255])
    SKYBLUE = numpy.array([0,102,255])
    BLUE = numpy.array([0,0,255])
    PURPLE = numpy.array([102,0,255])
    FUCHSIA = numpy.array([255,0,255])
    PINK = numpy.array([255,0,102])
    WHITE = numpy.array([0,0,0])

    def __init__(self, notification_q, mac):
        super(ColorificWorker, self).__init__()
        self.notification_q = notification_q
        self.stoprequest = threading.Event()
        self.mac = mac
        self.currentcolor = ColorificWorker.WHITE
        self.faderorder = [ColorificWorker.RED, ColorificWorker.ORANGE, ColorificWorker.YELLOW, ColorificWorker.GREEN, ColorificWorker.AQUA, ColorificWorker.SKYBLUE, ColorificWorker.BLUE, ColorificWorker.PURPLE, ColorificWorker.FUCHSIA, ColorificWorker.PINK]
        self.currentfadecolor = ColorificWorker.RED
        self.fadertrigger = 0
        self.alerton = 0
        self.reconnecttrigger = 0
        
        self.bulb_connect()
        self.color_shift(ColorificWorker.BLUE)

    def run(self):
        while not self.stoprequest.isSet():
            try:
                cmd = self.notification_q.get(True, 0.05)
                if cmd == 'alert_mention':
                    self.alert_mention()
                if cmd == 'alert_im':
                    self.alert_im()
                if cmd == 'alert_channel':
                    self.alert_channel()

            except Queue.Empty:
                curtime = int(time.time())
                if curtime % 60 == 0:
                    self.fadertrigger = 1
                    self.reconnecttrigger = 1
                else:
                    if self.reconnecttrigger == 1:
                        self.gatt.sendline('disconnect')
                        self.bulb_connect()
                    if self.fadertrigger == 1 and self.alerton == 0:
                        self.fadertrigger = 0
                        self.fader_next()
                continue

    def close(self, timeout=None):
        self.gatt.sendline('disconnect')
        self.gatt.sendline('exit')
        self.stoprequest.set()
        super(ColorificWorker, self).join(timeout)

    def bulb_connect(self):
        self.gatt = pexpect.spawn('gatttool -I')
        self.gatt.sendline('connect {0}'.format(self.mac))
        try:
            self.gatt.expect(['successful','[CON]'])
        except EOF:
            print('Received EOF')
            self.close()
        except TIMEOUT:
            print('Timeout Elapsed')
            self.close()

    def nrgbstr(self, narray):
        r, g, b = map(lambda a: int(a), narray)
        return self.rgbstr(r, g, b)

    def rgbstr(self, r, g, b):
        return '{0:02X}{1:02X}{2:02X}'.format(r, g, b)

    def color_shift(self, newcolor):
        if self.currentcolor == None:
            self.color_change(newcolor)
            return
        lnvector = newcolor - self.currentcolor
        for x in grange(0.05, 1.00, 0.05):
            tempcolor = self.currentcolor + lnvector * x
            self.gatt.sendline('char-write-cmd 0x0028 580103014000'+self.nrgbstr(tempcolor))
            time.sleep(SLEEP_SEC)
        self.currentcolor = newcolor

    def color_change(self, newcolor):
        self.gatt.sendline('char-write-cmd 0x0028 580103014000'+self.nrgbstr(newcolor))
        self.currentcolor = newcolor

    def fader_next(self):
        fi = npindex(self.faderorder, self.currentfadecolor) + 1
        if fi == len(self.faderorder): fi = 0
        self.color_shift(self.faderorder[fi])
        self.currentfadecolor = self.faderorder[fi]

    def alert_mention(self):
        self.alerton = 1
        for x in range(20):
            self.color_change(ColorificWorker.RED)
            time.sleep(SLEEP_SEC)
            self.color_change(ColorificWorker.YELLOW)
        self.color_shift(self.currentfadecolor)
        self.alerton = 0

    def alert_im(self):
        self.alerton = 1
        for x in range(20):
            self.color_change(ColorificWorker.BLUE)
            time.sleep(SLEEP_SEC)
            self.color_change(ColorificWorker.GREEN)
        self.color_shift(self.currentfadecolor)
        self.alerton = 0

    def alert_channel(self):
        self.alerton = 1
        for x in range(20):
            self.color_change(ColorificWorker.PINK)
            time.sleep(SLEEP_SEC)
            self.color_change(ColorificWorker.AQUA)
        self.color_shift(self.currentfadecolor)
        self.alerton = 0
