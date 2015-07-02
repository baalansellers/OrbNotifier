import Queue, time, numpy

from colorificworker import ColorificWorker


def main():
    notification_q = Queue.Queue()

    cw = ColorificWorker(notification_q)

    cw.start()
    cw.alert_red()
    time.sleep(5)
    cw.color_shift(cw.BLUE)
    time.sleep(5)
    cw.alert_red()
    time.sleep(20)
    cw.join()
    #while True:
        #try:
            #test = 1
        #except KeyboardInterrupt:
            #smw.join()
            #return
        #except EOFError:
            #smw.join()
            #return


if __name__ == '__main__':
    main()
