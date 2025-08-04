#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from re import search
from typing import Any, List, Optional

import lxml.etree
import numpy

from eopf.common import date_utils, xml_utils
from eopf.exceptions import FormattingError

from .abstract import (
    EOAbstractListValuesFormatter,
    EOAbstractSingleValueFormatter,
    EOAbstractXMLFormatter,
)


class ToDatetime(EOAbstractXMLFormatter):
    """Formatter for the datetime attribute compliant with the stac standard"""

    # docstr-coverage: inherited
    name = "to_datetime"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> Optional[str]:
        """
        The datetime retrived from the product from XML search, the datetime STAC attribute
        should contain the middle time between the start_datetime and the end_datetime.

        Return the time formatted according to ISO with the UTC offset attached,
        giving a full format of 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'.
        The fractional part is omitted if self.microsecond == 0.
        """
        # map children content (text value) to tag names without namespace URIs
        children = {xml_utils.xml_local_name(elt): elt.text for elt in xpath_input}
        candidates = [
            ["startTime", "stopTime"],  # S01 & S03 tag
            ["PRODUCT_START_TIME", "PRODUCT_STOP_TIME"],  # S02 tag (Product_Info)
            ["DATASTRIP_SENSING_START", "DATASTRIP_SENSING_STOP"],  # S02 tag (Datastrip_Time_Info)
        ]
        for tag_start, tag_stop in candidates:
            if tag_start in children and tag_stop in children:
                start = children[tag_start]
                stop = children[tag_stop]
                if start is not None and stop is not None and len(start) > 1 and len(stop) > 1:
                    return date_utils.stac_iso8601(
                        date_utils.middle_date(date_utils.force_utc_iso8601(start), date_utils.force_utc_iso8601(stop)),
                    )
                else:
                    self._logger.warning("datetime: empty text, can not compute middle time")

        self._logger.warning("datetime: tag not found, can not compute middle time")
        return None


class ToBands(EOAbstractXMLFormatter):
    name = "to_bands"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> List[str]:
        bands_set = set()
        for element in xpath_input:
            band_id = str(element.attrib["bandId"])
            if len(band_id) == 1:
                bands_set.add(f"b0{band_id}")
            else:
                bands_set.add(f"b{band_id}")

        return sorted(bands_set)


class ToPosList(EOAbstractXMLFormatter):
    """Formatter for the pos list to a single str"""

    # docstr-coverage: inherited
    name = "to_pos_list"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> Optional[str]:
        """
        Use to filter the posList element to provide a specific formatting for them

        Parameters
        ----------
        xpath_input

        Returns

        """
        if not isinstance(xpath_input, list):
            raise TypeError("Only list accepted")
        if len(xpath_input) >= 1:
            if isinstance(xpath_input[0], lxml.etree._Element):
                if len(xpath_input) == 1:
                    if xpath_input[0].tag.endswith("posList") and xpath_input[0].text is not None:
                        values = xpath_input[0].text.split(" ")
                        match_list = ", ".join(
                            " ".join([values[idx + 1], values[idx]]) for idx in range(0, len(values) - 1, 2)
                        )
                        return f"POLYGON(({match_list}))"
                    if xpath_input[0].text is not None:
                        return xpath_input[0].text
                    else:
                        ret = ""
                        for val in xpath_input[0].values():
                            ret = ret + " " + str(val)
                        return ret[1:]
                else:
                    return ",".join([elt.text for elt in xpath_input])

            if isinstance(xpath_input[0], lxml.etree._ElementUnicodeResult):
                # When accessing xml attributes (with @), the object returned is a list with the attribute
                # as an ElementUnicodeResult. We retrieve it and cast it to str.
                return str(xpath_input[0])

        return None


class ToDetectors(EOAbstractXMLFormatter):
    name = "to_detectors"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> List[str]:
        detectors_set = set()
        for element in xpath_input:
            detector_id = str(element.attrib["detectorId"])
            if len(detector_id) == 1:
                detectors_set.add(f"d0{detector_id}")
            else:
                detectors_set.add(f"d{detector_id}")

        return sorted(detectors_set)


class ToMean(EOAbstractListValuesFormatter):
    name = "to_mean"

    def _format(self, xpath_input: List[str]) -> Any:
        return numpy.mean([float(element) for element in xpath_input])


class ToList(EOAbstractListValuesFormatter):
    name = "to_list"

    def _format(self, xpath_input: List[str]) -> Any:
        return [float(element) for element in xpath_input]


