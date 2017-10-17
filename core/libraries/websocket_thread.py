import threading

class ConnectThread (threading.Thread):

   def __init__(self, ws):
      threading.Thread.__init__(self)
      self.wsinstance=ws

   def run(self):
      self.wsinstance.connect()
      