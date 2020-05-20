#-------------------------------------------------------------------------------
# Name:        Simple Explore
# Purpose:     This allows you transfer all songs from one playlist to another, as long as it isnt a liked song,
#              The aim was to do this to the changing spotify ones, to help you find new songs
#
# Author:      Llione684
#
# Created:     14/05/2020
# Copyright:   (c) Llione684 2020
# Licence:     <GNUGPLv3>
#-------------------------------------------------------------------------------

import spotipy
import time
import tkinter
from tkinter import ttk
import os




class addPlaylistScreen(tkinter.Frame):
    def __init__(self, parent, *args, **kargs):
        tkinter.Frame.__init__(self, parent, *args, **kargs)
        self.parent = parent
        self.nameLabel = tkinter.Label(self, text="Playlist name:")
        self.uriLabel = tkinter.Label(self, text="Spotify uri:")
        self.nameEntry = tkinter.Entry(self)
        self.uriEntry = tkinter.Entry(self)
        self.submitButton = tkinter.Button(self, text="Submit", command=self.addPlaylistScreenButton)

        self.nameLabel.grid(row=0)
        self.nameEntry.grid(row=1)
        self.uriLabel.grid(row=2)
        self.uriEntry.grid(row=3)
        self.submitButton.grid(row=4)

    def addPlaylistScreenButton(self):
        writeToFile("config.ini", str(self.nameEntry.get())+"="+str(self.uriEntry.get()), "end")
        mainScreenPage.playlistListBox.insert("end", str(self.nameEntry.get()))
        mainScreenPage.update()
        addPage.destroy()

class settingUsernameScreen(tkinter.Frame):
    def __init__(self, parent, *args, **kargs):
        tkinter.Frame.__init__(self, parent, *args, **kargs)
        self.username = ""
        self.parent=parent
        self.entryLabel = tkinter.Label(self, text="Please enter your spotify username")
        self.usernameEntry= tkinter.Entry(self, textvariable=self.username)
        self.usernameSubmission = tkinter.Button(self, text="Connect", command = self.usernameSubmissionButton)
        self.entryLabel.grid(row=0)
        self.usernameEntry.grid(row=1)
        self.usernameSubmission.grid(row=2)

    def usernameSubmissionButton(self):
        mainScreenPage.username = self.usernameEntry.get()
        writeToFile("config.ini", "username="+mainScreenPage.username, 0)
        mainScreenPage.spUsername.configure(text = mainScreenPage.username)
        mainScreenPage.update()
        mainScreenPage.spotify = mainScreenPage.spConnect()
        usernamePage.destroy()



