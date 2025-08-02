import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from iugu.api import IuguApi

class Invoices:
    def __init__(self):
        self.api = IuguApi()
        self.endpoint_url = UrlUtil().make_url(self.base_url, ['v1', 'invoices'])
    
    def get_by_id(self, id):
        logging.info(f'get invoice info by id: {id}...')
        endpoint_url = UrlUtil().make_url(self.endpoint_url, [id])
        response = self.request(HTTPMethod.GET, endpoint_url)
        return jsonpickle.decode(response)