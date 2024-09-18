# cribl-jobs-api
Dump data from the job API in Cribl to help with monitoring scheduled tasks. Status, stats, and timing are available to use as required.

## Sample run

```
$ python3 cribl_job_monitor.py -l https://main-my-instance.cribl.cloud/api/v1
[
    {
        "id": "1726669500.2210.scheduled.purple_air",
        "status": {
            "state": "finished"
        },
        "stats": {
            "tasks": {
                "finished": 2,
                "failed": 0,
                "cancelled": 0,
                "orphaned": 0,
                "inFlight": 0,
                "count": 2,
                "totalExecutionTime": 514,
                "minExecutionTime": 48,
                "maxExecutionTime": 466
            },
            "discoveryComplete": 1,
            "state": {
                "initializing": 1726669500716,
                "pending": 1726669500755,
                "running": 1726669500854,
                "finished": 1726669501501
            },
            "totalResults": 1,
            "collectedBytes": 0,
            "collectedEvents": 1,
            "discoveredEvents": 1,
            "filteredEvents": 0,
            "flushedBuffers": 0
        },
        "name": "purple_air",
        "wg": "homenet"
    },
 
<snip more items>
```
