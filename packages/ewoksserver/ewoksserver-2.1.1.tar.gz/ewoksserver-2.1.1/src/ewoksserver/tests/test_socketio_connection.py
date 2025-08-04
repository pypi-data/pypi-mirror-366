import time


def test_socketio_connection_local(local_exec_client):
    _, sclient = local_exec_client
    _test_socketio_connection(sclient)


def test_socketio_connection_celery(celery_exec_client):
    _, sclient = celery_exec_client
    _test_socketio_connection(sclient)


def _test_socketio_connection(sclient):
    assert sclient.is_running()
    _assert_eventloop_is_running(True, sclient)
    sclient.disconnect()
    _assert_eventloop_is_running(False, sclient)
    sclient.connect()
    _assert_eventloop_is_running(True, sclient)


def _assert_eventloop_is_running(running, sclient, timeout=3):
    t0 = time.time()
    while True:
        if sclient.is_running() == running:
            return
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            raise TimeoutError
