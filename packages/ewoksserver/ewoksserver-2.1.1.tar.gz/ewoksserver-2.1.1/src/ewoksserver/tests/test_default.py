def test_default_workflows(rest_client, default_workflow_identifiers, api_root):
    for identifier in default_workflow_identifiers:
        response = rest_client.get(f"{api_root}/workflow/{identifier}")
        data = response.json()
        assert response.status_code == 200, data


def test_default_icons(rest_client, default_icon_identifiers, api_root):
    for identifier in default_icon_identifiers:
        response = rest_client.get(f"{api_root}/icon/{identifier}")
        data = response.json()
        assert response.status_code == 200, data


def test_default_tasks(rest_client, default_task_identifiers, api_root):
    for identifier in default_task_identifiers:
        response = rest_client.get(f"{api_root}/task/{identifier}")
        data = response.json()
        assert response.status_code == 200, data
