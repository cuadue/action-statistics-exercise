import threading
import json
from collections import defaultdict

class _Record:
    '''Private helper class'''
    total = 0
    count = 0

    @property
    def average(self):
        if not self.count:
            return 0
        return self.total / self.count

    def addTime(self, time):
        self.total += float(time)
        self.count += 1

class ActionStatistics:
    '''Maintains the average time for actions'''
    def __init__(self):
        self.mutex = threading.Lock()
        self.records = defaultdict(_Record)

    def addAction(self, jsonString):
        '''
        Accepts a JSON serialized object and maintains an average time for each
        action.  This function is thread safe. The JSON object needs to have two
        entries (unknown keys are ignored):

        - `action`, the value of which must be a string, and
        - `time`, the value of which must be a number

        Example inputs:

        - `{"action": "jump", "time": 100}`
        - `{"action": "run", "time": 75}`
        - `{"action": "jump", "time": 200}`

        Exceptions:

        - `TypeError` if:
            - the input is not string-like, or
            - the type of the values do not match the schema
        - `json.decoder.JSONDecodeError` for invalid JSON 
        - `KeyError` if the input does not contain the required keys
        - `ValueError` if the value of time cannot be converted to a number

        '''
        obj = json.loads(jsonString)
        action = obj['action']
        time = obj['time']
        if not isinstance(action, str):
            raise TypeError(
                'The type of action must be string-like, not %s' % type(action))
        with self.mutex:
            self.records[action].addTime(time)

    def getStats(self):
        '''
        Returns a JSON serialized array summarizing the statistics for each
        action recorded by`addAction`. This function is thread safe. Each item
        in the array is an object having two entries:

        - `action`, the value of which is a string, and
        - `avg`, the mean average of the `time` for that action

        Example output:

        [
            {"action": "jump", "avg": 150},
            {"action": "run", "avg": 75}
        ]
        '''
        result = []
        with self.mutex:
            for action, record in self.records.items():
                result.append(dict(action=action, avg=record.average))
        return json.dumps(result)
