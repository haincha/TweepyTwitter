#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from tweepy import *
from tweepy.utils import *
from tweepy.streaming import *
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import sqlite3
import webbrowser

auth = OAuthHandler('7EgFN2y086sNd2QbLZ9HrQ', 'w5LGbUC75GDILhjz0DNXgC712DgxE0ccr3UJ3yIX18')
conn = sqlite3.connect("keys.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS keys (key,secret)")
c.execute("SELECT key FROM keys")
key = c.fetchone()
c.execute("SELECT secret FROM keys")
secret = c.fetchone()
conn.close
force = False
if(key != None):
	auth.set_access_token(key[0], secret[0])
	api = API(auth)
else:
	force = True

class Twitter(QDialog):
	def __init__(self, parent=None):
		super(Twitter, self).__init__(parent)
		if(force == True):
			self.createSignin()
			# Create widgets
			self.mainLayout = QVBoxLayout()
			self.mainLayout.addWidget(self.signin)
			self.setLayout(self.mainLayout)

		else:
			self.createTimeline()
			# Create widgets
			self.mainLayout = QVBoxLayout()
			self.mainLayout.addWidget(self.timeline)
			self.setLayout(self.mainLayout)
	
	def createSignin(self):
		self.signin = QGroupBox()
		self.setWindowTitle("Twitter")
		layout = QGridLayout()
		self.label1 = QLabel("Get Access Code from Twitter")
		self.goto = QPushButton("Go to Twitter")
		self.label2 = QLabel("Enter Twitter Auth Code")
		self.edit = QLineEdit("")
		self.button = QPushButton("Submit")        
		# Create layout and add widgets
		layout.addWidget(self.label1)
		layout.addWidget(self.goto)
		layout.addWidget(self.label2)
		layout.addWidget(self.edit)
		layout.addWidget(self.button)
		# Set dialog layout
		self.signin.setLayout(layout)
		# Add button signal to auth slot
		self.goto.clicked.connect(self.twitterweb)
		self.button.clicked.connect(self.authorize)
	
	def createTimeline(self):
		self.timeline = QGroupBox()
		# Create widgets
		self.setWindowTitle("Twitter")
		layout = QGridLayout()
		self.tweettext = QLineEdit("")
		self.tweetbutton = QPushButton("Submit") 
		self.update = QPushButton("Update")
		self.stream = api.home_timeline()
		# Create layout and add widgets
		i = 0
		for tweet in self.stream:
			self.user = QLabel(tweet.user.screen_name +": ")
			self.new = QLabel(tweet.text)
			layout.addWidget(self.user, i, 0)
			layout.addWidget(self.new, i, 1)
			i += 1
		layout.addWidget(self.tweettext, i, 1)
		layout.addWidget(self.tweetbutton, i, 2)
		layout.addWidget(self.update, i, 0)
		# Set dialog layout
		self.timeline.setLayout(layout)
		# Add button signal to auth slot
		self.tweetbutton.clicked.connect(self.newtweet)
		self.update.clicked.connect(self.updateframe)
	
	def twitterweb(self):
		webbrowser.open(auth.get_authorization_url())       

	def authorize(self):
		if(force == True):
			pin = self.edit.text()
			token = auth.get_access_token(verifier=pin)
			auth.set_access_token(token.key, token.secret)
			global api
			api = API(auth)
			insertinfo = [(token.key, token.secret)]
			c.executemany("INSERT INTO keys VALUES (?,?)", insertinfo)
			conn.commit()
			conn.close
			while(api.verify_credentials() == False):
				#waiting
				nothing = 0
			self.signin.setParent(None)
			self.createTimeline()
			self.mainLayout.addWidget(self.timeline)
			self.setLayout(self.mainLayout)
	def newtweet(self):
		post = self.tweettext.text()
		api.update_status(post)
		self.tweettext.clear()
	def updateframe(self):
		self.timeline.setParent(None)
		self.createTimeline()
		self.mainLayout.addWidget(self.timeline)
		self.setLayout(self.mainLayout)
 
if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    mainwin = Twitter()
    mainwin.show()
    # Run the main Qt loop
    sys.exit(app.exec_())