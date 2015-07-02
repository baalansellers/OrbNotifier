from slackmonitorworker import SlackMonitorWorker

def main():
    smw = SlackMonitorWorker()
    smw.start()
    while True:
        try:
            test = 1
        except KeyboardInterrupt:
            print('keyboard interrupt')
            smw.close()
            return
        except EOFError:
            print('EOF Error')
            smw.close()
            return

if __name__ == '__main__':
    main()
