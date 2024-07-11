from bot import client
from threading import Thread
from website import run_website

web = Thread(target=run_website, args=(client,))
web.start()
print("WEB | started successfully")
client.run()
web.join()
