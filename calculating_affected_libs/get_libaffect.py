from lib.database import get_postgres_connection
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime
postgres = get_postgres_connection()
POSTGRES_HOST = postgres.host
POSTGRES_PORT = postgres.port
POSTGRES_USER = postgres.user
POSTGRES_PWD = postgres.password
POSTGRES_DB = postgres.db
Base = automap_base()
# Create engine, session
engine = create_engine(
    "postgresql+psycopg2://"
    + POSTGRES_USER
    + ":"
    + POSTGRES_PWD
    + "@"
    + POSTGRES_HOST
    + ":"
    + POSTGRES_PORT
    + "/"
    + POSTGRES_DB,
    client_encoding="utf-8",
)
session = Session(engine)
# Reflect the tables
Base.prepare(engine, reflect=True)
# Mapped classes are now created with names by default
# matching that of the table name.
ScantistLibraryVersion = Base.classes.scantist_library_version
ScantistLibrary = Base.classes.scantist_library
ScantistLibraryVersionIssue = Base.classes.scantist_libraryversionissue
ScantistSecurityIssue = Base.classes.scantist_securityissue


def get_updated_vul_info(timestamp=datetime.datetime(2017, 7, 25), lib_only=False):
    """
    start from issues from a timestamp which is stored last time we did this update,
    get all related versions and their libname, vendor, version number
    """
    updated_vul_ver_info = (
        session.query(
            ScantistLibrary.name,
            ScantistLibrary.vendor,
            ScantistLibraryVersion.version_number,
            ScantistSecurityIssue.public_id,
            ScantistLibraryVersionIssue.is_valid,
        )
            .filter(
            ScantistLibraryVersionIssue.processed_time > timestamp,
            ScantistLibrary.platform == 'Go',
        )
            .join(
            ScantistLibraryVersion,
            ScantistLibrary.id == ScantistLibraryVersion.library_id,
        )
            .join(
            ScantistLibraryVersionIssue,
            ScantistLibraryVersion.id
            == ScantistLibraryVersionIssue.library_version_id,
        )
            .join(
            ScantistSecurityIssue,
            ScantistLibraryVersionIssue.security_issue_id
            == ScantistSecurityIssue.id,
        )
            .order_by(ScantistLibraryVersionIssue.processed_time.asc())
    )
    unique_vul_node = {}
    for update in updated_vul_ver_info:
        if (
                not f"{update[1]}-{update[0]}-{update[2]}-{update[3]}"
                    in unique_vul_node
        ):
            unique_vul_node[
                f"{update[1]}-{update[0]}-{update[2]}-{update[3]}"
            ] = update

    add_vul_rel = filter(lambda x: x[4] == True, list(unique_vul_node.values()))
    del_vul_rel = filter(lambda x: x[4] == False, list(unique_vul_node.values()))

    add_node = []
    del_node = {}

    for update in add_vul_rel:
        node = next((x for x in add_node if x["public_id"] == update[3]), None)
        if node:
            if update[1] + ":" + update[0] in node["affects"]:
                node["affects"][update[1] + ":" + update[0]].append(update[2])
            else:
                node["affects"][update[1] + ":" + update[0]] = [update[2]]
        else:
            add_node.append(
                {
                    "public_id": update[3],
                    "vulnerabilityId": update[3],
                    "affects": {update[1] + ":" + update[0]: [update[2]]},
                }
            )
    libaffects_list = []
    affect_list = []
    vulnerable_lib = []
    vul_node = add_node
    vul_node_list = []
    for vul in vul_node:
        for libvendor, vers in vul["affects"].items():
            for ver in vers:
                affect_list.append((vul['public_id'], libvendor.lstrip(':')+':'+ver))
        libaffects_list.append((vul['public_id'], libvendor.lstrip(':')))
        vulnerable_lib.append(libvendor.lstrip(':'))
        vul_node_list.append(vul['public_id'])
    vulnerable_lib = list(set(vulnerable_lib))
    libaffects_list = list(set(libaffects_list))
    affect_list = list(set(affect_list))
    vul_node_list =list(set(vul_node_list))
    if lib_only:
        return vulnerable_lib
    else:
        return libaffects_list, affect_list, vul_node_list

