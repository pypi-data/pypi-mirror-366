import pytest
from ewoksjob.client.futures import TimeoutError


def test_discover_tasks_from_a_module(rest_client, default_task_identifiers, api_root):
    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == sorted(default_task_identifiers)

    module = "ewoksserver.tests.dummy_tasks"

    response = rest_client.post(
        f"{api_root}/tasks/discover", json={"modules": [module]}
    )
    data = response.json()
    assert response.status_code == 200, data
    expected = [
        "ewoksserver.tests.dummy_tasks.MyTask1",
        "ewoksserver.tests.dummy_tasks.MyTask2",
        "ewoksserver.tests.dummy_tasks.my_task3",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)

    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    expected = default_task_identifiers + [
        "ewoksserver.tests.dummy_tasks.MyTask1",
        "ewoksserver.tests.dummy_tasks.MyTask2",
        "ewoksserver.tests.dummy_tasks.my_task3",
    ]
    assert sorted(data["identifiers"]) == sorted(expected)


def test_discover_method_task_type(rest_client, api_root):
    module = "ewoksserver.tests.dummy_tasks"

    response = rest_client.post(
        f"{api_root}/tasks/discover",
        json={"modules": [module], "task_type": "method"},
    )
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == ["ewoksserver.tests.dummy_tasks.my_task3"]


def test_discover_all_tasks(rest_client, default_task_identifiers, api_root):
    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert sorted(data["identifiers"]) == sorted(default_task_identifiers)

    response = rest_client.post(f"{api_root}/tasks/discover")
    data = response.json()
    assert response.status_code == 200, data
    expected = default_task_identifiers + [
        "ewokscore.tests.examples.tasks.addfunc.addfunc",
        "ewokscore.tests.examples.tasks.condsumtask.CondSumTask",
        "ewokscore.tests.examples.tasks.errorsumtask.ErrorSumTask",
        "ewokscore.tests.examples.tasks.nooutputtask.NoOutputTask",
        "ewokscore.tests.examples.tasks.simplemethods.add",
        "ewokscore.tests.examples.tasks.simplemethods.append",
    ]
    assert set(expected) <= set(data["identifiers"])

    response = rest_client.get(f"{api_root}/tasks")
    data = response.json()
    assert response.status_code == 200
    assert set(expected) <= set(data["identifiers"])


def test_discover_in_a_non_existing_module(rest_client, api_root):
    response = rest_client.post(
        f"{api_root}/tasks/discover", json={"modules": ["not_a_module"]}
    )
    data = response.json()
    assert response.status_code == 404, data
    assert "No module named" in data["message"]

    response = rest_client.post(f"{api_root}/tasks/discover")
    data = response.json()
    assert response.status_code == 200, data
    assert data["identifiers"]


def test_discover_timeout(celery_discover_timeout_client, api_root):
    rest_client, _ = celery_discover_timeout_client
    with pytest.raises(TimeoutError):
        rest_client.post(f"{api_root}/tasks/discover")
