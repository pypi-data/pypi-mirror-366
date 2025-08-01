import datetime 

def greet(name):
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time}\tit's my great pleasure to meet you\n hello {name}!")

if __name__ == "__main__":
    greet("user")