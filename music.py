from __future__ import with_statement
import sys
from markov import markov
import random
import math
from music21 import *
"""
initial population
    -supply either artist name or 2 songs 
    -select subset of pitches from each song OR if artist supplied, take 2 random subsets of pitch file of length num_traits
        -EXPERIMENT WITH -- when getting pitches, do i want to select a subset of same pitches (e.g. [C# C# C# C# C#]or do i want diversity?) 
    -take euclidean distance between 2 subsets -- this becomes the fitness comparator
    -build markov model with the traits selected above

fitness
    -sum([euclidean distance individual and parent_1], [euclidean distance between individual and parent_2]    
    -winners of round =  30%similar, 30%X middle, and 60% different children depending on desired number of children.this will be useful to ensure that the population doesnt converge 
    -use case:
        the 2 songs supplied on the cmd line are "billy joel - we didnt start the fire" and "jay-z - hard knock life". 
        take the euclidean distance between those 2 songs and use that to compare against the SUM of the euclidean distance between the child and billy joel, and the euclidean distance between the child and jay-z.     

implement opts, args = getopt.getopt to allow flags and args 
	e.g. python music.py -a <artist> -s1 <song_1> -s2 <song_2>

TODO: modify markov chain to take in a list of pitches instead of a file -- [ [melody_1], ... , [melody_n] ]

TODO: if size of song_file, i.e. number of pitches in the file is LESS THAN NUM_TRAITS then set NUM_TRAITS EQUAL to the total number of pitches in the file (e.g. big poppa has 50 pitches, NUM_TRAITS = 100, set NUM_TRAITS=50)
"""

PITCH_DIR = './pitches/pitches_'
NUM_TRAITS = 4
POP_SIZE = 2
NUM_GEN = 5
DURATION = ['whole', 'half', 'quarter', 'eighth', '16th']

def euclid_distance(song1, song2):
	# len(song_1) == len(song_2)
	val = 0
	for i in range(len(song1)):
		val += math.sqrt((pitch.Pitch(song1[i]).midi - int(pitch.Pitch(song2[i]).midi)) ** 2)
	#return [math.sqrt((pitch.Pitch(song1[i]).midi - pitch.Pitch(song2[i]).midi) ** 2) for i in range(len(song1))]
	return val

def mutate():
	# use markov.get_next_pitches() to generate new pitches for individual
	pass

def subset(song):
	nt = NUM_TRAITS
	if len(song) < nt:
		nt = len(song)
	start = random.randint(0, ((len(song) - nt) + 1))
	end = start + nt
	return song[start:end]

def parse_songs(songs):
	'''
	supply list of files --
	for each file,
		read in the pitches 
		store in influencer list
	'''
	data = []
	for song in songs:
		with open("./midi_info/"+song,"r") as f: 
			pitches = [elem for elem in f.read().split('\n') if elem] 
			for pitch in pitches: 
				data.append(pitch.split())
	return data

def individual(m):
	# returns tuple -- ([pitches], duration)
	return (m.generate_music(NUM_TRAITS), random.choice(DURATION))

def population(m):
	return [individual(m) for i in range(POP_SIZE)]

def run(influencers):
	data = parse_songs(influencers)		
	subset_data = []
	for d in data:
		subset_data += [subset(d)]
	ed = euclid_distance(subset_data[0], subset_data[1])
	print 'subset data :: ', subset_data,'\n'
	print 'ED :: ', ed
	pitch_data = [item for sublist in subset_data for item in sublist]
	print 'pitch data :: ', pitch_data, '\n'
	m = markov(pitch_data)
	markov_music = m.generate_music(NUM_TRAITS)
	print 'm MUSIC : : ', markov_music,'\n'


# KEEP TO ONLY 2 SONGS FOR NOW -- EUCLID DISTANCE ONLY MADE TO WORK FOR 2 SONGS !!!
influencers = ['I_Aint_Mad_Atcha.txt', 'Nothing_To_Lose.txt']
run(influencers)
