import psycopg2
import json
from psycopg2.extras import Json

from lib.database import get_postgres_connection
postgres = get_postgres_connection()
DB_NAME = postgres.db
DB_HOST = postgres.host
DB_PORT = int(postgres.port)
DB_USER = postgres.user
DB_PWD = postgres.password

# DB_NAME = postgres.db
# DB_HOST = 'localhost'#postgres.host
# DB_PORT = int(postgres.port)
# DB_USER = 'cvetriage'
# DB_PWD = 'postgres'
conn = psycopg2.connect(dbname=DB_NAME,
                            user=DB_USER,
                            password=DB_PWD,
                            host=DB_HOST,
                            port=DB_PORT)

def get_conn():
    return psycopg2.connect(dbname=DB_NAME,
                            user='secbug',
                            password='fgyu7RE0',
                            host=DB_HOST,
                            port=DB_PORT)

#conn = get_conn()
#
conn = psycopg2.connect(dbname=DB_NAME,
                            user=DB_USER,
                            password=DB_PWD,
                            host=DB_HOST,
                            port=DB_PORT)
def insert_p5_libraries(libraries):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """INSERT INTO p5_scantist_library 
                (created, modified, is_valid, processed_time, name, description, vendor, language, platform, source, process_status)
                VALUES (%(created)s, %(modified)s, %(is_valid)s, 
                %(processed_time)s, %(name)s, %(description)s, %(vendor)s, %(language)s, %(platform)s, %(source)s, %(process_status)s);
            """

    cur.executemany(sql_str, tuple(libraries))

