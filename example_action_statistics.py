from action_statistics import ActionStatistics

actionStats = ActionStatistics()
actionStats.addAction('{"action":"jump", "time":100}')
actionStats.addAction('{"action":"run", "time":75}')
actionStats.addAction('{"action":"jump", "time":200}')
print(actionStats.getStats())