class ToListStr(EOAbstractListValuesFormatter):
    name = "to_list_str"

    def _format(self, xpath_input: List[str]) -> Any:
        return xpath_input


class ToListFloat(EOAbstractListValuesFormatter):
    name = "to_list_float"

    def _format(self, xpath_input: List[str]) -> Any:
        return [float(element) for element in xpath_input]


class ToListInt(EOAbstractListValuesFormatter):
    name = "to_list_int"

    def _format(self, xpath_input: List[str]) -> Any:
        return [int(element) for element in xpath_input]


class ToProcessingHistory(EOAbstractXMLFormatter):
    # docstr-coverage: inherited
    name = "to_processing_history"

    def get_attr(self, node: Any, path: str) -> Any:
        try:
            childs = node.xpath(path, namespaces=self.namespaces)
        except lxml.etree.XPathEvalError:
            childs = []
            self._logger.warning("The product history is probaly missing namespaces.")
        if len(childs) > 0:
            return str(childs[0])
        else:
            return None

    def transform(self, output: Any, output_role: Any, node: Any, accu: Any) -> str:
        if node is not None:
            processor = self.get_attr(node, f"{self.safe_namespace}:facility/{self.safe_namespace}:software/@name")
            version = self.get_attr(node, f"{self.safe_namespace}:facility/{self.safe_namespace}:software/@version")
            facility_name = self.get_attr(node, f"{self.safe_namespace}:facility/@name")
            facility_organisation = self.get_attr(node, f"{self.safe_namespace}:facility/@organisation")
            processing_time = self.get_attr(node, "@stop")
            inputs: Any = dict()
            try:
                childs = node.xpath(f"{self.safe_namespace}:resource", namespaces=self.namespaces)
            except lxml.etree.XPathEvalError:
                childs = []
                self._logger.warning("The product history is probaly missing namespaces.")
            for child in childs:
                role = self.get_attr(child, "@role")
                input = self.transform(
                    self.get_attr(child, "@name"),
                    self.get_attr(child, "@role"),
                    (
                        child.xpath(f"{self.safe_namespace}:processing", namespaces=self.namespaces)[0]
                        if len(child.xpath(f"{self.safe_namespace}:processing", namespaces=self.namespaces)) > 0
                        else None
                    ),
                    accu,
                )
                if input == "":
                    continue
                if role in inputs:
                    inputs[role + "1"] = inputs.pop(role)
                    inputs[role + "2"] = input
                elif role + "1" in inputs:
                    for i in range(3, 999):
                        if not role + str(i) in inputs:
                            inputs[role + str(i)] = input
                            break
                        if i > 997:
                            raise FormattingError("too many inputs with identical role " + role + " for " + output)
                else:
                    inputs[role] = input
            record = dict()
            record["type"] = output_role
            record["processor"] = processor
            if version:
                record["version"] = version
            if facility_name and facility_organisation:
                record["processingCentre"] = facility_name + ", " + facility_organisation
            if processing_time:
                record["processingTime"] = processing_time
            if len(inputs) > 0:
                record["inputs"] = inputs
            record["output"] = output
            accu.append(record)
        else:
            pass
        return output

    def _format(self, packed_data) -> Any:  # type: ignore
        """

        Parameters
        ----------
        input: Any
            input

        Returns
        ----------
        Any:
            Returns the input
        """
        xml_node, self.namespaces, product_name, url = packed_data

        # S1 namespaces differs from S2 and S4
        s1_rex = r"S1[ABCD]_.{2}_.{4}_(\d).{3}_.*"
        if search(s1_rex, url):
            self.safe_namespace = "safe"
        else:
            self.safe_namespace = "sentinel-safe"

        accu: List[Any] = list()

        # determine the product level based on the url of the product
        level = ""
        if url is not None:
            # Sentinels 1, 2, 3 regexes to retrieve the level
            sentinels_rex = [
                r"S1[ABCD]_.{2}_.{4}_(\d).{3}_.*",
                r"S2[ABCD]_MSI(\w{3})_.*",
                r"S3[ABCD]_\w{2}_(.)_.*",
            ]
            i = 0
            while level == "" and i < len(sentinels_rex):
                match = search(sentinels_rex[i], url)
                if match and match[1]:
                    if match[1][0] != "L":
                        level = "L" + match[1]
                    else:
                        level = match[1]
                else:
                    # in case of no match proceed to the following regex
                    i += 1

        self.transform(
            product_name,
            level,
            xml_node,
            accu,
        )
        return accu


