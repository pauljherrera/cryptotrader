# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:27:21 2017

@author: Paúl Herrera
"""

class PubSubPattern():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribers = []

    def publish(self, message):
        for s in self.subscribers:
            s.receive(message)
            
    def receive(self, message):
        raise NotImplementedError
    
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    
    
class Subscriber:
    def __init__(self, name):
        self.name = name
    def update(self, message):
        # start new Thread in here to handle any task
        print('\n\n {} got message "{}"'.format(self.name, message))
        
class Publisher:
    def __init__(self, events):
        # maps event names to subscribers
        # str -> dict
        self.events = { event : dict() for event in events }
                          
    def get_subscribers(self, event):
        return self.events[event]

    def get_events(self):
        return self.events
                
    def register(self, event, channel):
        self.get_subscribers(event)[channel] = channel.update

    def unregister(self, event, channel):
        del self.get_subscribers(event)[channel]

    def dispatch(self, event, message):
        for subscriber, callback in self.get_subscribers(event).items():
            callback(message)           
    
