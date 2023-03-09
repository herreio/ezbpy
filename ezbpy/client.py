# import xmltodict
from urllib.request import urlopen

from . import parser, utils

# BASE_URL = "https://ezb.ur.de/ezeit"


# def param_lang(lang):
#     if lang not in ["de", "en"]:
#         raise Exception()
#     return lang


# def url_details(jourid, bibid="UBR", client_ip=None, colors=7, lang="de"):
#     url = "{0}/detail.phtml".format(BASE_URL)
#     if isinstance(bibid, str):
#         url = "{0}?bibid={1}".format(url, bibid)
#     elif isinstance(client_ip, str):
#         url = "{0}?client_ip={1}".format(url, client_ip)
#     else:
#         raise Exception()
#     url = "{0}&colors={1}&jour_id={2}&xmloutput=1".format(url, colors, jourid)
#     return url


# def fetch_details(ezb_id, bibid="UBR", client_ip=None, colors=7, lang="de"):
#     url = url_details(ezb_id, bibid=bibid, client_ip=client_ip, colors=colors,
#                       lang=lang)
#     try:
#         with urlopen(url) as con:
#             return con.read().decode("latin-1")
#     except Exception:
#         pass


# def json_details(ezb_id, bibid="UBR", client_ip=None, colors=7, lang="de"):
#     response = fetch_details(ezb_id, bibid=bibid, client_ip=client_ip,
#                              colors=colors, lang=lang)
#     try:
#         return xmltodict.parse(response)
#     except Exception:
#         pass


class Ezeit:

    def __init__(self, bibid="UBR", client_ip=None, colors=7, lang="de", log=0):
        self.base_url = "https://ezb.ur.de/ezeit"
        if isinstance(bibid, str):
            self.bibid = bibid
            self.client_ip = None
        elif isinstance(client_ip, str):
            self.bibid = None
            self.client_ip = client_ip
        else:
            raise ValueError()
        self.client_ip = client_ip
        self.colors = colors
        if lang not in ["de", "en"]:
            raise ValueError()
        self.lang = lang
        self.encoding = "latin-1"
        self.logger = utils.get_logger("{0}.{1}".format(
            self.__module__, self.__class__.__name__))

    def add_param_bibid_or_client_ip(self, url):
        if self.bibid is not None:
            return "{0}?bibid={1}".format(url, self.bibid)
        elif self.client_ip is not None:
            return "{0}?client_ip={1}".format(url, self.client_ip)
        else:
            raise ValueError

    def add_param_colors(self, url):
        return "{0}&colors={1}".format(url, str(self.colors))

    def add_param_lang(self, url):
        return "{0}&lang={1}".format(url, self.lang)

    def add_shared_params(self, url):
        url = self.add_param_bibid_or_client_ip(url)
        url = self.add_param_colors(url)
        url = self.add_param_lang(url)
        return url

    @staticmethod
    def add_param_xmloutput(url):
        return "{0}&xmloutput=1".format(url)

    @staticmethod
    def add_param_xmlv(url, xmlv):
        return "{0}&xmlv={1}".format(url, xmlv)

    def fetch_url(self, url):
        try:
            with urlopen(url) as con:
                return con.read().decode(self.encoding)
        except Exception as e:
            self.logger.error(e.__class__.__name__)
            # raise
            # pass
            # print("fetch_url: Exception")

    def url_details(self, jourid, xmlv=None):
        url = "{0}/detail.phtml".format(self.base_url)
        url = self.add_shared_params(url)
        url = "{0}&jour_id={1}".format(url, jourid)
        url = self.add_param_xmloutput(url)
        if isinstance(xmlv, int):
            url = self.add_param_xmlv(url, xmlv)
        # print(url)
        return url

    # def parse_xml(self, xmlstr):
    #     try:
    #         return xmltodict.parse(xmlstr)
    #     except Exception:
    #         pass

    def fetch_details(self, jourid, xmlv=None, parse=True, clean=True):
        url = self.url_details(jourid, xmlv=xmlv)
        payload = self.fetch_url(url)
        return parser.EzbDetailAboutJournal(payload, clean=clean) \
            if parse else payload

    def url_subjects(self):
        url = "{0}/fl.phtml".format(self.base_url)
        url = self.add_shared_params(url)
        url = self.add_param_xmloutput(url)
        return url

    def fetch_subjects(self, parse=True, clean=True):
        url = self.url_subjects()
        payload = self.fetch_url(url)
        return parser.EzbSubjectList(payload, clean=clean) \
            if parse else payload
