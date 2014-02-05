#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
module: heartthrob.py
author: Zach Lamberty
created: 2014-02-02

Description:
    A python implementation of the heartthrob game

Usage:
    python heartthrob.py

"""

import argparse as _argparse
import csv as _csv
import random as _random
import os as _os
import urllib2 as _urllib2

from collections import defaultdict as _defaultdict

#-----------------------#
#   Module Constants    #
#-----------------------#
_HT_INTRO_TEXT = ['\nThis young stud muffin\'s name is {}',
                  '\nIs that a banana in {}\'s pocket or... a knife?!',
                  '\n{} just entered your bone-zone',
                  '\nLook out ladies, {} is about to make ya pants sop']
_HT_INTRO_TEXT = [el + '\n\tPic: {}' for el in _HT_INTRO_TEXT]
_HT_OUTRO_TEXT = ['S T U D (emphasis on the S, T, and D)\n',
                  'Jackpot.\n',
                  'Oooooooooooooooooo gurl damn\n']
USED, UNUSED = 0, 1

#-----------------------#
#   Heartthrob Classes  #
#-----------------------#

class NoUniqueValue(Exception):
    """docstring for NoUniqueValue"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HeartthrobData(object):
    """ A data container for the Heartthrob game. Must have the following as
        public member functions:

        htd.nameAndPic()
        htd.fact()
        htd.ambition()
        htd.quirk()
        htd.turnoff()

        which, ideally, will be a random (but unique) member of an internal
        list of such properties.

    """

    def __init__(self, csvName=None, googDrive=None, url=None):
        self.d = _defaultdict(lambda: _defaultdict(list))

        if csvName:
            self._load_csv(csvName)
        elif googDrive:
            self._load_googDrive(googDrive)
        elif url:
            self._load_url(url)
        else:
            raise ValueError("Ba-durt")

    # Data loading
    def _load_csv(self, csvName):
        """ Load the csv name into an object from which we can randomly pick our
            ht data. We require a superset of the column headings:

                name
                pic url
                fact
                ambition
                quirk
                turn-off

        """
        with open(csvName, 'rb') as fIn:
            data = list(_csv.DictReader(fIn))

        trans = {k.lower(): k for k in data[0]}

        self.d['nameAndPic'][UNUSED] = [(d[trans['name']], d[trans['pic url']])
                                        for d in data if d[trans['name']]]
        self.d['fact'][UNUSED] = [d[trans['fact']] for d in data
                                  if d[trans['fact']]]
        self.d['ambition'][UNUSED] = [d[trans['ambition']] for d in data
                                      if d[trans['ambition']]]
        self.d['quirk'][UNUSED] = [d[trans['quirk']] for d in data
                                   if d[trans['quirk']]]
        self.d['turn-off'][UNUSED] = [d[trans['turn-off']] for d in data
                                      if d[trans['turn-off']]]

    def _load_googDrive(self, googDrive):
        """ Go get the googDrive, save it to the local directory as a csv, pass it to
            _load_csv, and delete that shit.

            Check out:
                https://developers.google.com/drive/web/manage-downloads
                https://developers.google.com/drive/web/quickstart/quickstart-python

        """
        pass

    def _load_url(self, url):
        """ ditto with the above """
        fIn = _urllib2.urlopen(url)
        with open('./tmp.csv', 'wb') as fOut:
            fOut.write(fIn.read())
        self._load_csv('./tmp.csv')
        _os.remove('./tmp.csv')

    # Random data generating functions
    def nameAndPic(self):
        return self._random_choice('nameAndPic')

    def fact(self):
        return self._random_choice('fact')

    def ambition(self):
        return self._random_choice('ambition')

    def quirk(self):
        return self._random_choice('quirk')

    def turnoff(self):
        return self._random_choice('turn-off')

    def _random_choice(self, key):
        try:
            i = _random.randint(0, len(self.d[key][UNUSED]) - 1)
            x = self.d[key][UNUSED].pop(i)
            self.d[key][USED].append(x)
            return x
        except Exception as err:
            print 'ERROR: {}'.format(err.message)
            raise NoUniqueValue('woooooooo crap no more {} values'.format(key))

    # Refreshing used data
    def refresh_choices(self, key):
        self.d[key][UNUSED] = self.d[key].pop(USED)


