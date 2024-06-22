from bot import client
from threading import Thread
from website import run_website

Thread(target=run_website, args=(client,)).start()
client.run()
