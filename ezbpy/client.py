from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from . import __version__, parser, utils


class Ezb:

    def __init__(self, base_url, encoding="latin-1"):
        self.base_url = base_url
        self.encoding = encoding

    def fetch_url(self, url, lazy=True):
        try:
            req = Request(url, headers={"User-agent": "{0}.{1}/{2}".format(
                __name__, self.__class__.__name__, __version__)})
            with urlopen(req) as con:
                return con.read().decode(self.encoding)
        except HTTPError as err:
            self.logger.error("Got HTTP {0} while accessing URL {1}".format(
                err.code, url))
            if not lazy:
                raise
        except URLError as err:
            self.logger.error("Access to URL %s failed!" % url)
            self.logger.error(err.reason)
            if not lazy:
                raise


class CollectionsApi(Ezb):
    """
    https://ezb.ur.de/services/collections-api.phtml
    """

    def __init__(self):
        super().__init__("https://ezb-api.ur.de/collections/v1/")

    def fetch_list(self, parse=True, lazy=True):
        payload = self.fetch_url(self.base_url, lazy=lazy)
        return parser.EzbCollections(payload) \
            if parse else payload


class CollectionApi(Ezb):
    """
    https://ezb.ur.de/services/collections-api.phtml
    """

    def __init__(self):
        super().__init__("https://ezb.ur.de/api/collections")

    def url(self, collection_id):
        return "{0}/{1}".format(self.base_url, collection_id)

    def fetch(self, collection_id, lazy=True, parse=True):
        url = self.url(collection_id)
        payload = self.fetch_url(url, lazy=lazy)
        return parser.EzbCollection(payload) if parse else payload


class Ezeit(Ezb):
    """
    https://ezb.ur.de/services/xmloutput.phtml
    """

    def __init__(self, bibid="UBR", client_ip=None, colors=7, lang="de", log=0):
        super().__init__("https://ezb.ur.de/ezeit")
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

    def url_details(self, jourid, xmlv=None):
        url = "{0}/detail.phtml".format(self.base_url)
        url = self.add_shared_params(url)
        url = "{0}&jour_id={1}".format(url, jourid)
        url = self.add_param_xmloutput(url)
        if isinstance(xmlv, int):
            url = self.add_param_xmlv(url, xmlv)
        return url

    def fetch_details(self, jourid, xmlv=None, lazy=True, parse=True, clean=True):
        url = self.url_details(jourid, xmlv=xmlv)
        payload = self.fetch_url(url, lazy=lazy)
        return parser.EzbDetailAboutJournal(payload, clean=clean) \
            if parse else payload

    def url_subjects(self):
        url = "{0}/fl.phtml".format(self.base_url)
        url = self.add_shared_params(url)
        url = self.add_param_xmloutput(url)
        return url

    def fetch_subjects(self, lazy=True, parse=True, clean=True):
        url = self.url_subjects()
        payload = self.fetch_url(url, lazy=lazy)
        return parser.EzbSubjectList(payload, clean=clean) \
            if parse else payload
