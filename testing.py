import datetime

matchTime = 3214

if matchTime >= 3600:
   time = "01:"
else:
   time = ""


time += datetime.datetime.fromtimestamp(matchTime).strftime('%M:%S')


print(time)