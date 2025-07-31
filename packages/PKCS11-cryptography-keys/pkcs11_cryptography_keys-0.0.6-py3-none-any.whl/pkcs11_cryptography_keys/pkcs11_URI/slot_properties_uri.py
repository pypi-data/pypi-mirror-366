from urllib.parse import quote

from ..utils.slot_properties import SlotProperties
from .definitions import CK_SLOT_INFO_translation, ParameterMatch


# slot properties
class SlotPropertiesURI(SlotProperties):
    def __init__(self, properties: dict, set_flags: list[str]) -> None:
        super().__init__(properties, set_flags)

    def check_uri_parameter(self, tag: str, value, logger) -> ParameterMatch:
        if tag in CK_SLOT_INFO_translation:
            ck_tag = CK_SLOT_INFO_translation[tag]
            if ck_tag in self._properties and value != self._properties[ck_tag]:
                logger.info(
                    "On token '{0}' did not match '{1}'".format(
                        value,
                        self._properties[ck_tag],
                    )
                )
                return ParameterMatch.FoundButWrongValue
            else:
                return ParameterMatch.Found
        else:
            return ParameterMatch.NotFound

    def gen_uri_tags(self):
        for tag in CK_SLOT_INFO_translation:
            ck_tag = CK_SLOT_INFO_translation[tag]
            val = quote(self._properties[ck_tag])
            yield tag, val
