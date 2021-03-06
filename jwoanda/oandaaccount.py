import os
import logging
import smtplib
from email.mime.text import MIMEText
import threading
import yaml
from xdg import BaseDirectory

import v20

class OandaEnvironment(object):
    def __init__(self, environment='practice'):
        self.environment = environment
        self.readconf()
        
        self._apiurl = {'practice': "api-fxpractice.oanda.com",
                        'live'    : "api-fxtrade.oanda.com"}
        
        self._streamingapiurl = {'practice': "stream-fxpractice.oanda.com",
                                'live'    : "stream-fxtrade.oanda.com"}

        self._api = v20.Context(self._apiurl[self.environment],
                                token=self.apikey,
                                datetime_format='UNIX')


    def readconf(self):
        configpath = BaseDirectory.save_config_path('jwoanda')
        filename = os.path.join(configpath, 'config.yml')
        try:
            with open(filename) as f:
                d = yaml.load(f)
                try:
                    general = d.get('general')
                    self._datadir = os.path.expanduser(general.get('datadir'))
                except:
                    self._datadir = BaseDirectory.save_data_path("jwoanda")
                self._accounts = d.get('accounts')
                self._emailconf = d.get('email')
        except:
            raise Exception("Couldn't open/read account config file: %s" % filename)


    def info(self):
        logging.info("environment = %s", self.environment)
        logging.info("account_id  = %s", self.account_id)
        logging.info("apikey      = %s", self.apikey)


    def api(self):
        return self._api


    def streamingapi(self):
        return v20.Context(self._streamingapiurl[self.environment],
                           token=self.apikey,
                           datetime_format='UNIX')


    @property
    def account_id(self):
        return self._accounts.get(self.environment).get('accountid')


    @property
    def datadir(self):
        return self._datadir


    # @property
    # def environment(self):
    #     return self._environment


    # @environment.setter
    # def environment(self, value):
    #     if value not in ['practice', 'live']:
    #         raise ValueError("Wrong environment value")
    #     self._environment = value
    #     self._api = v20.Context(self._apiurl[self.environment],
    #                             token=self.apikey,
    #                             datetime_format='UNIX')


    def golive(self):
        self._environment = 'live'
        self._api = v20.Context(self._apiurl[self._environment],
                                token=self.apikey,
                                datetime_format='UNIX')

    def gopractice(self):
        self._environment = 'practice'
        self._api = v20.Context(self._apiurl[self._environment],
                                token=self.apikey,
                                datetime_format='UNIX')
        

    @property
    def apikey(self):
        return self._accounts.get(self.environment).get('apikey')


    def sendemail(self, subject, body):
        thread = threading.Thread(target=self._sendemail, args=(subject, body,))
        thread.start()


    def _sendemail(self, subject, body):
        fromm = self._emailconf.get('from')
        to = self._emailconf.get('to')
        server = self._emailconf.get('server')
        username = self._emailconf.get('username')
        password = self._emailconf.get('password')

        if fromm is None or to is None or server is None:
            logging.warning('email not sent due to missing configuration')
            return

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = fromm
        msg['To'] = to

        try:
            if server == 'localhost':
                s = smtplib.SMTP(server)
            else:
                s = smtplib.SMTP_SSL(server)
            if username is not None and password is not None:
                s.login(username, password)
            s.sendmail(fromm, [to], msg.as_string())
            s.quit()
            logging.debug('email sent')
        except:
            logging.error('email not sent due to error')


oandaenv = OandaEnvironment()
