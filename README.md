Signalwire 2021 Community Code Off

This is an incredibly quick-n-dirty entry.

How it works:

The code uses the Signalwire Python Relay API. It listens for incoming
voice calls and text messages.

If a voice call is received, the call is answered, some minor details
about the call are logged, and prompt_tts() is used to play the
instructions and wait for a DTMF digit (either '1' or '2') to be
pressed. The digit pressed is then logged, and if the digit represented
a valid choice play_tts() is used to acknowledge the choice and an email
is sent to Ghostbusters HQ. (If an invalid response is received no email
is sent.) The call is then terminated.

If a text message is received, some details about the message are logged and
a reply is sent to the incoming phone number. The message payload is then examined
for any media files, just in case a photo or video was sent. The media files
are downloaded to temporary files, renamed if they're detected as jpeg or html files,
then attached to an email sent to Ghostbusters HQ.

Signalwire technology used: the Relay SDK for Python.

External dependencies used: a few Python modules (urllib, smtplib,
magic, email, etc.) and it expects there's a local SMTP server available to send email.

The code imports EMAIL_ADDRESS, PHONE_NUMBER, API_PROJECT, API_TOKEN
from the environment.
