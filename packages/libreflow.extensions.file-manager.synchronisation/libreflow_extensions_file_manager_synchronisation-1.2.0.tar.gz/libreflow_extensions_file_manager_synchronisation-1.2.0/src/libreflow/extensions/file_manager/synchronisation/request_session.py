import os
import re
import sys
import argparse
import fnmatch
import time
import traceback
import datetime
from kabaret import flow
from libreflow.session import BaseCLISession
from .sync_utils import resolve_pattern


def parse_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Request Session Arguments'
    )
    parser.add_argument(
        '-p', '--project', dest='project',
    )
    parser.add_argument(
        '-d', '--delay',
        dest='delay', type=int, default=180,
        help="Delay before restarting batch requests."
    )
    parser.add_argument(
        '--lifetime-limit',
        dest='lifetime_limit', type=float, default=600.0,
        help="Exclude revisions newer than this lifetime."
    )
    values, _ = parser.parse_known_args(args)

    return (
        values.project,
        values.delay,
        values.lifetime_limit
    )

patterns = {
    # "/anpo/films/anpo/sequences/sq001/shots/*/tasks/layout/files/layout_blend/history/revisions/*": ['lfs'],
    # "/anpo/films/anpo/sequences/sq001/shots/*/tasks/layout/files/layout_blend/history/revisions/v001": ['lfs', 'faraway'],
    # "/anpo/asset_types/*/asset_families/*/assets/*/tasks/{design,rigging,shading}/files/{layers, rigging_blend, textures*}/history/revisions/v001": ['lfs', 'faraway'],
    # "/anpo/asset_types/*/asset_families/*/assets/*/tasks/{shading}/files/{textures*}/history/revisions/v002": ['faraway'],
    # "/anpo/films/anpo/sequences/sq002/shots/sh000{35,36,37}/tasks/animation/files/animation_blend/history/revisions/v???": ['lfs']
    "/anpo/films/anpo/sequences/sq999/shots/sh00999/tasks/layout/files/layout_blend/history/revisions/v???": ['lfs', 'faraway']
}
def log(msg):
    print("[REQUEST SESSION - %s] %s" % (
        datetime.datetime.fromtimestamp(time.time()).strftime('%y-%m-%d %H:%M:%S'),
        msg
    ))

def get_revisions(session, project_name, created_before):
    entity_mng = session.cmds.Flow.call('/'+project_name, 'get_entity_manager', [], {})
    coll_files = entity_mng.get_file_collection()
    coll_revisions = entity_mng.get_revision_collection()
    coll_statutes = entity_mng.get_sync_status_collection()
    c = coll_statutes.get_entity_store().get_collection(coll_statutes.collection_name())
    return c.aggregate([
        {
            '$addFields': {
                'revision': {
                    '$regexFind': {'input': '$name', 'regex': r'(.+)/sync_statutes/[^/]+$'}
                },
                'site': {
                    '$regexFind': {'input': '$name', 'regex': r'.+/([^/]+)$'}
                }
            }
        },
        {
            '$set': {
                'revision': { '$arrayElemAt': ['$revision.captures', 0] },
                'site':     { '$arrayElemAt': ['$site.captures', 0] },
            }
        },
        {
            '$group': {
                '_id': '$revision',
                'statutes': { '$push': {'site': '$site', 'status': '$status'}},
            }
        },
        {
            '$lookup': {
                'from': coll_revisions.collection_name(),
                'localField': '_id',
                'foreignField': 'name',
                'as': 'revision_data'
            }
        },
        {
            '$lookup': {
                'from': coll_files.collection_name(),
                'localField': '_id',
                'foreignField': 'last_revision_oid',
                'as': 'last_revision_of'
            }
        },
        {
            '$addFields': {
                'date': {'$arrayElemAt': ['$revision_data.date', 0]}
            }
        },
        {
            '$match': {
                '$expr': {'$lt': ['$date', created_before]}
            }
        }
    ])

def get_request_rules(actor, project_name):
    """
    Return the project's request rules as a mapping <pattern>:<list of sites>.
    """
    rules = actor.get_object(f"/{project_name}/admin/project_settings/request_rules")
    return {r.pattern.get(): r.sites.get()
        for r in rules.mapped_items() \
        if r.enabled.get()}

