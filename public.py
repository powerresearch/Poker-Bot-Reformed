import datetime

def is_recent_file(file_name):
    date = datetime.datetime.now().strftime('%Y,%m,%d,%H,%m,%s')
    date = date.split(',')
    date0 = date[0]+date[1]+date[2]
    date1 = str(int(date0)-1)
    valid_date = list()
    valid_date.append(date0)
    valid_date.append(date1)
    if date[2] == '01':
        valid_date += [str(int(date[0]+date[1])-1)+str(i) for i in xrange(28, 32)]
    if not file_name[2:10] in valid_date:
        return False
    else:
        return True
