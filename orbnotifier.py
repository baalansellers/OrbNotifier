import os, json
from slackmonitorworker import SlackMonitorWorker

def main():
    if os.path.isfile('orbnotifier.config'):
        with open('orbnotifier.config', 'r') as f:
            conf = json.load(f)
    else:
        conf = {'token':'','mac':''}
        with open('orbnotifier.config', 'w') as f:
            json.dump(conf, f)
        print('No orbnotifier.config file found, I created one for you, please fill in the nessary data before running again.')
        return

    try:
        if conf['token'] == '':
            print('You seem to be missing a token, please add one to your orbnotifier.config file.')
            return
    except KeyError:
        print('You seem to be missing a token, please add one to your orbnotifier.config file.')
        return

    try:
        if conf['mac'] == '':
            print('You seem to be missing a mac, please add one to your orbnotifier.config file.')
            return
    except KeyError:
        print('You seem to be missing a mac, please add one to your orbnotifier.config file.')
        return

    print('Type quit or exit to stop service.')
    
    smw = SlackMonitorWorker(conf['token'], conf['mac'])
    smw.start()
    while True:
        try:
            msgin = raw_input()
            if msgin == 'quit':
                smw.close()
                print('Goodbye!')
                return
            if msgin == 'exit':
                smw.close()
                print('Goodbye!')
                return
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