class ToBoolInt(EOAbstractSingleValueFormatter):
    """Formatter for converting a string to an integer representation of bool"""

    # docstr-coverage: inherited
    name = "to_bool_int"

    def _format(self, xpath_input: str) -> int:
        return int("true" == xpath_input.lower())


class ToProcessingSoftware(EOAbstractXMLFormatter):
    """Formatter for extracting processing software from xml"""

    # docstr-coverage: inherited
    name = "to_processing_software"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> dict[str, str]:
        """retrieve the name and version of the xml node xpath_input"""
        try:
            dict_attrib = xpath_input[0].attrib
            return {str(dict_attrib["name"]): str(dict_attrib["version"])}
        except Exception as e:
            self._logger.debug(f"{self.name}: {e}")
            return {"": ""}


class ToSciDOI(EOAbstractListValuesFormatter):
    """Formatter for extracting product doi from xml"""

    # docstr-coverage: inherited
    name = "to_sci_doi"

    def _format(self, xpath_input: List[str]) -> str:
        # retrieve the right part of the DOI url
        try:
            if xpath_input and len(xpath_input) == 1:
                return xpath_input[0].replace("https://doi.org/", "")
        except Exception:
            self._logger.warning("Can not retrieve sci:doi", exc_info=True)
        return ""


class ToProductTimeliness(EOAbstractSingleValueFormatter):
    """Formatter for getting the timeliness for specific timeliness"""

    # docstr-coverage: inherited
    name = "to_product_timeliness"

    def _format(self, xpath_input: str) -> str:
        timeliness_category = xpath_input
        to_timeliness_map = {
            "NR": "PT3H",
            "NRT": "PT3H",
            "NRT-3h": "PT3H",
            "ST": "PT36H",
            "24H": "PT24H",
            "STC": "PT36H",
            "Fast-24h": "PT24H",
            "AL": "Null",
            "NT": "P1M",
            "NTC": "P1M",
        }
        if timeliness_category in to_timeliness_map:
            return to_timeliness_map[timeliness_category]
        else:
            return "Null"


class ToUTMZone(EOAbstractSingleValueFormatter):
    """Formatter for getting the utm zone"""

    # docstr-coverage: inherited
    name = "to_utm_zone"

    def _format(self, xpath_input: str) -> str:

        # read https://github.com/stac-extensions/product/blob/main/README.md
        # to be modified based on what is present in xml_accessors.py workaround of this accessor: TODO
        utm_zone = xpath_input.split("/")
        if len(utm_zone) < 2:
            raise FormattingError("No L1C UTM zone format found")
        return utm_zone[1].lstrip()


class ToSatOrbitState(EOAbstractListValuesFormatter):
    """Formatter for getting the correct orbit state"""

    # docstr-coverage: inherited
    name = "to_sat_orbit_state"

    def _format(self, xpath_input: List[str]) -> str:
        """There are cases when that xml data is with uppercase or
        it has several xml data attributes about ascending, descending, etc"""
        # the data might come in uppercase | has usage for S1 products
        if xpath_input and len(xpath_input) == 1:
            return xpath_input[0].lower()
        return "No data about orbit state"


class ToProviders(EOAbstractSingleValueFormatter):
    """Formatter for respecting providers stac standard"""

    # docstr-coverage: inherited
    name = "to_providers"

    def _format(self, xpath_input: str) -> Any:
        """Function that returns the input without formatting"""
        return xpath_input


class ToPlatform(EOAbstractSingleValueFormatter):
    """Formatter for the platform attribute compliant with the stac standard"""

    # docstr-coverage: inherited
    name = "to_platform"

    def _format(self, xpath_input: str) -> Any:
        """The platform's name retrived from the resulted list from XML search"""
        if isinstance(xpath_input, str) and xpath_input is not None:
            return str(xpath_input).lower()
        else:
            raise FormattingError("No data about stac_discovery/properties/platform")


class ToSarPolarizations(EOAbstractListValuesFormatter):
    """Formatter for sar:polarizations attribute"""

    # docstr-coverage: inherited
    name = "to_sar_polarizations"

    def _format(self, xpath_input: List[str]) -> Any:
        """The input parameter from this function should be a list with all polarizations"""
        if isinstance(xpath_input, list):
            return xpath_input
        else:
            raise FormattingError("The xml path for sar:polarizations is wrong or it doesn't exist!")
