import datetime

def getClass(scan_time_str):
	datetime_object = datetime.datetime.strptime(scan_time_str, '%H:%M')
	scan_time = datetime_object.time()
	
	class1_start = datetime.time(19, 0)
	class1_end = datetime.time(21, 0)
	class1 = "class1"
	other = "class2"
	
	if (within_range(class1_start, class1_end, scan_time)):
		return class1
	else:
		return other
		
def within_range(start, end, x):
	if start <= end:
		return start <= x <= end
	else:
		return start <= x or x <= end	
		
'''

def getClass(scan_time_str):
	scan_time_str = "2023-1-1 "+scan_time_str
	datetime_object = datetime.strptime(scan_time_str, '%Y-%m-%d %H:%M')
	scan_time = datetime_object
	
	class1_start = datetime(2003, 1, 1, 19, 0)
	class1_end = datetime(2003, 1, 1, 21, 0)
	class1 = "class1"
	
	if ((scan_time >= class1_start) and (scan_time < class1_end)):
		return class1
	else:
		return "class2" 
'''
