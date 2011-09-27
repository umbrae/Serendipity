import os
import cPickle as pickle

cwd = os.path.realpath(os.path.dirname(__file__))

try:
    subreddits = pickle.load(open(os.path.join(cwd, 'subreddits.pickle'), 'r'))
except:
    raise Exception("Unable to load subreddits.pickle - perhaps you have yet to run build_subreddits.py?")
