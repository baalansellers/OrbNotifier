# OrbNotifier
Bluetooth RGB LED bulb that notifies (blinks) on mentions of your user id (@username) or @channel.

##Configuration:
  - Requst an API key/token from Slack: https://api.slack.com/web
  - Test out your token with the rtm.start API call: https://api.slack.com/methods/rtm.start/test
  - Search for and note your user id, in the returned JSON from rtm.start: self.id
  - Find your Colorific Bulb's MAC address: `sudo hcitool lescan`
  - Create a text file in the same folder as the .py files. Name it orbnotifier.config with the following contents: `{"token": "[your Slack token]", "userid": "@[your user id]", "mac": "[your bulb's mac address]"}`    (i.e. `{"token": "xoxp-1111111111-2222222222-3333333333-ab123c", "userid": "@Abc1234d", "mac": "AA:BB:CC:DD:11:22"}`)

##Run:

  Just run: `python orbnotifier.py`
  
##Note:
  - If you don't create a config file first, it will create a stub file which you can then edit and fill in just the three parameters.
  - To stop the service just type in "quit" or "exit" (without quotes), then hit enter/return.
  - If for some reason it doesn't close down cleanly, gets an unhandled error or something, you may see zombie processes. You can scan for these: `ps -eLf`
  - and kill them by running: `sudo kill -9 [pid]`
