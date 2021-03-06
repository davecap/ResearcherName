#!/usr/bin/env python

import wsgiref.handlers
import os
import datetime
import logging

from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.api import memcache

import entrez

logging.getLogger().setLevel(logging.DEBUG)

# Models

# class User(db.Model):
#     id = db.StringProperty(required=True)
#     created = db.DateTimeProperty(auto_now_add=True)
#     updated = db.DateTimeProperty(auto_now=True)
#     name = db.StringProperty(required=True)
#     profile_url = db.StringProperty(required=True)
#     picture = db.StringProperty(required=True)
#     location = db.StringProperty()
#     access_token = db.StringProperty()
#     
#     def get_location(self):
#         # TODO: look for UserProfile location data
#         pass
# 
# class UserEvent(db.Model):
#     id = db.StringProperty(required=True)
#     created = db.DateTimeProperty(auto_now_add=True)
#     updated = db.DateTimeProperty(auto_now=True)
#     friend_ids = db.StringListProperty(default=[])
#     event_id = db.StringProperty(default=None)
#     
#     # TODO: async?
#     def add_friend(self, user_id):
#         if user_id not in self.friend_ids:
#             self.friend_ids.append(user_id)
#             self.put()
#     
#     # TODO: async?
#     def remove_friend(self, user_id):
#         if user_id in self.friend_ids:
#             self.friend_ids.remove(user_id)
#             self.put()
#     
# class UserProfile(db.Expando):
#     id = db.StringProperty(required=True)
#     # latitude
#     # longitude
#     # city
#     # country
#     # postal_code
#     # interests = g.get_connections("me", "interests")
#     # music = g.get_connections("me", "music")
#     # books = g.get_connections("me", "books")
#     # movies = g.get_connections("me", "movies")
#     # television = g.get_connections("me", "television")
#     # albums = g.get_connections("me", "albums")
#     # #likes = g.get_connections("me", "likes")
# 
# # Controllers
# 
# class BaseHandler(webapp.RequestHandler):
#     @property
#     def current_event(self):
#         if not self.current_user:
#             return None
#         elif not hasattr(self, "_current_event"):
#             user_event = UserEvent.get_by_key_name(self.current_user.id)
#             if not user_event:
#                 # create a new event for a new user
#                 user_event = UserEvent(key_name=self.current_user.id,
#                                         id=self.current_user.id)
#                 user_event.put()
#             # TODO: expire old user events?
#             self._current_event = user_event             
#         return self._current_event
#     
#     @property
#     def current_user(self):
#         if not hasattr(self, "_current_user"):
#             self._current_user = None
#             cookie = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APPLICATION_ID, FACEBOOK_SECRET_KEY)
#             if cookie:
#                 # Store a local instance of the user data so we don't need
#                 # a round-trip to Facebook on every request
#                 user = User.get_by_key_name(cookie["uid"])
#                 if not user:
#                     graph = facebook.GraphAPI(cookie["access_token"])
#                     profile = graph.get_object("me", fields='id,name,link,picture,location')
#                     
#                     try:
#                         # FB locations are in 'City, State' format
#                         location = profile["location"]["name"]
#                     except:
#                         location = None
#                     
#                     user = User(key_name=str(profile["id"]),
#                                 id=str(profile["id"]),
#                                 name=profile["name"],
#                                 profile_url=profile["link"],
#                                 picture=profile["picture"],
#                                 location=location,
#                                 access_token=cookie["access_token"])
#                     user.put()
#                 elif user.access_token != cookie["access_token"]:
#                     user.access_token = cookie["access_token"]
#                     user.put()
#                 self._current_user = user
#         return self._current_user
# 
class IndexHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), "templates/index.html")
        args = dict()
        self.response.out.write(template.render(path, args))

