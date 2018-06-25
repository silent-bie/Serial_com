print("this is a user code test!")
get_times=0
clean()
while True:
	get=read()
	if get:
		get=deal_list(get,chr)
		get=list_to_str(get)
		log(get)	
		send_string(get)
		get_times+=1
		progress(get_times)
		if get_times==100:
			break;
		
