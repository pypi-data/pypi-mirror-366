import logging
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESearchResult:

    def __init__(self, count: int, ret_max: int, ret_start: int,
                 id_list: list,
                 query_translation,
                 translation_stack,
                 translation_set):
        self.count = count
        self.ret_max = ret_max
        self.ret_start = ret_start
        self.id_list = id_list
        self.query_translation = query_translation
        self.translation_set = translation_set
        self.translation_stack = translation_stack

    @staticmethod
    def from_xml(xml_data):
        tree = ET.fromstring(xml_data)

        id_list = None
        ret_max = None
        ret_start = None
        count = None
        query_translation = None
        translation_set = None
        translation_stack = None

        for o in tree:
            if o.tag == "IdList":
                id_list = [i.text for i in o]
            elif o.tag == "Count":
                count = int(o.text)
            elif o.tag == "RetStart":
                ret_start = int(o.text)
            elif o.tag == "RetMax":
                ret_max = int(o.text)
            elif o.tag == "QueryTranslation":
                query_translation = o.text
            elif o.tag == "TranslationSet":
                translation_set = o.text
            elif o.tag == "TranslationStack":
                translation_stack = o.text
            else:
                logger.warning(f'Ignored tag: {o.tag}: {o.text}')

        return ESearchResult(count, ret_max, ret_start,
                             id_list,
                             query_translation,
                             translation_stack,
                             translation_set)
