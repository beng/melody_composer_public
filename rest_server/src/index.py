"""
@author   Ben G

this is a genetic algorithm that composes melodies.
"""

import music21

import json

import web

#import models.midi_info as mim
import helper.consts as consts
import helper.utility as utility
import ga
import model

urls = (
    '/', 'Index',
    '/save_midi/(.+)/(.+)', 'SaveMidi',
    '/load_traits/(.+)/(.+)', 'LoadTraits',
    '/markov/(.+)/(.+)/(.+)/(.+)', 'Markov',
    '/ga/spawn/(.+)/(.+)/(.+)/(.+)', 'SpawnPopulation',
    '/ga/fitness', 'Fitness',
    '/interactive', 'Interactive',
    '/mongo', 'MongoTesting',)

render = web.template.render('templates/', base='layout')
title = "Melody Composer"

########################################################
# Test
########################################################
class Index():
    def GET(self):
        return "Hello"

########################################################
# Mongo Testing
########################################################
class MongoTesting():
    def GET(self):
        trait = 'note'
        notes = []
        
        for item in model.music_find_trait('Vivaldi', 'winter_allegro',trait):
            notes.append(item[trait])
        
        notes = ' '.join(notes)

        population = Markov().GET(5000, 5, 'Vivaldi', 'winter_allegro')

        print population

########################################################
# Interactive Testing
########################################################
class Interactive():
    def GET(self):
        artist = 'vivaldi'
        song = 'winter_allegro'
        data = Markov().GET(100, 5, artist, song)
        data = data[0].split()
        return render.interactive(title, data)


########################################################
# Return Population of X individuals and Y traits each
########################################################
class SpawnPopulation():
    """Use Markov chain to spawn the initial population for the
    requested artist, song, size, and nodes"""

    def GET(self, artist, song, num_indi, num_traits):
        """Experiment with using the same Markov chain pool on the entire
    initial population VS regenerating a markov chain for each individual

    Also experiment with the nodes and size values with above"""

        num_indi = int(num_indi)
        num_traits = int(num_traits)
        population = Markov().GET(5000, 10, artist, song)
        min = 0
        max = len(population)

        for ni in range(num_indi):
            current_gen = 0            
            for nt in range(num_traits):
                start, stop = utility.random_sampling(min, max, num_traits)
                trait = {
                    'generation': current_gen,
                    'indi_id': ni,
                    'trait_id': nt,
                    'artist': artist,
                    'song': song,
                    'note': population[start:stop]}
                model.pop_save_population(trait)
            current_gen += 1

########################################################
# Save MIDI to Server
########################################################
class SaveMidi():
    def GET(self, artist, song):
        """Export MIDI file to specified filetype
        Checks to see if the requested MIDI file exists
        on my server. If it does, extracts the requested
        traits from it using the music21 library.
        @TODO If it doesn't I need to return an error
        """

        # convert to stream
        artist = artist.capitalize()
        fp = utility.to_path(consts.midi_dir, artist, song, 'mid')
        stream = utility.extract_corpus(fp)

        # extract notes, returns generator
        trait_dict = utility.extract_traits(stream, [music21.note.Note])

        # add notes to music collection in mongodb
        for items in trait_dict:
            items.update({'artist': artist, 'song': song})
            model.music_save_traits(items)

        web.ctx.status = '200 OK'
        return 'explicit 200'

########################################################
# Generate Markov Chain
########################################################
class Markov():
    """Return json of Markov chain"""

    def GET(self, size, nodes, artist, song):
        """Return a Markov chain for the specified artist and song"""

        #model.music_find()
        # generate a single individual (genome)
        # mc_pop = ' '.join(utility.dict_to_string(trait) for trait in data)
        '''
        artist = artist.capitalize()
        extension = 'json'
        filepath = utility.to_path(consts.pitch_dir, artist, song, extension)

        # create string containing only the value of the traits
        data = utility.load_file(filepath, extension)
        mc_pop = ' '.join(utility.dict_to_string(trait) for trait in data)
        '''

        notes = []
        trait = 'note'
        for item in model.music_find_trait(artist, song, trait):
            notes.append(item[trait])
        notes = ' '.join(notes)

        pool = ga.genome(notes, size=int(size), nodes=int(nodes))

        # convert to list
        pool = pool[0].split()

        # remove first and last element because they might be
        # corrupt
        pool.pop(0)   # first
        pool.pop()    # last
        
        return pool

########################################################
# Run Web Server
########################################################
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()