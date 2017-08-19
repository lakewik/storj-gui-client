from utilities.account_manager import AccountManager
from utilities.backend_config import Configuration
import storj
from utilities.log_manager import logger


class StorjEngine:

    def __init__(self):
        self.conf_manager = Configuration()
        self.account_manager = AccountManager()
        self.password = None
        if self.account_manager.if_logged_in():
            self.password = self.account_manager.get_user_password()
            self.email = self.account_manager.get_user_email()
            # initialize Storj
            max_bridge_request_timeout = self.conf_manager.get_max_bridge_request_timeout()
            bridge_api_url = self.conf_manager.get_bridge_api_url()
            self.storj_client = storj.Client(email=self.email,
                                             password=self.password,
                                             do_hashing=False,
                                             timeout=max_bridge_request_timeout)
                                             #storj_bridge=bridge_api_url)
            logger.debug('Login from credentials xml file')
        logger.debug('testlogin, StorjEngine')