def get_target_sites(revision_oid, request_rules, sync_statutes, is_latest):
    """
    Return target site names which require the given revision.
    """
    target_sites = set()
    for pattern, sites in request_rules.items():
        sites = set(sites)
        if sites.issubset(target_sites):
            continue

        for p in resolve_pattern(pattern):
            if re.search(r'\[last\]$', p) is not None:
                if not is_latest:
                    continue
                p = re.sub(r'\[last\]$', revision_oid.rsplit('/', 1)[1], p)
            if not fnmatch.fnmatch(revision_oid, p):
                continue

            target_sites |= set(sites)
            break
    target_sites = {name for name in target_sites \
        if sync_statutes.get(name, 'NotAvailable') != 'Available'}
    return target_sites

def get_job_queue(actor, project_name, site_name):
    oid = f"/{project_name}/admin/multisites/working_sites/{site_name}/queue/job_list"
    return actor.get_object(oid)

def get_request_status(job_queue, job_type, revision_oid):
    """
    Return the status of the first job found in the given queue
    with the given type and revision oid.
    """
    coll = job_queue.get_entity_store().get_collection(
        job_queue.collection_name())
    result = coll.find({'emitter_oid': revision_oid,
                        'type': job_type})
    statutes = set([j['status'] for j in result])
    if 'WAITING' in statutes:
        return 'WAITING'
    elif 'ERROR' in statutes:
        return 'ERROR'

    return None # force upload

def send_requests(actor, project_name, revision_oid, target_sites, user_name):
    """
    Request the download of the given revision for the given sites.
    If the revision is not uploaded yet, an upload is requested at
    the source site.
    """
    try:
        rev = actor.get_object(revision_oid)
    except flow.exceptions.MappedNameError:
        log(f"ERROR - Invalid revision oid: {revision_oid}")
        return

    for target_site in target_sites:
        if rev.get_sync_status(site_name=target_site) == 'Available':
            log(f"{revision_oid} already available at {target_site}")
            continue

        target_jobs = get_job_queue(actor, project_name, target_site)
        request_status = get_request_status(target_jobs,
            'Download', revision_oid)
        if request_status is None:
            log(f"{revision_oid} -> {target_site}")
            # Add download job for the requesting site
            target_jobs.submit_job(
                job_type='Download',
                init_status='WAITING',
                emitter_oid=revision_oid,
                user=user_name,
                studio=target_site
            )
        else:
            log(f"{revision_oid} download has {request_status} status in {target_site}")
        rev.set_sync_status('Requested', site_name=target_site)

    if rev.get_sync_status(exchange=True) == 'Available':
        # Skip source site request if revision is already uploaded
        return

    source_site_name = rev.site.get()
    source_jobs = get_job_queue(actor, project_name, source_site_name)
    request_status = get_request_status(source_jobs,
        'Upload', revision_oid)
    if request_status is None:
        log(f"{revision_oid} <- {source_site_name}")
        # Add upload job for the source site
        source_jobs.submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=revision_oid,
            user=user_name,
            studio=source_site_name
        )
    else:
        log(f"{revision_oid} upload has {request_status} status in {source_site_name}")

def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        read_replica_host,
        read_replica_port,
        remaining_args,
    ) = BaseCLISession.parse_command_line_args(argv)

    session = BaseCLISession(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)
    actor = session.get_actor('Flow')
    project_name, delay, lifetime_limit = parse_remaining_args(remaining_args)
    user_name = session.cmds.Flow.call(f"/{project_name}",
        'get_user_name', [], {})

    while (True):
        i = 0
        start = time.time()
        log(f"Searching for new revisions to request...")
        request_rules = get_request_rules(actor, project_name)
        cursor = get_revisions(session, project_name, time.time()-lifetime_limit)
        for d in cursor:
            statutes = {s['site']: s['status'] \
                for s in d['statutes'] \
                if s['site'] != 'exchange'}
            target_sites = get_target_sites(d['_id'], request_rules, statutes, bool(d.get('last_revision_of')))
            if not target_sites:
                continue

            send_requests(actor, project_name, d['_id'], target_sites, user_name)
            i += 1

        if i > 0:
            log(f"Found {i} revision matches in {time.time() - start:.3}s")
        time.sleep(delay)


if __name__ == "__main__":
    while True:
        try:
            main(sys.argv[1:])
        except (Exception, KeyboardInterrupt) as e:
            if isinstance(e, KeyboardInterrupt):
                print("Request session stopped")
                sys.exit(0)
            else:
                print("The following error occurred:")
                print(traceback.format_exc())
                print("Restarting request session...")
                time.sleep(10)