def get_id_p5_lib(name):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """SELECT id FROM p5_scantist_library WHERE name = %s;"""

    cur.execute(sql_str, (name,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None


def get_id_lib(name):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """SELECT id FROM scantist_library WHERE name = %s;"""

    cur.execute(sql_str, (name,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None

def get_go_names_and_localpath(last_timestamp):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """SELECT sl.name, sr.local_path FROM public."2_scantist_repolist" as sr 
            inner join public."2_scantist_libraryrepourl" as slr on slr.repolist_id = sr.id
            inner join public.scantist_library as sl on sl.id = slr.library_id
            where sl.platform = 'Go' and sl.created >= '%s';""" % last_timestamp
        cur.execute(sql_str)
        return dict(cur.fetchall())


def get_repolist(name):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """SELECT id FROM "2_scantist_repolist" WHERE name = %s;"""

    cur.execute(sql_str, (name,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None

def get_repourl(library_id, repolist_id):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """SELECT id FROM "2_scantist_libraryrepourl" WHERE library_id = %s and repolist_id = %s;"""

    cur.execute(sql_str, (library_id, repolist_id,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None



def insert_repolist(repo):
    conn.autocommit = True
    cur = conn.cursor()
    sql_str = """INSERT INTO "2_scantist_repolist" 
                    (created, modified, name, repo_url, homepage_url, branch, scm_type, sync_status, sync_time, platform, local_path, process_status, process_time, db_import_status, db_import_time, type, language_id, taglist, feature_tags)
                    VALUES (%(created)s, %(modified)s, %(name)s, 
                    %(repo_url)s, %(homepage_url)s, %(branch)s, %(scm_type)s, %(sync_status)s, %(sync_time)s, %(platform)s, %(local_path)s, %(process_status)s, %(process_time)s, %(db_import_status)s, %(db_import_time)s, %(type)s, %(language_id)s, %(taglist)s, %(feature_tags)s) RETURNING id;
                """

    cur.execute(sql_str, repo)
    return cur.fetchone()[0]


def insert_repourl(repourl):
    conn.autocommit = True
    cur = conn.cursor()
    sql_str = """INSERT INTO "2_scantist_libraryrepourl" 
                    (created, modified, is_valid, library_id, repolist_id)
                    VALUES (%(created)s, %(modified)s, %(is_valid)s, 
                    %(library_id)s, %(repolist_id)s) RETURNING id;
                """

    cur.execute(sql_str, repourl)
    return cur.fetchone()[0]

def get_vers(libraryid, vername):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """SELECT id FROM p5_scantist_library_version WHERE library_id = %s and version_number = %s;"""

    cur.execute(sql_str, (libraryid, vername,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None



def insert_p5_library_version(versions):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """INSERT INTO p5_scantist_library_version 
                (created, modified, is_valid, processed_time, version_number, release_date, is_active, is_officially_supported, is_clean, source, library_id, process_status)
                VALUES (%(created)s, %(modified)s, %(is_valid)s, 
                %(processed_time)s, %(version_number)s, %(release_date)s, %(is_active)s, %(is_officially_supported)s, %(is_clean)s, %(source)s, %(library_id)s, %(process_status)s) RETURNING id;
            """

    cur.executemany(sql_str, tuple(versions))

def insert_p5_library_license(licenses):
    conn.autocommit = True
    cur = conn.cursor()

    sql_str = """INSERT INTO p5_scantist_library_license 
                (created, modified, is_valid, processed_time, library_id, license_id, affected_versions, process_status)
                VALUES (%(created)s, %(modified)s, %(is_valid)s, 
                %(processed_time)s, %(library_id)s, %(license_id)s, %(affected_versions)s, %(process_status)s) RETURNING id;
            """

    cur.executemany(sql_str, tuple(licenses))


def get_lib_ids():
    conn.autocommit = True
    cur = conn.cursor()
    query_str = """SELECT name, id FROM p5_scantist_library where platform = 'Go';"""
    cur.execute(query_str)
    lib_ids = dict(cur.fetchall())
    return lib_ids

def get_affected_libs():
    conn.autocommit = True
    cur = conn.cursor()
    query_str = """SELECT sl.name, ssi.public_id FROM public.scantist_securityissue as ssi 
inner join public.scantist_libraryversionissue as slvi on slvi.security_issue_id = ssi.id 
inner join public.scantist_library_version as slv on slvi.library_version_id = slv.id 
inner join public.scantist_library as sl on sl.id = slv.library_id 
where sl.platform = 'Go';"""
    cur.execute(query_str)
    return cur.fetchall()

def get_all_repourl():
    conn.autocommit = True
    cur = conn.cursor()
    query_str = """SELECT repo_url FROM "2_scantist_repolist";"""
    cur.execute(query_str)
    repolist = list(x[0] for x in cur.fetchall())
    return repolist

def get_licenses():
    conn_l = get_conn()
    conn_l.autocommit = True
    cur = conn_l.cursor()
    query_str = """SELECT identifier, id FROM scantist_license where is_valid = true;"""
    cur.execute(query_str)
    lic_dict = dict(cur.fetchall())
    return lic_dict

def get_ver_ids():
    conn.autocommit = True
    cur = conn.cursor()
    query_str = """SELECT slv.id, slv.version_number, sl.name FROM public.p5_scantist_library_version as slv 
join public.p5_scantist_library as sl on sl.id = slv.library_id where sl.platform = 'Go';"""
    cur.execute(query_str)
    ver_ids = {}
    for item in cur.fetchall():
        ver_ids[item[2] + ':' + item[1]] = item[0]
    return ver_ids


def update_repo_location(repolist_id, location):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """UPDATE "2_scantist_repolist" SET local_path = %s WHERE id = %s;"""

        cur.execute(sql_str, (location, repolist_id,))


def update_commit_processed_time(commit_id, time_now):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """UPDATE triage_commit SET processed_time = %s WHERE id = %s;"""

        cur.execute(sql_str, (time_now, commit_id,))


def insert_securityissue(security_issue):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """INSERT INTO scantist_securityissue 
            (created, modified, score, description, public_id, vulnerable_software_versions, language, is_valid)
            VALUES (%(created)s, %(modified)s, %(score)s, 
            %(description)s, %(public_id)s, %(vulnerable_software_versions)s, %(language)s, %(is_valid)s) RETURNING id;
        """

        cur.execute(sql_str, security_issue)
        return cur.fetchone()[0]


def insert_securityissue_group(securityissue_group):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """INSERT INTO scantist_securityissue 
                    (created, modified, score, description, public_id, vulnerable_software_versions, language, is_valid)
                    VALUES (%(created)s, %(modified)s, %(score)s, 
                    %(description)s, %(public_id)s, %(vulnerable_software_versions)s, %(language)s, %(is_valid)s) RETURNING id;
                """

        cur.executemany(sql_str, tuple(securityissue_group))


def insert_securitbug_group(securitybug_group):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """INSERT INTO scantist_securitybug 
                    (securityissue_ptr_id, vector)
                    VALUES (%(securityissue_ptr_id)s, %(vector)s) RETURNING securityissue_ptr_id;
                """

        cur.executemany(sql_str, tuple(securitybug_group))


def get_securityissue_by_public_id(public_id):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """SELECT id FROM scantist_securityissue WHERE public_id = %s;"""

        cur.execute(sql_str, (public_id,))
        return cur.fetchone(), cur.rowcount


def update_securityissue_description(public_id_and_description):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """UPDATE scantist_securityissue SET description = %(description)s WHERE public_id = %(public_id)s;"""

        cur.executemany(sql_str, tuple(public_id_and_description))


def get_commit_id_and_public_id():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """SELECT commitid, public_id FROM triage_commit;"""

        cur.execute(sql_str)
        return cur.fetchall()


def get_securityissue_publicid_issueid():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """SELECT public_id, id FROM scantist_securityissue;"""

        cur.execute(sql_str)
        return cur.fetchall(), cur.rowcount


def update_public_id_of_commits(commits_to_update):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """UPDATE triage_commit SET public_id = %(public_id)s WHERE id = %(id)s;"""

        cur.executemany(sql_str, tuple(commits_to_update))


# def get_latest_sec_bug_seq_of_year(current_year):
#     with get_conn() as conn:
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         sql_str = """SELECT public_id FROM scantist_securityissue
#         WHERE public_id LIKE %s AND is_valid = TRUE ORDER BY public_id DESC LIMIT 1;"""
#
#         cur.execute(sql_str, (f'SEC-{current_year}-%',))
#         # cur.execute(sql_str, (f'SEC-2018-%',))
#
#         if cur.rowcount < 1:
#             return 0
#         else:
#             return int(cur.fetchone()[0].split('-')[-1])


def fetch_vulnerable_commits_without_public_id():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """SELECT triage_commit.id, triage_commit.language, triage_commit.subject, triage_commit.public_id 
        FROM triage_commit INNER JOIN "2_scantist_repolist" ON triage_commit.repo_id = "2_scantist_repolist".id
        WHERE "2_scantist_repolist".type = 'ml20181205' 
        AND triage_commit.status = 1 AND (triage_commit.public_id IS NULL OR triage_commit.public_id = '');"""

        cur.execute(sql_str)
        return cur.fetchall(), cur.rowcount


def insert_libraryversionissue(libraryversionissue):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_string = """INSERT INTO scantist_libraryversionissue 
            (created, modified, is_source, library_version_id, security_issue_id, issue_type, up_to, is_valid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

        cur.execute(sql_string, libraryversionissue)


def insert_libraryversionissue_group(libraryversionissue_to_update):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        sql_str = """INSERT INTO scantist_libraryversionissue 
            (created, modified, is_source, library_version_id, security_issue_id, issue_type, up_to, is_valid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

        cur.executemany(sql_str, tuple(libraryversionissue_to_update))


def check_existing_libraryversionissue(lib_ver_id, sec_issue_id):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        query_str = """SELECT id FROM scantist_libraryversionissue 
        WHERE library_version_id = %s AND security_issue_id = %s AND is_valid = TRUE;"""

        cur.execute(query_str, (lib_ver_id, sec_issue_id,))

        return cur.rowcount < 1


def get_library_id_with_repo_id(repo_id):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()
        query_str = """SELECT library_id, repolist_id FROM "2_scantist_libraryrepourl" 
                WHERE is_valid = TRUE AND repolist_id = %s;"""

        cur.execute(query_str, (repo_id,))

        if cur.rowcount != 1:
            return None

        return cur.fetchone()[0]


def get_all_repo_id_and_library_id():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()
        query_str = """SELECT repolist_id, library_id FROM "2_scantist_libraryrepourl";"""

        cur.execute(query_str)

        return cur.fetchall()


def fetch_libraryversion(library_id):
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        query_str = """SELECT id, version_number FROM scantist_library_version 
        WHERE library_id = %s AND is_valid = TRUE;"""

        cur.execute(query_str, (library_id,))

        if cur.rowcount < 1:
            return []

        return cur.fetchall()


def fetch_all_libraryversion():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        query_str = """SELECT library_id, id, version_number FROM scantist_library_version;"""

        cur.execute(query_str)

        if cur.rowcount < 1:
            return []
        ret_dict = []
        for item in cur.fetchall():
            ret_dict.append({item[0]: [item[1], item[2]]})
        return ret_dict


def fetch_unprocessed_commits_with_public_id():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        query_str = """SELECT id, subject, repo_id, public_id, affected_versions, language FROM triage_commit 
        WHERE public_id IS NOT NULL AND processed_time IS NULL AND affected_versions != '{}';"""  # AND description IS NOT NULL

        cur.execute(query_str)
        return cur.fetchall(), cur.rowcount


def get_repo_list():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()
        query_str = """SELECT id, repo_url, homepage_url, language_id, sync_time, db_import_time, name, local_path
                        FROM "2_scantist_repolist" WHERE id in (
                            SELECT repolist_id from "2_scantist_libraryrepourl"
                            where is_valid=true
                        );"""
        print('fetching repo_list ...')
        cur.execute(query_str)
        return cur.fetchall()


def get_filter_keywords():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()
        query_str = 'select keyword, language_id from "2_scantist_keyword";'
        cur.execute(query_str)

        keyword_dict = {}
        for keyword in cur.fetchall():
            if keyword[1] in keyword_dict:
                keyword_dict[keyword[1]].append(keyword[0])
            else:
                keyword_dict[keyword[1]] = [keyword[0]]

        return keyword_dict


# def delete_misc_commits(commit_ids):
#     with get_conn() as conn:
#         conn.autocommit = True
#         cur = conn.cursor()
#         triage_triageresult_query_str = "DELETE FROM triage_triageresult WHERE commit_id = %s;"
#         triage_deeplearning_query_str = "DELETE FROM triage_deeplearning WHERE commit_id = %s;"
#         triage_commit_query_str = "DELETE FROM triage_commit WHERE id = %s;"
#
#         for commit_id in commit_ids:
#             print(f'deleting: {commit_id}')
#             cur.execute(triage_triageresult_query_str, (commit_id,))
#             cur.execute(triage_deeplearning_query_str, (commit_id,))
#             cur.execute(triage_commit_query_str, (commit_id,))


def fetch_commits_without_version():
    with get_conn() as conn:
        conn.autocommit = True
        cur = conn.cursor()

        query_string = """SELECT
                            triage_commit.id, 
                            triage_commit.commitId, 
                            triage_commit.created_date, 
                            triage_commit.affected_versions,
                            "2_scantist_repolist".repo_url 
	                      FROM triage_commit INNER JOIN "2_scantist_repolist" 
	                      ON triage_commit.repo_id = "2_scantist_repolist".id 
	                      WHERE "2_scantist_repolist".type = 'ml20181205' 
	                      AND triage_commit.status = 1 
	                      AND triage_commit.affected_versions = '{}';"""

        cur.execute(query_string)

        if cur.rowcount >= 1:
            return cur.fetchall()
        else:
            return None


# def update_commit_with_release_data(commit):
#     query_string = """UPDATE triage_commit SET affected_versions = %s WHERE id = %s;"""
#
#     with get_conn() as conn:
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         print(f'updating {commit["id"]}')
#         cur.execute(query_string, (json.dumps(
#             commit['releases']), commit['id']))

#
# def get_all_libraryid_name_and_platform():
#     query_string = """SELECT name, platform, id from scantist_library where name != '' and platform != '';"""
#
#     with get_conn() as conn:
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         cur.execute(query_string)
#
#         keyword_dict = {}
#         for keyword in cur.fetchall():
#             keyword_dict[f'{keyword[0]}-{keyword[1]}'] = keyword[2]
#         return keyword_dict


# def get_all_libraryid_name_and_platform_for_java():
#     query_string = """SELECT name, platform, id, vendor from scantist_library where name != '' and platform = 'Maven';"""
#
#     with get_conn() as conn:
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         cur.execute(query_string)
#
#         keyword_dict = {}
#         for keyword in cur.fetchall():
#             keyword_dict[f'{keyword[3]}:{keyword[0]}-{keyword[1]}'] = keyword[2]
#         return keyword_dict


LANGUAGE_ID_MAPPING = {
    'c': 1,
    'c++': 1,
    'java': 2,
    'javascript': 3,
    'python': 4,
    'ruby': 5,
    'go': 6,
    'php': 7
}

ID_LANGUAGE_MAPPING = {
    1: 'c/c++',
    2: 'java',
    3: 'javascript',
    4: 'python',
    5: 'ruby',
    6: 'go',
    7: 'php'
}

if __name__ == '__main__':
    res = get_filter_keywords()
    print(res)
