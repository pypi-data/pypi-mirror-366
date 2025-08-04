import time

from ewoksutils import event_utils
from ewokscore.tests.examples.graphs import get_graph

from .api_versions import api_version_bounds


def test_execute_with_celery(celery_exec_client, api_root):
    _test_execute(api_root, *celery_exec_client)


def test_execute_without_celery(local_exec_client, api_root):
    _test_execute(api_root, *local_exec_client)


def test_new_client_new_events(local_exec_client, api_root):
    client, sclient = local_exec_client
    _test_execute(api_root, client, sclient)
    sclient.disconnect()
    sclient.connect()
    time.sleep(1)
    assert not sclient.get_events()


@api_version_bounds(max_version="1.1.0")
def test_execute_options_v1(rest_client, mocked_local_submit, api_root):
    workflow = {
        "graph": {
            "id": "myworkflow",
            "label": "label1",
            "category": "cat1",
            "execute_arguments": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "worker_options": {"queue": "id00"},
        },
        "nodes": [{"id": "task1"}],
    }
    response = rest_client.post(f"{api_root}/workflows", json=workflow)
    data = response.json()
    assert response.status_code == 200, data

    # Check that the backend uses execute_arguments and worker_options
    # from the workflow definition
    response = rest_client.post(f"{api_root}/execute/myworkflow")
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
        },
    }
    assert mocked_local_submit == expected_submit_arguments

    # Check that the backend merges execute_arguments and worker_options
    # from the client
    data = {
        "execute_arguments": {
            "engine": "ppf",
            "slurm_arguments": {
                "parameters": {"time_limit": 20, "partition": "nice"},
                "pre_script": "module load ewoks",
            },
        },
        "worker_options": {"queue": "id00", "time_limit": 30},
    }

    response = rest_client.post(f"{api_root}/execute/myworkflow", json=data)
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 20, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
            "time_limit": 30,
        },
    }
    assert mocked_local_submit == expected_submit_arguments


@api_version_bounds(min_version="2.0.0")
def test_execute_options(rest_client, mocked_local_submit, api_root):
    workflow = {
        "graph": {
            "id": "myworkflow",
            "label": "label1",
            "category": "cat1",
            "execute_arguments": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "submit_arguments": {"queue": "id00"},
        },
        "nodes": [{"id": "task1"}],
    }
    response = rest_client.post(f"{api_root}/workflows", json=workflow)
    data = response.json()
    assert response.status_code == 200, data

    # Check that the backend uses execute_arguments and submit_arguments
    # from the workflow definition
    response = rest_client.post(f"{api_root}/execute/myworkflow")
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 10, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
        },
    }
    assert mocked_local_submit == expected_submit_arguments

    # Check that the backend merges execute_arguments and submit_arguments
    # from the client
    data = {
        "execute_arguments": {
            "engine": "ppf",
            "slurm_arguments": {
                "parameters": {"time_limit": 20, "partition": "nice"},
                "pre_script": "module load ewoks",
            },
        },
        "submit_arguments": {"queue": "id00", "time_limit": 30},
    }

    response = rest_client.post(f"{api_root}/execute/myworkflow", json=data)
    expected_submit_arguments = {
        "args": (),
        "kwargs": {
            "args": (workflow,),
            "kwargs": {
                "engine": "ppf",
                "slurm_arguments": {
                    "parameters": {"time_limit": 20, "partition": "nice"},
                    "pre_script": "module load ewoks",
                },
            },
            "queue": "id00",
            "time_limit": 30,
        },
    }
    assert mocked_local_submit == expected_submit_arguments


def _test_execute(api_root, client, sclient):
    graph_name, expected = upload_graph(api_root, client)
    response = client.post(f"{api_root}/execute/{graph_name}")
    assert response.status_code == 200, response.json()

    n = 2 * (len(expected) + 2)
    events = get_events(api_root, sclient, n)
    _assert_events(response, events, expected)
    return n


def upload_graph(api_root, client):
    graph_name = "acyclic1"
    graph, expected = get_graph(graph_name)
    response = client.post(f"{api_root}/workflows", json=graph)
    assert response.status_code == 200, response.json()
    return graph_name, expected


def get_events(api_root, sclient, nevents, timeout=10):
    t0 = time.time()
    events = list()
    while True:
        for event in sclient.get_events():
            if "/v1" in api_root and "engine" in event_utils.FIELD_TYPES:
                event["binding"] = event.pop("engine")
            events.append(event)
        if len(events) == nevents:
            break
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            raise TimeoutError(f"Received {len(events)} instead of {nevents}")
    return events


def _assert_events(response, events, expected):
    n = 2 * (len(expected) + 2)
    assert len(events) == n

    job_id = response.json()["job_id"]
    for event in events:
        assert event["job_id"] == job_id
        if event["node_id"]:
            assert event["node_id"] in expected


@api_version_bounds(min_version="1.1.0", max_version="1.1.0")
def test_get_workers_with_celery(celery_exec_client, api_root):
    rest_client, _ = celery_exec_client
    response = rest_client.get(f"{api_root}/execution/workers")
    assert response.status_code == 200, response.json()
    assert response.json()["workers"] == ["celery"]


@api_version_bounds(min_version="1.1.0", max_version="1.1.0")
def test_get_workers_without_celery(rest_client, api_root):
    response = rest_client.get(f"{api_root}/execution/workers")
    assert response.status_code == 200, response.json()
    assert response.json()["workers"] is None


@api_version_bounds(min_version="2.0.0")
def test_get_queues_with_celery(celery_exec_client, api_root):
    rest_client, _ = celery_exec_client
    response = rest_client.get(f"{api_root}/execution/queues")
    assert response.status_code == 200, response.json()
    assert response.json()["queues"] == ["celery"]


@api_version_bounds(min_version="2.0.0")
def test_get_queues_without_celery(rest_client, api_root):
    response = rest_client.get(f"{api_root}/execution/queues")
    assert response.status_code == 200, response.json()
    assert response.json()["queues"] is None
