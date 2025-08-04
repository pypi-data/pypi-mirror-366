from ..app import backend


def test_get_routes():
    routes = {(1, 0, 0): None, (1, 0, 1): None, (2, 0, 0): None}

    all_routes = backend.get_routes("test", routes)
    expected = {
        (1, 0, 0, 0): backend.Route(
            router=None, prefix="/api/v1_0_0", tag="v1.0.0", versioned=True
        ),
        (1, 0, 1, 0): backend.Route(
            router=None, prefix="/api/v1_0_1", tag="v1.0.1", versioned=True
        ),
        (2, 0, 0, 0): backend.Route(
            router=None, prefix="/api/v2_0_0", tag="v2.0.0", versioned=True
        ),
        (1, 0, 1, 1): backend.Route(
            router=None, prefix="/api/v1", tag="v1", versioned=True
        ),
        (2, 0, 0, 1): backend.Route(
            router=None, prefix="/api/v2", tag="v2", versioned=True
        ),
        (2, 0, 0, 2): backend.Route(
            router=None, prefix="/api", tag="test", versioned=False
        ),
    }
    assert all_routes == expected

    all_routes = backend.get_routes("test", routes, suffix="testprefix")
    expected = {
        (1, 0, 0, 0): backend.Route(
            router=None, prefix="/api/v1_0_0/testprefix", tag="v1.0.0", versioned=True
        ),
        (1, 0, 1, 0): backend.Route(
            router=None, prefix="/api/v1_0_1/testprefix", tag="v1.0.1", versioned=True
        ),
        (2, 0, 0, 0): backend.Route(
            router=None, prefix="/api/v2_0_0/testprefix", tag="v2.0.0", versioned=True
        ),
        (1, 0, 1, 1): backend.Route(
            router=None, prefix="/api/v1/testprefix", tag="v1", versioned=True
        ),
        (2, 0, 0, 1): backend.Route(
            router=None, prefix="/api/v2/testprefix", tag="v2", versioned=True
        ),
        (2, 0, 0, 2): backend.Route(
            router=None, prefix="/api/testprefix", tag="test", versioned=False
        ),
    }
    assert all_routes == expected
