"""
pyPreservicaFSDate module definition

A python module for adding dates from a file system onto Preservica assets

author:     James Carr
licence:    Apache License 2.0

"""

import argparse
import datetime
import os.path
import pathlib

from pyPreservica import *

FILE_DATES_SCHEMA_NS = "http://www.preservica.com/metadata/group/file_system_dates"

xml_document = """
<file_system_dates xmlns="http://www.preservica.com/metadata/group/file_system_dates" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <created_date>$C$</created_date>
                <modified_date>$M$</modified_date>
                <accessed_date>$A$</accessed_date>
</file_system_dates>
"""

PROG_HELP = """
Add file system dates to Preservica assets.
Search local file system for matching files and add the file system dates to Preservica.
Files are either matched on Asset title and filename or by fixity which is slower.

You provide both a Preservica collection UUID and a local file system folder to look for matches
"""



class FileHash:
    """
    A wrapper around the hashlib hash algorithms that allows an entire file to
    be hashed in a chunked manner.
    """

    def __init__(self, algorithm):
        self.algorithm = algorithm

    def get_algorithm(self):
        return self.algorithm

    def __call__(self, file):
        hash_algorithm = self.algorithm()
        with open(file, 'rb') as f:
            buf = f.read(HASH_BLOCK_SIZE)
            while len(buf) > 0:
                hash_algorithm.update(buf)
                buf = f.read(HASH_BLOCK_SIZE)
        return hash_algorithm.hexdigest()

def group_metadata(metadata: MetadataGroupsAPI):
    """
    Add a NewGen Metadata Group into the tenancy if
    it does not already exist

    This will hold the date metadata

    :param metadata: MetadataGroupsAPI client
    :return:
    """
    # does Twitter metadata group already exist
    for group in metadata.groups():
        if group.schemaUri == FILE_DATES_SCHEMA_NS:
            return

    fields = [GroupField(field_id="created_date", name="Created Date", field_type=GroupFieldType.DATE, visible=True,
                         indexed=True, editable=True, minOccurs=1, maxOccurs=1),
                GroupField(field_id="modified_date", name="Modified Date", field_type=GroupFieldType.DATE, visible=True,
                         indexed=True, editable=True, minOccurs=1, maxOccurs=1),
                GroupField(field_id="accessed_date", name="Accessed Date", field_type=GroupFieldType.DATE, visible=True,
                         indexed=True, editable=True, minOccurs=1, maxOccurs=1)]

    metadata.add_group(group_name="File System Dates", group_description="File System Dates", fields=fields)


def fixity(asset: Asset, entity: EntityAPI):
    """
    Find the fixity value and algorithm from the Preservica Asset
    """
    for bs in entity.bitstreams_for_asset(asset):
        for f in bs.fixity:
            return f, bs.fixity[f]
    return None


def add_dates(asset: Asset, entity: EntityAPI, full_path):
    """
    Add the dates into Preservica
    """
    stat = os.lstat(full_path)
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).date()
    ctime = datetime.datetime.fromtimestamp(stat.st_ctime).date()
    atime = datetime.datetime.fromtimestamp(stat.st_atime).date()
    xml_doc = xml_document.replace("$M$", str(mtime)).replace("$C$", str(ctime)).replace("$A$", str(atime))
    entity.add_metadata_as_fragment(asset, FILE_DATES_SCHEMA_NS, xml_doc)



def main():
    """

    For each asset in a collection search a local file system folder for the file
    and if found add the filesystem dates into Preservica.

    :return:
    """

    cmd_parser = argparse.ArgumentParser(
        prog='pyPreservicaFSDate',
        description=PROG_HELP,
        epilog='')

    cmd_parser.add_argument("-c", "--collection", type=str, help="The Preservica parent collection uuid",
                            required=False)

    cmd_parser.add_argument("-p", "--path", type=pathlib.Path, help="The file system path to search",
                           required=False)

    cmd_parser.add_argument("-f", "--fixity",  action='store_const', const=True, help="Use fixity matching (slow)",
                            required=False)

    args = cmd_parser.parse_args()
    cmd_line = vars(args)

    groups: MetadataGroupsAPI = MetadataGroupsAPI()
    entity: EntityAPI = EntityAPI()

    group_metadata(groups)

    collection = cmd_line['collection']
    if collection is None:
        folder = None
        print(f"WARNING: No collection specified, all Preservica collections will be checked")
    else:
        folder = entity.folder(collection)

    fs_path = cmd_line['path']
    if fs_path is None:
        norm_path = os.getcwd()
        print(f"WARNING: No local folder specified, the local folder {norm_path} will be checked")
    else:
        if not os.path.isdir(fs_path):
            print(f"The specified path does not exist: {fs_path}")
            exit(1)
        norm_path = os.path.normpath(fs_path)

    use_fixity: bool = cmd_line['fixity']

    fixity_hash = dict()

    print(f"Searching for files within: {norm_path}")

    if use_fixity:
        print(f"Using fixity to match Assets to files")
        fixity_hash["MD5"] = FileHash(hashlib.md5)
        fixity_hash["SHA1"] = FileHash(hashlib.sha1)
        fixity_hash["SHA256"] = FileHash(hashlib.sha256)
        fixity_hash["SHA512"] = FileHash(hashlib.sha512)
        for a in filter(only_assets, entity.all_descendants(folder)):
            print(f'Searching the filesystem for asset: {a.title}\r', end="")
            asset = entity.asset(a.reference)
            if FILE_DATES_SCHEMA_NS not in asset.metadata_namespaces():
                algorithm, fixity_value = fixity(a, entity)
                for root, dirs, files in os.walk(norm_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        file_fixity = fixity_hash[algorithm](full_path)
                        if str(fixity_value).lower() == str(file_fixity).lower():
                            print(f"Found matching file with same fixity {file}, adding dates...")
                            add_dates(asset, entity, full_path)
            else:
                print(f"Asset {asset.title} has existing file system dates, skipping...")


    if use_fixity is None:
        for a in filter(only_assets, entity.all_descendants(folder)):
            print(f'Searching the filesystem for asset: {a.title}\r', end="")
            asset = entity.asset(a.reference)
            if FILE_DATES_SCHEMA_NS not in asset.metadata_namespaces():
                for root, dirs, files in os.walk(norm_path):
                    for file in files:
                        if Path(str(os.path.basename(file))).stem == asset.title:
                            print(f"Found matching file with name {file}, adding dates...")
                            full_path = os.path.join(root, file)
                            add_dates(asset, entity, full_path)
            else:
                print(f"Asset {asset.title} has existing file system dates, skipping...")



if __name__ == '__main__':
    sys.exit(main())