class AjaxHandler(webapp.RequestHandler):
    """ Base AJAX request handler, requires logged-in user and AJAX request header """
    def process(self):
        raise NotImplementedError()
    
    def get(self):
        # must be logged in
        #if self.current_user is None:
        #    return self.error(403)
        # must be ajax request
        #if 'X-Requested-With' not in self.request.headers.keys() or self.request.headers['X-Requested-With'] != 'XMLHttpRequest':
        #    return self.error(403)
        self.process()

class AjaxSearchPubmedHandler(AjaxHandler):
    def process(self):
        query = self.request.get("q")
        if not query:
            self.response.out.write('')
        else:
            handle = entrez.esearch(db="pubmed", term=query)
            record = entrez.read(handle)
            handle = entrez.efetch(db="pubmed", id=record["IdList"], rettype="xml")
            print handle.read()
            #record = entrez.read(handle)
            #self.response.out.write(record)
            #self.response.out.write(handle.read())
            #self.response.out.write(simplejson.dumps({ "pmids": record["IdList"] }))

# class AjaxNextEventHandler(AjaxHandler):
#     def get_user_info(self):
#         # TODO: get and set UserProfile for the current_user and friends in the friend list
#         # TODO: get user location
#         # TODO: look up events!
#         
#         # # get or create the user profile by this ID
#         # f_user_profile = UserProfile.get_by_key_name(f_id)
#         # if f_user_profile is None:
#         #     # TODO
#         #     pass
#         
#         g = facebook.GraphAPI(self.current_user.access_token)
#         interests = g.get_connections("me", "interests")
#         music = g.get_connections("me", "music")
#         books = g.get_connections("me", "books")
#         movies = g.get_connections("me", "movies")
#         television = g.get_connections("me", "television")
#         albums = g.get_connections("me", "albums")
#         #likes = g.get_connections("me", "likes")
#         return '%s<br />%s<br />%s<br />%s<br />%s<br />%s<br />' % (interests, music, books, movies, albums, television)
#         
#     def process(self):
#         # get an event for the user and return it as an HTML partial
#         t = str(datetime.datetime.now())
#         info = self.get_user_info()
#         self.response.out.write('<b>Next Event for user %s</b><br />%s<br />%s' % (self.current_user.name, t, info))
# 
# class AjaxFriendListHandler(AjaxHandler):
#     def process(self):
#         friends = facebook.GraphAPI(self.current_user.access_token).get_connections("me", "friends")
#         if friends and 'data' in friends:
#             res = simplejson.dumps([ { 'value':f['id'], 'label':f['name'] } for f in friends['data'] ])
#             self.response.out.write(res)
# 
# class AjaxRemoveFriendHandler(AjaxHandler):
#     def process(self):
#         f_id = self.request.get("id")
#         self.current_event.remove_friend(f_id)
#         self.response.out.write(simplejson.dumps({ "id": f_id }))
#                     
# class AjaxAddFriendHandler(AjaxHandler):
#     def process(self):
#         f_id = self.request.get("id")
#         
#         # get the friend's profile
#         friend = User.get_by_key_name(f_id)
#         if friend is None:
#             profile = facebook.GraphAPI(self.current_user.access_token).get_object(f_id, fields='id,name,link,picture')
#             
#             friend = User(key_name=str(profile["id"]),
#                         id=str(profile["id"]),
#                         name=profile["name"],
#                         profile_url=profile["link"],
#                         picture=profile["picture"])
#             friend.put()
#         
#         self.current_event.add_friend(f_id)
#         self.response.out.write(simplejson.dumps({ "name": friend.name, "picture": friend.picture, "id": friend.id }))
#        
# class AjaxSetLocationHandler(AjaxHandler):
#     def process(self):
#         # TODO process GET params: latitude, longitude, city, country, postal_code
#         # set in UserProfile
#         self.response.out.write(simplejson.dumps({ }))

def main():
    application = webapp.WSGIApplication([
                        ('/', IndexHandler),
                        ('/ajax/search', AjaxSearchPubmedHandler),
                    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
