#!/usr/bin/env python3

from signalwire.relay.consumer import Consumer
import inspect
import time
import urllib.request
import sys
import time
import smtplib
import requests
import magic
import logging
import os
from base64 import encodebytes
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from tempfile import NamedTemporaryFile

EMAIL_ADDRESS=os.environ.get('EMAIL_ADDRESS')
API_PROJECT=os.environ.get('API_PROJECT')
API_TOKEN=os.environ.get('API_TOKEN')
PHONE_NUMBER=os.environ.get('PHONE_NUMBER')

def send_email(number, message, files=[]):
   msg=MIMEMultipart()
   msg['From']=f'Ghostbusters HQ <{EMAIL_ADDRESS}>'
   msg['Date']=formatdate(localtime=True)
   msg['Subject']='Incoming alert received'
   msg.attach(MIMEText('New alert received from '+number+'\n'+message))

   # attach files, if needed
   for file in files:
      fp=open(file, 'rb')
      part=MIMEBase('application', "octet-stream")
      part.set_payload(encodebytes(fp.read()).decode())
      fp.close()
      part.add_header('Content-Transfer-Encoding', 'base64')
      part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
      msg.attach(part)

   try:
      smtpObj=smtplib.SMTP('localhost')
      smtpObj.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
      logging.info("Successfully sent email")
   except SMTPException:
      logging.error("Error: unable to send email")
   return


class CustomConsumer(Consumer):
   def setup(self):
      self.project = API_PROJECT
      self.token = API_TOKEN
      self.contexts = ['home', 'office']

   def teardown(self):
      logging.info('Consumer teardown...')

   async def ready(self):
      logging.info('Connected and ready')

   async def on_incoming_message(self, message):
      logging.info('Incoming message from '+message.from_number+': '+ (message.body or ''))

      result=await self.client.messaging.send(context='home', to_number=message.from_number, from_number=PHONE_NUMBER, body='The Ghostbusters are on it!')
      if result.successful:
         logging.info(f'Message sent. ID: {result.message_id}')

      attachments=[]
      m=magic.open(magic.MAGIC_MIME)
      m.load()

      for url in message.media or []:
         tempfile=NamedTemporaryFile(delete=False)
         logging.info('Creating temp file: '+tempfile.name)
         urllib.request.urlretrieve(url, tempfile.name)

         if m.file(tempfile.name)=='image/jpeg':
            os.rename(tempfile.name, tempfile.name+'.jpg')
            tempfile.name=tempfile.name+'.jpg'
         elif m.file(tempfile.name)=='text/html':
            os.rename(tempfile.name, tempfile.name+'.html')
            tempfile.name=tempfile.name+'.html'

         attachments.append(tempfile.name)
      send_email(message.from_number, "Something funny going on?!\n"+(message.body or ''), attachments)

   async def on_incoming_call(self, call):
      result=await call.answer()
      if result.successful:
         logging.info('Incoming call from '+call.from_number+' received...')
         result=await call.prompt_tts(prompt_type='digits', text='Press 1 to report something funny going on, or press 2 to report a slimer sighting', digits_max=1)
         if result.successful:
            pin = result.result
            logging.info(f'Digits detected: {result.result}')

            if '1'==result.result:
               await call.play_tts(text="If something funny is going on, the Ghostbusters team will check it out!")
               send_email(call.from_number, "Voice report of something funny going on")
            elif '2'==result.result:
               await call.play_tts(text="Slimer sighting reported...expect a Ghostbusters team response shortly!")
               send_email(call.from_number, "Voice report of slimer sighting!")
            else:
               await call.play_tts(text="Sorry, didn't catch that")

         await call.hangup()

consumer = CustomConsumer()
consumer.run()
