# -*- coding: utf-8 -*-

import logging
import storj

from .utilities.account_manager import AccountManager


class StorjEngine:

    __logger = logging.getLogger('%s.StorjEngine' % __name__)

    def __init__(self):
        self.account_manager = AccountManager()
        self.password = None
        if self.account_manager.if_logged_in():
            self.password = self.account_manager.get_user_password()
            self.email = self.account_manager.get_user_email()

            # initialize Storj
            self.storj_client = storj.Client(
                email=self.email,
                password=self.password,
                do_hashing=False)
            self.__logger.debug('Login from credentials xml file')
        self.__logger.debug('testlogin, StorjEngine')
