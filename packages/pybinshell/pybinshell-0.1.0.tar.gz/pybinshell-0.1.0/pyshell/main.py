import os

def shell():
	while True:
		uin = input("$ ")
		if uin == "quit":
			exit()
		os.system(uin)

