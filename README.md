# hotswatch - Watch for HOTS matches and trigger notification events

## Getting Started
1. install python 3.7

2. install requirements using `pip install -r requirements.txt`

3. rename `config.py.sample` to `config.py`. Edit in a text editor and change the settings to match your requirements

4. run the script using `python hotswatch.py`

5. launch HOTS. Events enabled within config.py will automatically trigger when entering a match

## How

HOTS creates a temporary `replay.server.battlelobby` file when entering a match. hotswatch watches for creation of / changes to this file, and triggers notification events as a result.

## FAQ

### What game modes are supported
* Quick Match, Versus AI, or any other game type which goes straight into match loading after matchmaking
* It is *not* suitable for modes which have a lobby prior to match loading (e.g. Hero/Team League)

### What notification types are supported
* Out of the box hotswatch supports the following notification types:
    * [Pushover](https://pushover.net) push notifications (e.g. iOS/Android),
    * audio clips via Sonos/Google Home
    * SMS notifications (via sinch.com)

* Additional notification types can be implemented by adding extra python code to `notifier.py`. Hotswatch will automatically instantiate and call the notify() method on all subclasses of the Notifier class defined within this file. 
```
class NotifyByMyDesiredMethod(Notifier):
     def notify(self):
       [Put your custom python code here]
```

### What Operating Systems are supported
* Windows only at the moment


## Todo

* TBD



