import datetime

print(datetime.datetime.strptime('11/11/06', '%d/%m/%y'))
print(datetime.datetime.now() < datetime.datetime.strptime('11/11/21', '%d/%m/%y'))