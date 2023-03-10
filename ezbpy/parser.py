import re
import html
import json
import xmltodict


def postprocess(data):
    if isinstance(data, str):
        return re.sub(r"\s+", " ", data).strip()
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], str):
                data[k] = re.sub(r"\s+", " ", data[k])
            if isinstance(data[k], dict):
                data[k] = postprocess(data[k])
            if isinstance(data[k], list):
                for element in data[k]:
                    element = postprocess(element)
    if isinstance(data, list):
        for element in data:
            element = postprocess(element)
    return data


class EzbData:

    def __init__(self):
        pass

    def get(self, key, data=None):
        if data is None and hasattr(self, "data"):
            data = self.data
        if isinstance(data, dict):
            if isinstance(key, str):
                if key in data and data[key]:
                    return data[key]
            if isinstance(key, list) and len(key) > 0 and key[0] in data:
                if len(key[1:]) == 1 and isinstance(key[1:][0], str):
                    return self.get(key[1:][0], data[key[0]])
                return self.get(key[1:], data[key[0]])


class EzbXml(EzbData):

    def __init__(self, xmlstr, tag, clean):
        super().__init__()
        self.root_tag = "ezb_page"
        self.xmlstr = xmlstr
        try:
            self.data = xmltodict.parse(xmlstr)
            if clean:
                self.data = postprocess(self.data)
        except Exception:
            raise ValueError
        self.jsonstr = json.dumps(self.data, indent=2)
        self.tag = tag
        self.page_name = self.get([self.root_tag, "page_name"])
        self.page_vars = self.get([self.root_tag, "page_vars"])
        self.library = self.get([self.root_tag, "library"])
        self.header = {
            "bibid": self.get("@bibid", data=self.library),
            "colors": self.get([self.root_tag, "@colors"]),
            "lang": self.get([self.root_tag, "@lang"])
            }

    def getroot(self):
        return self.get(self.root_tag)

    def main(self):
        return self.get([self.root_tag, self.tag])


class EzbDetailAboutJournal(EzbXml):

    def __init__(self, xmlstr, tag="ezb_detail_about_journal", clean=True):
        super().__init__(xmlstr, tag, clean)

    def field(self, key):
        main = self.main()
        return self.get(["journal", key], data=main)

    @property
    def title(self):
        return self.field("title")


class EzbSubjectList(EzbXml):

    def __init__(self, xmlstr, tag="ezb_subject_list", clean=True):
        super().__init__(xmlstr, tag, clean)

    def fields(self):
        main = self.main()
        return self.get("subject", data=main)


class EzbJson(EzbData):

    def __init__(self, jsonstr):
        super().__init__()
        self.raw = jsonstr
        self.data = json.loads(self.raw)
        self.jsonstr = json.dumps(self.data, indent=2)


class EzbCollection(EzbJson):

    def __init__(self, jsonstr):
        super().__init__(jsonstr)

    def parse(self, field, data=None):
        value = self.get(field, data=data)
        return html.unescape(value.strip())


class EzbCollections(EzbJson):

    def __init__(self, jsonstr):
        super().__init__(jsonstr)
        self.root_element = "collections"
        self.flat_list = []
        if isinstance(self.data, dict):
            collections = self.get(self.root_element)
            for colltype in collections:
                for collection in collections[colltype]:
                    if collection not in self.flat_list:
                        self.flat_list.append(collection)
            self.flat_list_parsed = self._parse_collections()

    def _parse_collections(self):
        flat_list_parsed = []
        for coll in self.flat_list:
            jsonstr = json.dumps(coll)
            flat_list_parsed.append(EzbCollectionsCollection(jsonstr))
        if len(flat_list_parsed) > 0:
            return flat_list_parsed

    def main(self):
        return self.get(self.root_element)

    def get_collection_types(self):
        main = self.main()
        if isinstance(main, dict):
            colltypes = list(set(main.keys()))
            colltypes.sort()
            return colltypes

    def get_collections_via_type(self, type_name):
        return self.get([self.root_element, type_name])

    def find_value_via_field(self, key, field_key, field_value):
        values = [c[key] for c in self.flat_list
                  if key in c and field_key in c
                  and c[field_key] == field_value]
        if len(values) > 0:
            values.sort()
            return values

    def find_collections_via_field(self, field_key, field_value):
        return self.find_value_via_field("ezb_collection_id", field_key, field_value)

    def find_collections_via_package_id(self, package_id):
        return self.find_collections_via_field("ezb_package_id", package_id)

    def find_collections_via_collection_anchor(self, coll_anchor):
        return self.find_collections_via_field("ezb_collection_anchor", coll_anchor)

    def find_products_via_field(self, field_key, field_value):
        return self.find_value_via_field("zdb_product_id", field_key, field_value)

    def find_products_via_package_id(self, package_id):
        return self.find_products_via_field("ezb_package_id", package_id)

    def find_products_via_collection_anchor(self, coll_anchor):
        return self.find_products_via_field("ezb_collection_anchor", coll_anchor)


class EzbCollectionsCollection(EzbJson):

    def __init__(self, jsonstr):
        super().__init__(jsonstr)

    @property
    def ezb_collection_id(self):
        return self.get("ezb_collection_id")

    @property
    def ezb_collection_name(self):
        return self.get("ezb_collection_name")
