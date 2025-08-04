def test_single_workflow(rest_client, api_root):
    identifier = "myworkflow"

    response = rest_client.get(f"{api_root}/workflow/{identifier}")
    assert response.status_code == 404

    workflow1a = {"graph": {"id": identifier}, "nodes": [{"id": "task1"}]}
    response = rest_client.post(f"{api_root}/workflows", json=workflow1a)
    data = response.json()
    assert response.status_code == 200, data
    assert data == workflow1a

    response = rest_client.get(f"{api_root}/workflow/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == workflow1a

    workflow1b = {"graph": {"id": identifier}, "nodes": [{"id": "task2"}]}
    response = rest_client.put(f"{api_root}/workflow/{identifier}", json=workflow1b)
    data = response.json()
    assert response.status_code == 200, data
    assert data == workflow1b

    response = rest_client.get(f"{api_root}/workflow/{identifier}")
    data = response.json()
    assert response.status_code == 200, data
    assert data == workflow1b

    response = rest_client.delete(f"{api_root}/workflow/{identifier}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"identifier": identifier}

    response = rest_client.delete(f"{api_root}/workflow/{identifier}")
    data = response.json()
    assert response.status_code == 404
    assert data["message"] == f"Workflow '{identifier}' is not found."

    response = rest_client.get(f"{api_root}/workflow/{identifier}")
    data = response.json()
    assert response.status_code == 404
    assert data["message"] == f"Workflow '{identifier}' is not found."


def test_workflow_creation_errors(rest_client, default_workflow_identifiers, api_root):
    workflow_without_id = {"graph": {}}
    response = rest_client.post(f"{api_root}/workflows", json=workflow_without_id)
    assert response.status_code == 422
    data = response.json()
    assert data["message"] == "Workflow identifier missing"

    workflow_with_empty_id = {"graph": {"id": ""}}
    response = rest_client.post(f"{api_root}/workflows", json=workflow_with_empty_id)
    assert response.status_code == 422
    data = response.json()
    assert data["message"] == "Workflow identifier cannot be empty"

    existing_id = default_workflow_identifiers[0]
    workflow_with_existing_id = {"graph": {"id": existing_id}}
    response = rest_client.post(f"{api_root}/workflows", json=workflow_with_existing_id)
    assert response.status_code == 409
    data = response.json()
    assert data["message"] == f"Workflow '{existing_id}' already exists."


def test_multiple_workflows(rest_client, default_workflow_identifiers, api_root):
    response = rest_client.get(f"{api_root}/workflows")
    data = response.json()
    assert response.status_code == 200
    assert data == {"identifiers": list(default_workflow_identifiers)}

    workflow1a = {"graph": {"id": "myworkflow1"}, "nodes": [{"id": "task1"}]}
    workflow1b = {"graph": {"id": "myworkflow1"}, "nodes": [{"id": "task2"}]}
    workflow2 = {"graph": {"id": "myworkflow2"}, "nodes": [{"id": "task1"}]}

    response = rest_client.post(f"{api_root}/workflows", json=workflow1a)
    data = response.json()
    assert response.status_code == 200, data

    response = rest_client.post(f"{api_root}/workflows", json=workflow1b)
    data = response.json()
    assert response.status_code == 409, data
    assert data["message"] == "Workflow 'myworkflow1' already exists."
    response = rest_client.post(f"{api_root}/workflows", json=workflow2)
    data = response.json()
    assert response.status_code == 200, data

    response = rest_client.get(f"{api_root}/workflows")
    data = response.json()
    assert response.status_code == 200
    expected = default_workflow_identifiers + ["myworkflow1", "myworkflow2"]
    assert sorted(data["identifiers"]) == sorted(expected)


def test_workflow_descriptions(rest_client, default_workflow_identifiers, api_root):
    response = rest_client.get(f"{api_root}/workflows/descriptions")
    data = response.json()
    assert response.status_code == 200
    default_descriptions = [
        desc for desc in data["items"] if desc["id"] in default_workflow_identifiers
    ]
    assert data == {"items": default_descriptions}

    workflow1 = {
        "graph": {"id": "myworkflow1", "label": "label1", "category": "cat1"},
        "nodes": [{"id": "task1"}],
    }
    workflow2 = {"graph": {"id": "myworkflow2"}, "nodes": [{"id": "task1"}]}
    response = rest_client.post(f"{api_root}/workflows", json=workflow1)
    data = response.json()
    assert response.status_code == 200, data
    response = rest_client.post(f"{api_root}/workflows", json=workflow2)
    data = response.json()
    assert response.status_code == 200, data

    response = rest_client.get(f"{api_root}/workflows/descriptions")
    data = response.json()["items"]
    assert response.status_code == 200
    expected = default_descriptions + [
        {"id": "myworkflow1", "label": "label1", "category": "cat1"},
        {"id": "myworkflow2"},
    ]
    data = sorted(data, key=lambda x: x["id"])
    assert data == expected


def test_workflow_description_keys(rest_client, default_workflow_identifiers, api_root):
    desc = {
        "id": "myworkflow1",
        "label": "label1",
        "category": "cat1",
        "keywords": {"tags": ["XRPD", "ID00"]},
        "input_schema": {"title": "Demo workflow"},
        "ui_schema": {"mx_pipeline_name": {"ui:widget": "checkboxes"}},
    }
    workflow1 = {
        "graph": {
            **desc,
            "custom1": 1,
            "custom2": {},
            "execute_arguments": {"engine": "ppf"},
            "worker_options": {"queue": "id00"},
        },
        "nodes": [{"id": "task1"}],
    }
    response = rest_client.post(f"{api_root}/workflows", json=workflow1)
    data = response.json()
    assert response.status_code == 200, data

    response = rest_client.get(
        f'{api_root}/workflows/descriptions?kw=tags:["XRPD", "ID00"]'
    )
    data = response.json()["items"]
    assert data == [desc], data


def test_workflow_keywords(rest_client, default_workflow_identifiers, api_root):
    for instrument_name in ("ID00", "ID99"):
        for scan_type in ("ct", "loopscan"):
            workflow = {
                "graph": {
                    "id": f"myworkflow_{instrument_name}_{scan_type}",
                    "label": "label1",
                    "category": "cat1",
                    "keywords": {
                        "instrument_name": instrument_name,
                        "scan_type": scan_type,
                    },
                },
                "nodes": [{"id": "task1"}],
            }
            response = rest_client.post(f"{api_root}/workflows", json=workflow)
            data = response.json()
            assert response.status_code == 200, data

    response = rest_client.get(f"{api_root}/workflows")
    data = response.json()["identifiers"]
    assert response.status_code == 200
    expected = default_workflow_identifiers + [
        "myworkflow_ID00_ct",
        "myworkflow_ID00_loopscan",
        "myworkflow_ID99_ct",
        "myworkflow_ID99_loopscan",
    ]
    assert sorted(data) == sorted(expected)

    response = rest_client.get(f"{api_root}/workflows?kw=instrument_name:ID00")
    data = response.json()["identifiers"]
    assert response.status_code == 200
    expected = ["myworkflow_ID00_ct", "myworkflow_ID00_loopscan"]
    assert sorted(data) == sorted(expected)

    response = rest_client.get(
        f"{api_root}/workflows?kw=instrument_name:ID00&kw=scan_type:ct"
    )
    data = response.json()["identifiers"]
    assert response.status_code == 200
    assert data == ["myworkflow_ID00_ct"]

    response = rest_client.get(f"{api_root}/workflows/descriptions")
    data = [res["id"] for res in response.json()["items"]]
    expected = default_workflow_identifiers + [
        "myworkflow_ID00_ct",
        "myworkflow_ID00_loopscan",
        "myworkflow_ID99_ct",
        "myworkflow_ID99_loopscan",
    ]
    assert sorted(data) == sorted(expected)

    response = rest_client.get(
        f"{api_root}/workflows/descriptions?kw=instrument_name:ID00"
    )
    data = [res["id"] for res in response.json()["items"]]
    expected = ["myworkflow_ID00_ct", "myworkflow_ID00_loopscan"]
    assert sorted(data) == sorted(expected)

    response = rest_client.get(
        f"{api_root}/workflows/descriptions?kw=instrument_name:ID00&kw=scan_type:ct",
    )
    data = [res["id"] for res in response.json()["items"]]
    assert data == ["myworkflow_ID00_ct"]
