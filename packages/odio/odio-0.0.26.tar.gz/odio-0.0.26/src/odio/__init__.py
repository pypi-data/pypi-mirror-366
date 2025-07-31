import xml.dom.minidom
import zipfile


class OdioException(Exception):
    pass


def parse_document(f):
    with zipfile.ZipFile(f, "r") as z:
        dom = xml.dom.minidom.parseString(z.read("META-INF/manifest.xml"))
        version = dom.documentElement.getAttribute("manifest:version")

        if version == "1.1":
            import odio.v1_1

            return odio.v1_1.parser.parse_node(dom)
        elif version == "1.2":
            import odio.v1_2

            return odio.v1_2.parse_document(z)
        elif version == "1.3":
            import odio.v1_3

            return odio.v1_3.parse_document(z)
        else:
            raise Exception(
                f"The version '{version}' isn't recognized. The valid version strings "
                f"are '1.1', '1.2' and '1.3'."
            )
