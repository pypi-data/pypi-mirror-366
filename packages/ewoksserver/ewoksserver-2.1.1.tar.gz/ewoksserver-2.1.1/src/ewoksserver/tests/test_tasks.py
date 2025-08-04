import json


def test_single_task(rest_client, api_root):
    identifier = "myproject.tasks.Dummy"

    response = rest_client.get(f"{api_root}/task/{identifier}")
    data = response.json()
    expected = {
        "message": "Task 'myproject.tasks.Dummy' is not found.",
        "type": "task",
        "identifier": "myproject.tasks.Dummy",
    }
    assert response.status_code == 404
    assert data == expected

    task1a = {
        "task_identifier": identifier,
        "task_type": "class",
        "required_input_names": ["a"],
    }
    response = rest_client.post(f"{api_root}/tasks", json=task1a)
    data = response.json()
    assert response.status_code == 200, data
    expected = {
        "required_input_names": ["a"],
        "task_identifier": "myproject.tasks.Dummy",
        "task_type": "class",
    }
    assert data == expected

    response = rest_client.get(f"{api_root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1a

    task1b = {
        "task_identifier": identifier,
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }
    response = rest_client.put(f"{api_root}/task/{identifier}", json=task1b)
    data = response.json()
    assert response.status_code == 200, data
    expected = {
        "required_input_names": ["a", "b"],
        "task_identifier": "myproject.tasks.Dummy",
        "task_type": "class",
    }
    assert data == expected

    response = rest_client.get(f"{api_root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1b

    response = rest_client.delete(f"{api_root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"identifier": identifier}

    response = rest_client.delete(f"{api_root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 404
    assert data == {
        "identifier": identifier,
        "message": f"Task '{identifier}' is not found.",
        "type": "task",
    }

    response = rest_client.get(f"{api_root}/task/{identifier}")
    data = response.json()
    assert response.status_code == 404
    expected = {
        "identifier": identifier,
        "message": f"Task '{identifier}' is not found.",
        "type": "task",
    }
    assert data == expected


def test_task_creation_errors(rest_client, default_task_identifiers, api_root):
    task_without_id = {"task_type": "class"}
    response = rest_client.post(f"{api_root}/tasks", json=task_without_id)
    assert response.status_code == 422

    task_with_empty_id = {"task_identifier": "", "task_type": "class"}
    response = rest_client.post(f"{api_root}/tasks", json=task_with_empty_id)
    assert response.status_code == 422
    data = response.json()
    assert data["message"] == "Task identifier cannot be empty"

    existing_id = default_task_identifiers[0]
    task_with_existing_id = {"task_identifier": existing_id, "task_type": "class"}
    response = rest_client.post(f"{api_root}/tasks", json=task_with_existing_id)
    assert response.status_code == 409
    data = response.json()
    assert data["message"] == f"Task '{existing_id}' already exists."


def test_multiple_tasks(rest_client, default_task_identifiers, api_root):
    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == sorted(default_task_identifiers)

    task1a = {
        "task_identifier": "myproject.tasks.Dummy1",
        "task_type": "class",
        "required_input_names": ["a"],
    }
    task1b = {
        "task_identifier": "myproject.tasks.Dummy1",
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }
    task2 = {
        "task_identifier": "myproject.tasks.Dummy2",
        "task_type": "class",
        "required_input_names": ["a", "b"],
    }

    response = rest_client.post(f"{api_root}/tasks", json=task1a)
    data = response.json()
    assert response.status_code == 200, data
    assert data == task1a

    response = rest_client.post(f"{api_root}/tasks", json=task1b)
    data = response.json()
    assert response.status_code == 409, data
    expected = {
        "identifier": "myproject.tasks.Dummy1",
        "message": "Task 'myproject.tasks.Dummy1' already exists.",
        "type": "task",
    }
    assert data == expected

    response = rest_client.post(f"{api_root}/tasks", json=task2)
    data = response.json()
    assert response.status_code == 200, data
    assert data == task2

    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200, data
    expected = default_task_identifiers + [
        "myproject.tasks.Dummy1",
        "myproject.tasks.Dummy2",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)


def test_task_descriptions(rest_client, default_task_identifiers, api_root):
    response = rest_client.get(f"{api_root}/tasks/descriptions")
    data = response.json()
    assert response.status_code == 200
    default_descriptions = [
        desc
        for desc in data["items"]
        if desc["task_identifier"] in default_task_identifiers
    ]
    assert data == {"items": default_descriptions}

    module = "ewoksserver.tests.dummy_tasks"

    response = rest_client.post(
        f"{api_root}/tasks/discover", json={"modules": [module]}
    )
    data1 = response.json()
    assert response.status_code == 200, data1

    response = rest_client.get(f"{api_root}/tasks/descriptions")
    data2 = response.json()["items"]
    data2 = [
        r["task_identifier"] for r in data2 if r["task_identifier"].startswith(module)
    ]
    assert response.status_code == 200
    assert sorted(data1["identifiers"]) == sorted(data2)


def test_malformed_task(rest_client, api_root, tmpdir):
    malformed_task_id = "myproject.tasks.Malformed"
    task_malformed = {"task_identifier": malformed_task_id}
    normal_task_id = "myproject.tasks.Normal"
    task_normal = {
        "task_identifier": normal_task_id,
        "task_type": "class",
    }
    response = rest_client.post(f"{api_root}/tasks", json=task_malformed)
    assert response.status_code == 422

    response = rest_client.get(f"{api_root}/tasks/descriptions")
    data = response.json()
    existing_tasks = len(data["items"])

    tasks_dir = tmpdir / "tasks"
    malformed_task_file = tasks_dir / f"{malformed_task_id}.json"
    normal_task_file = tasks_dir / f"{normal_task_id}.json"

    with open(normal_task_file, "w") as f:
        json.dump(task_normal, f)
    with open(malformed_task_file, "w") as f:
        json.dump(task_malformed, f)

    response = rest_client.get(f"{api_root}/tasks/{malformed_task_id}")
    assert response.status_code == 404

    response = rest_client.get(f"{api_root}/tasks/descriptions")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) - existing_tasks == 1

    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert len(data["identifiers"]) - existing_tasks == 1