class HeartthrobGame(object):
    """ The HeartthrobGame object will be the primary user interface for the
        automated heartthrob game

    """
    def __init__(self, htd):
        """ The game object takes a HeartthrobData object to be used for
            creating heartthrobs

        """
        print "Welcome to HeartThrob!"
        subTexts = ["What makes *your* part throb?",
                    "Happy throbbing!",
                    "Throbbin' hood: men in tights"]
        print _random.choice(subTexts)
        self.htd = htd

    def __del__(self):
        print "You just got THROBBED."

    # Game play
    def tourney_play(self, rounds=2):
        """ Start the game! """
        hts = [self._make_heartthrob() for i in range(3**rounds)]
        while len(hts) > 1:
            print "\n\n**** NEW ROUND ****\n"
            hts = self._tourney_winners(hts)
        return hts[0]

    def _tourney_winners(self, hts):
        """ First, make sure that this list is a power of 3 -- if not, let it
            fail. Second, break it up into minigames of three people. The
            winners of these games go on to the next round

        """
        if not len(hts) % 3 == 0:
            err = "The length of the heartthrob list is not a power of 3"
            raise ValueError(err)
        return [self._mini_game(hts[i * 3: (i + 1) * 3])
                for i in range(len(hts) / 3)]

    def forever_play(self):
        """ Start the game, but never quit! """
        while True:
            try:
                hts = [self._make_heartthrob() for i in range(3)]
                self._mini_game(hts)
            except:
                break

    # Minigame
    def _mini_game(self, htsList):
        """ List out the contestants in whatever dramatic way you want, then
            have some way for determining a victor of them, and return that ht

        """
        for hts in htsList:
            self._present_heartthrob(hts)

        return self._get_winner(htsList)

    def _present_heartthrob(self, ht):
        """ "dramatically" present a HeartThrob """
        raw_input(_random.choice(_HT_INTRO_TEXT).format(*ht['nameAndPic']))
        raw_input("\tFact: {}".format(ht['fact']))
        raw_input("\tAmbition: {}".format(ht['ambition']))
        raw_input("\tQuirk: {}".format(ht['quirk']))
        raw_input("\tTurn-off: {}".format(ht['turnoff']))
        raw_input(_random.choice(_HT_OUTRO_TEXT))

    def _get_winner(self, htsList):
        """ Find some way of determining the winner. For now, just a raw input
            decision

        """
        opts = ["{} - {}".format(i + 1, el['nameAndPic'][0])
                for (i, el) in enumerate(htsList)]
        s = "\n\t".join(["So who makes ya heart throb?"] + opts + ['\nWho ya gon do???\t'])
        pick = raw_input(s)
        try:
            return htsList[int(pick) - 1]
        except Exception as e:
            print "try again!\n"
            return self._get_winner(htsList)

    # heartthrobs
    def _make_heartthrob(self):
        try:
            return {'nameAndPic': self.htd.nameAndPic(),
                    'fact': self.htd.fact(),
                    'ambition': self.htd.ambition(),
                    'quirk': self.htd.quirk(),
                    'turnoff': self.htd.turnoff()}
        except NoUniqueValue as e:
            print "We ran out of unique values!"



#-------------------------------#
#   Main routine                #
#-------------------------------#

def _parse_args():
    """Take a log file from the commmand line

    """
    parser = _argparse.ArgumentParser()
    parser.add_argument("-x", "--xample", help="An Example", action='store_true')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = _parse_args()

    main()
