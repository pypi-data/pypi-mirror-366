import os
from collections import Counter
from datetime import datetime

from ewokscore.tests.examples.graphs import get_graph

from .test_execute import upload_graph
from .test_execute import get_events


def test_get_execution_events(local_exec_client, api_root):
    client, sclient = local_exec_client

    graph_name, expected = upload_graph(api_root, client)
    nevents = 0
    nevents_per_exec = 2 * (len(expected) + 2)

    # Test no events (nothing has been executed)
    response = client.get(f"{api_root}/execution/events")
    assert response.status_code == 200
    data = response.json()
    assert data == {"jobs": list()}

    # Execute workflow
    response = client.post(f"{api_root}/execute/{graph_name}")
    data = response.json()
    assert response.status_code == 200, data
    job_id1 = data["job_id"]
    nevents += nevents_per_exec

    # Wait until all events have been received over the Socket.IO connection
    events1 = get_events(api_root, sclient, nevents)

    # Query should return the same a what was received over the Socket.IO connection
    response = client.get(f"{api_root}/execution/events")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get(f"{api_root}/execution/events?job_id={job_id1}")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get(f"{api_root}/execution/events?context=job")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert len(events[0]) == 2

    dtmid = datetime.now().astimezone()

    # Execute workflow
    response = client.post(f"{api_root}/execute/{graph_name}")
    data = response.json()
    assert response.status_code == 200, data
    job_id2 = data["job_id"]
    nevents += nevents_per_exec

    # Wait until all events have been received over the Socket.IO connection
    events2 = get_events(api_root, sclient, nevents_per_exec)

    response = client.get(f"{api_root}/execution/events")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 2
    assert events[0] == events1
    assert events[1] == events2

    response = client.get(f"{api_root}/execution/events?job_id={job_id2}")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert events[0] == events2

    response = client.get(f"{api_root}/execution/events?context=job")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 2
    assert len(events[0]) == 2
    assert len(events[1]) == 2

    if os.name == "nt":
        return  # TODO: time filtering fails on windows

    # Test time Query
    midtime = dtmid.isoformat().replace("+", "%2b")
    response = client.get(f"{api_root}/execution/events?endtime={midtime}")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get(f"{api_root}/execution/events?starttime={midtime}")
    assert response.status_code == 200
    events = response.json()["jobs"]
    assert len(events) == 1
    assert events[0] == events2


def test_get_execution_events_parallel(local_exec_client, api_root):
    client, sclient = local_exec_client

    _, expected = get_graph("demo")
    nevents = 0
    nevents_per_exec = 2 * (len(expected) + 2)

    # Test no events (nothing has been executed)
    jobs = client.get(f"{api_root}/execution/events").json()["jobs"]
    assert not jobs

    # Execute workflows in parallel
    nruns = 3
    for _ in range(nruns):
        response = client.post(
            f"{api_root}/execute/demo",
            json={"execute_arguments": {"inputs": [{"name": "delay", "value": 0.1}]}},
        )
        data = response.json()
        assert response.status_code == 200, data
        nevents += nevents_per_exec

    # Get events from Socket.IO and REST API
    events_socketio = get_events(api_root, sclient, nevents)
    events_get = client.get(f"{api_root}/execution/events").json()["jobs"]

    # Check that we have all events from the Socket.IO connection
    nevents = Counter()
    for event in events_socketio:
        nevents[event["job_id"]] += 1
    assert set(nevents.values()) == {nevents_per_exec}

    # Check that we have all events from the REST API
    nevents = Counter()
    for job in events_get:
        for event in job:
            nevents[event["job_id"]] += 1
    assert set(nevents.values()) == {nevents_per_exec}

    # Check whether that events from the REST API are properly grouped per job
    assert len(events_get) == nruns
    for job in events_get:
        assert len({event["job_id"] for event in job}) == 1