class mainScreen(tkinter.Frame):
    def __init__(self, parent, *args, **kargs):
        tkinter.Frame.__init__(self, parent, *args, **kargs)
        self.parent = parent
        self.username, self.dictionaryOfUrl = loadConfig()
        self.spUsernamePre = tkinter.Label(text = "Logged in as:")
        self.spUsername = tkinter.Button(text = self.username, fg = "red", command=settingUsername)
        if self.username != "":
            self.spotify = self.spConnect()
        self.spUsernamePre.grid(row = 0, column = 0)
        self.spUsername.grid(row = 0, column=1)

        self.songScroll = ttk.Scrollbar(mainPage, orient="vertical")
        self.songListBox = tkinter.Listbox(mainPage, yscrollcommand=self.songScroll.set, selectmode="BROWSE", width=50)
        self.songScroll.config(command=self.songListBox.yview)

        self.songListBox.grid(row=1, column=2)
        self.songScroll.grid(row=1, column=3)

        self.blackListButton = tkinter.Button(text="Blacklist Song")
        self.blackListButton.grid(row=2, column=2, ipadx = 20)

        self.playlistScroll = ttk.Scrollbar(mainPage, orient="vertical")
        self.playlistListBox = tkinter.Listbox(mainPage, yscrollcommand=self.playlistScroll.set, selectmode="BROWSE", width=50)
        self.playlistScroll.config(command=self.playlistListBox.yview)

        self.playlistListBox.grid(row=3, column=2)
        self.playlistScroll.grid(row=3, column=3)

        self.playlistButtonCanvas = tkinter.Canvas(mainPage)
        self.playlistButtonCanvas.grid(row=4, column=2)
        self.playlistAdd = tkinter.Button(self.playlistButtonCanvas, text="Add", command=addingPlaylist)
        self.playlistAdd.pack(side="left", ipadx=10)
        self.playlistRemove = tkinter.Button(self.playlistButtonCanvas, text="Remove", command=self.removePlaylist)
        self.playlistRemove.pack(side="right", ipadx=10)

        self.cleanPlaylistButton = tkinter.Button(mainPage, text="Clean Simple Explore", command=self.cleanPlaylistCommand)
        self.cleanPlaylistButton.grid(row=5, column=1, pady=25, ipadx=25)

        self.findSongsButton = tkinter.Button(text = "Find Songs", command=self.findSongs)
        self.findSongsButton.grid(row=0, column=2)

        for i in self.dictionaryOfUrl:
            self.playlistListBox.insert("end", str(i).split(":")[0])

        self.addedUri = []


        self.likedExploreSongsButton = tkinter.Button(text="Copy liked found songs to seperate playlist", command=self.likedExploreSongsCommand)
        self.likedExploreSongsButton.grid(row=6, column=1, pady=25)

        self.cleaningListBox = tkinter.Listbox(mainPage, yscrollcommand=self.playlistScroll.set, selectmode="BROWSE", width=50, height=5)
        self.cleaningListBox.grid(row=7, column=1, pady=20)

    def cleanPlaylistCommand(self):
        if self.spotify:
            exploreUri = self.playlistCreationCheck(self.spotify, self.username, "SimpleExplore", "All tracks Simple Explore has found")
            foundSongsExplore = self.playlistTracks(self.spotify, exploreUri)
            likedSongs = self.savedTracks(self.spotify)
            try:
                self.cleaningListBox.delete("end")
                self.cleaningListBox.update()
            except:
                pass
            insertlist = ["Deleting", "Deleting.", "Deleting..", "Deleting..."]
            counter = 0
            for song in foundSongsExplore:
                self.cleaningListBox.insert(0, insertlist[counter % 4])
                counter += 1
                self.cleaningListBox.update()
                self.cleaningListBox.delete(0)
                if song in likedSongs:
                    time.sleep(1)
                    self.spotify.user_playlist_remove_all_occurrences_of_tracks(self.username, exploreUri, [song])
            self.cleaningListBox.update()
            self.cleaningListBox.insert(0, "Deleted all liked songs")
            self.cleaningListBox.update()

    def likedExploreSongsCommand(self):
        if self.spotify:
            SELiked = self.playlistCreationCheck(self.spotify, self.username, "SE Liked", "The songs found that you like")
            SELikedTracks = self.playlistTracks(self.spotify, SELiked)
            exploreFound = self.playlistCreationCheck(self.spotify, self.username, "SimpleExplore", "All tracks Simple Explore has found")
            foundSongs = self.playlistTracks(self.spotify, exploreFound)
            likedSongs = self.savedTracks(self.spotify)
            try:
                self.cleaningListBox.delete("end")
                self.cleaningListBox.update()
            except:
                pass
            insertlist = ["Copying", "Copying.", "Copying..", "Copying..."]
            counter = 0
            for song in foundSongs:
                self.cleaningListBox.insert(0, insertlist[counter % 4])
                counter +=1
                self.cleaningListBox.update()
                self.cleaningListBox.delete(0)
                if (song not in SELikedTracks) and (song in likedSongs):
                    time.sleep(1)
                    self.spotify.user_playlist_add_tracks(self.username, SELiked, [song])
            self.cleaningListBox.update()
            self.cleaningListBox.insert(0, "Copied all songs")
            self.cleaningListBox.update()


    def spConnect(self):
        token = spotipy.util.prompt_for_user_token(self.username, "playlist-modify-private user-library-read playlist-read-private", client_id='', client_secret='', redirect_uri='')
        if token:
            sp = spotipy.Spotify(auth=token)
            self.spUsername.configure(fg="green")
        else:
            self.spUsername.configure(fg = "red")
        return sp

    def removePlaylist(self):
        selected = self.playlistListBox.curselection()
        if selected:
            self.playlistListBox.delete(selected)
            z = readLineFromFile("config.ini", 0).strip()[:7]
            if readLineFromFile("config.ini", 0).strip()[:8] == "username":
                writeToFile("config.ini", "", int(selected[0])+1)
            else:
                writeToFile("config.ini", "", int(selected[0]))

    def findSongs(self):
        username = self.username
        dictionaryOfUrl = self.dictionaryOfUrl
        reversedDictionaryOfUrl = {value:key for (key,value) in dictionaryOfUrl.items()}
        sp = self.spotify
        if sp:
            listOfUrl = dictionaryOfUrl.values()
            #Setup for playlist and track uri
            exploreUri = self.playlistCreationCheck(sp, username, "SimpleExplore", "All tracks Simple Explore has found")
            listOfExploreTracks = self.playlistTracks(sp, exploreUri)
            self.blacklistUri = self.playlistCreationCheck(sp, username, "SimpleExplore Blacklist", "Songs that keep appearing which you don't want in your explore playlist")
            listOfBlacklistTracks = self.playlistTracks(sp, self.blacklistUri)
            listOfsavedTracks = self.savedTracks(sp)

            for currentPlaylist in listOfUrl:#For each playlist in watched playlists
                self.songListBox.insert("end", "Checking: "+ reversedDictionaryOfUrl[currentPlaylist])
                self.songListBox.update()
                currentPlaylistTracks = sp.playlist_tracks(currentPlaylist)["items"] #As playlist is made of items

                for items in currentPlaylistTracks:#Sort through items, and check each track and uri
                    it = items["track"]
                    if (it["uri"] not in listOfsavedTracks) and (it["uri"] not in listOfExploreTracks) and (it["uri"] not in listOfBlacklistTracks):
                        time.sleep(1.5)
                        sp.user_playlist_add_tracks(username, exploreUri, [it["uri"]])
                        self.addedUri.append(it["uri"])
                        self.songListBox.insert("end", "Added "+ str(it["name"]) + " by "+ str(it["artists"][0]["name"]))
                        self.songListBox.update()
            self.songListBox.insert("end", "All songs have been found")
            self.songListBox.update()


    def blacklistSong(self):
        selected = self.songListBox.curselection()
        if self.spotify:
            if selected in self.addedUri:
                self.spotify.user_playlist_add_tracks(self.username, self.blacklistUri, [self.addedUri.index(selected)])
                self.songListBox.delete(selected)




    def playlistCreationCheck(self, sp, username, playlistName, playlistDesc):
    #Checks if simpleexplore exists, if not it makes it, returns uri of the playlist
        playlistNames = []
        playlistUri = {}
        returnUri = ""
        userPlaylists = sp.user_playlists(username)["items"]
        for playlist1 in userPlaylists:
            playlistNames.append(playlist1["name"])
            playlistUri[playlist1["name"]] = (playlist1["uri"])
        if playlistName in playlistNames:
            returnUri = playlistUri[playlistName]
        elif playlistName not in playlistNames:
            sp.user_playlist_create(username, playlistName, False, playlistDesc)
            returnUri = self.playlistCreationCheck(sp, username, playlistName, playlistDesc)
        return returnUri

    def playlistTracks(self, sp, exploreUri):
        #Returns uri of all songs in playlist
        returnList = []
        repeat = True
        offset1 = 0
        while repeat:
            checkingList = sp.playlist_tracks(exploreUri, offset=offset1)["items"]
            offset1 += 100
            if len(checkingList) == 100:
                for x in checkingList:
                    returnList.append(x["track"]["uri"])
            else:
                repeat = False
        return returnList

    def savedTracks(self, sp):
        #Returns uri of all songs in playlist
        returnList = []
        repeat = True
        offset1 = 0
        while repeat:
            checkingList = sp.current_user_saved_tracks(offset=offset1, limit=50)["items"]
            offset1 += 50
            if len(checkingList) == 50:
                for x in checkingList:
                    returnList.append(x["track"]["uri"])
            else:
                repeat = False
        return returnList




