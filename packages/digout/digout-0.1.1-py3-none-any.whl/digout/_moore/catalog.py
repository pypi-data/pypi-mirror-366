"""A Moore option file that allows to include an XML catalog file."""

if __name__ == "builtins":  # pragma: no cover
    from logging import getLogger
    from os import environ
    from pathlib import Path

    from Gaudi.Configuration import ApplicationMgr
    from Gaudi.Configuration import Gaudi__MultiFileCatalog as FileCatalog
    from Moore import options

    logger = getLogger(__name__)

    catalog_path = environ["DIGOUT_MOORE_XML_CATALOG"]

    if not Path(catalog_path).exists():
        msg = f"XML catalog file '{catalog_path}' does not exist."
        raise FileNotFoundError(msg)

    logger.debug("Using XML catalog file: %s", catalog_path)
    xml_file_name = "jobs/examples/xdigi2csv/pool_xml_catalog.xml"
    catalog = FileCatalog(Catalogs=[f"xmlcatalog_file:{xml_file_name}"])
    ApplicationMgr().ExtSvc.append(catalog)
    options.xml_file_catalog = catalog_path
