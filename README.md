# Slack OrbNotifier
Bluetooth RGB LED bulb integrated with Slack so that it notifies (blinks) on mentions of your user id (@username), @channel, or private message. You can find a full write-up of the project here: http://alansellers.net/projects/slack-orb-notifier/

##Configuration:
  - Requst an API key/token from Slack: https://api.slack.com/web
  - Test out your token with the rtm.start API call: https://api.slack.com/methods/rtm.start/test
  - Find your Colorific Bulb's MAC address: `sudo hcitool lescan`
  - Create a text file in the same folder as the .py files. Name it orbnotifier.config with the following contents: `{"token": "[your Slack token]", "mac": "[your bulb's mac address]"}`    (i.e. `{"token": "xoxp-1111111111-2222222222-3333333333-ab123c", "mac": "AA:BB:CC:DD:11:22"}`)

##Run:

  Just run: `python orbnotifier.py`
  
##Note:
  - If you don't create a config file first, it will create a stub file which you can then edit and fill in just the three parameters.
  - To stop the service just type in "quit" or "exit" (without quotes), then hit enter/return.
  - If for some reason it doesn't close down cleanly, gets an unhandled error or something, you may see zombie processes. You can scan for these: `ps -eLf`
  - and kill them by running: `sudo kill -9 [pid]`
