import cPickle as pickle

try:
    subreddits = pickle.load(open('subreddits.pickle', 'r'))
except:
    raise Exception("Unable to load subreddits.pickle - perhaps you have yet to run build_subreddits.py?")