# This can get genre c = sp.artist('46GXASE9LHzyssNqKOInUu')
def settingUsername():
    global usernamePage
    usernamePage = tkinter.Toplevel(mainPage)
    settingUsernamePage = settingUsernameScreen(usernamePage)
    settingUsernamePage.grid()

def addingPlaylist():
    global addPage
    addPage = tkinter.Toplevel(mainPage)
    addPageFrame = addPlaylistScreen(addPage)
    addPageFrame.grid()

def readLineFromFile(name, line):
    file = open(name, "r")
    foundLines = file.readlines()
    file.close()
    return foundLines[line]

def writeToFile(name, submission, line):
    file = open(name, "r")
    foundLines = file.readlines()
    file.close()
    file = open(name, "w+")
    if not foundLines:
        file.write(submission + "\n")
    else:
        if line == "end":
            foundLines.append(submission + "\n")
        else:
            foundLines[line] = submission
        file.writelines(foundLines)
    file.close()

def loadConfig():
    if os.path.isfile("config.ini"):
        file = open("config.ini", "r")
        foundLines = file.readlines()
        if not foundLines:
            return "", {}
        else:
            dictionaryOfUrl = {}
            for i in foundLines:
                if i != "":
                    temp = i.split("=")
                    dictionaryOfUrl[temp[0].strip()] = temp[1].strip()
            try:
                username = dictionaryOfUrl["username"]
                dictionaryOfUrl.pop("username")
            except:
                username = ""

            return username, dictionaryOfUrl
    else:
        return "", {}


mainPage = tkinter.Tk()
mainPage.title("Simple Explore")
mainScreenPage = mainScreen(mainPage)
mainScreenPage.grid()
mainPage.mainloop()
