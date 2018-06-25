log("this is a user code test!")
get_times=0
while True:
	clean()
	clear()
	send_string("win_list.")
	delay(2)
	get=read()
	if get is None:
		log("can't get com")
		break
	
	# if get:
		# get=deal_list(get,chr)
		# get=list_to_str(get)
		# 
		# log(get)	
		# send_string(get)
		# get_times+=1
		# progress(get_times)
		# if get_times==100:
			# break;
		
