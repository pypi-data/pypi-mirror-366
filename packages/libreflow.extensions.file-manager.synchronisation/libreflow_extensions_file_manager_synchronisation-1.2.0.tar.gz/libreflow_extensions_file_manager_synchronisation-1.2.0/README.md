# Libreflow request session

This session periodically requests file revisions according to request rules. A rule provides a set of target files, and an OID pattern: each revision matching this pattern will be requested for download towards the specified sites.

### Usage

Assuming the module `libreflow.extensions.file_manager.synchronisation` is accessible in the `PYTHONPATH`, the automatic request session can be run as follows:
```
python -m request_session LIBREFLOW_SESSION_OPTIONS REQUEST_OPTIONS
```

where `LIBREFLOW_SESSION_OPTIONS` are arguments of a standard libreflow session (see Libreflow [README](https://gitlab.com/lfs.coop/libreflow/libreflow#run)), and `REQUEST_OPTIONS` are the following:
```
-p, --project <name>           Name of the project.
-d, --delay <time>             Delay between two batch requests.
    --lifetime-limit <time>    Exclude revisions newer than this lifetime.
```

The session processes the rules defined in the `request_rules` under the project settings. Each rule associates a revision oid pattern with a list of target sites.