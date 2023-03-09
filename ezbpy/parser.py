import re
import json
import xmltodict


def postprocess(data):
    if isinstance(data, str):
        return re.sub(r"\s+", " ", data)
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


class EzbPage:

    def __init__(self, xmlstr, clean=True):
        self.root_tag = "ezb_page"
        self.xmlstr = xmlstr
        try:
            self.data = xmltodict.parse(xmlstr)
            if clean:
                self.data = postprocess(self.data)
        except Exception:
            raise ValueError
        self.jsonstr = json.dumps(self.data, indent=2)

    def get(self, key, data=None):
        if data is None:
            data = self.data
        if isinstance(data, dict):
            if isinstance(key, str):
                if key in data and data[key]:
                    return data[key]
            if isinstance(key, list) and len(key) > 0 and key[0] in data:
                if len(key[1:]) == 1 and isinstance(key[1:][0], str):
                    return self.get(key[1:][0], data[key[0]])
                return self.get(key[1:], data[key[0]])

    def getroot(self):
        return self.get(self.root_tag)


class EzbChild(EzbPage):

    def __init__(self, xmlstr, tag, clean):
        super().__init__(xmlstr, clean=clean)
        self.tag = tag

    def main(self):
        return self.get([self.root_tag, self.tag])


class EzbDetailAboutJournal(EzbChild):

    def __init__(self, xmlstr, tag="ezb_detail_about_journal", clean=True):
        super().__init__(xmlstr, tag, clean)

    def field(self, key):
        main = self.main()
        return self.get(["journal", key], data=main)

    @property
    def title(self):
        return self.field("title")


class EzbSubjectList(EzbChild):

    def __init__(self, xmlstr, tag="ezb_subject_list", clean=True):
        super().__init__(xmlstr, tag, clean)

    def fields(self):
        main = self.main()
        return self.get("subject", data=main)
