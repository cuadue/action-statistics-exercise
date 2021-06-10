import threading
import json

from action_statistics import ActionStatistics

def assert_average_equals(statsString, action, avg):
    arr = json.loads(statsString)
    for obj in arr:
        if obj['action'] == action:
            assert obj['avg'] == avg
            print("PASS: Action '%s' -> %f" % (action, avg))
            return
    raise KeyError(action)

def test_basic():
    dut = ActionStatistics()
    dut.addAction('{"action":"jump", "time":100}')
    dut.addAction('{"action":"run", "time":75}')
    dut.addAction('{"action":"jump", "time":200}')

    stats = dut.getStats()
    assert json.loads(stats) == json.loads('''
    [
        {"action":"jump", "avg":150},
        {"action":"run", "avg":75}
    ]
    ''')
    print("PASS basic test")

def assert_throws(exc_type, func):
    try:
        func()
    except Exception as e:
        assert isinstance(e, exc_type)
        return

    assert False, 'Did not throw exception of type %s' % exc_type

def test_bad_input():
    dut = ActionStatistics()
    assert_throws(json.decoder.JSONDecodeError, lambda: dut.addAction('{'))
    assert_throws(KeyError, lambda: dut.addAction('{}'))
    assert_throws(TypeError, lambda: dut.addAction('{"action": 5, "time": 5}'))
    assert_throws(ValueError, lambda: dut.addAction('{"action": "jump", "time": "abc"}'))

    print("PASS bad input test")
    

def test_concurrent():
    '''
    This test checks that concurrency bugs don't cause dropped function calls.
    An equal number of +1 and -1 average out to zero.
    '''
    dut = ActionStatistics()
    def work(action, time):
        for i in range(1024):
            dut.addAction('{"action":"%s", "time": %d}' % (action, time))
            dut.getStats()

    threads = []
    for i in range(64):
        time = 17 if i % 2 == 0 else 23
        threads.append(threading.Thread(target=work, args=('jump', time)))

    for i in range(64):
        threads.append(threading.Thread(target=work, args=('run', 1234)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    stats = dut.getStats()
    assert json.loads(stats) == json.loads('''
    [
        {"action": "jump", "avg": 20},
        {"action": "run", "avg": 1234}
    ]
    ''')
    print("PASS concurrency test")

if __name__ == '__main__':
    test_basic()
    test_bad_input()
    test_concurrent()
