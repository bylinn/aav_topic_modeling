#
# a script for getting a summary of stable topics from a "_review.txt" file.
#
# usage: >>$ python summarize_stable.py <RELATIVE PATH> <INT>
#
# <RELATIVE PATH> is the path to the txt file containing groups of stabilized 
# topics and the top n words for each model in each.
# <INT> is the number of top words to return in the summary.
#
# @csr18
# 

import sys, os

    
def collapse(*tuples):
    '''
    collapses a list of pairs of multipliers and lists of tokens
    to return a dictionary of tokens and their mean rank
    '''
    tokens = {}
    for t in tuples:
        topic_id, multiplier, words = t # ignore topic id here
        for i in range(len(words)):
            rank = (i + 1) * float(multiplier)
            tokens[words[i]] = tokens.get(words[i], []) + [rank]
    for token in tokens:
        tokens[token] = float(sum(tokens[token])) / len(tokens[token])
    return tokens

    
def process(path, n):

    topics = {}
    tuples = []
    
    with open(path, 'rb') as f_in:
        for line in f_in:
            if line.startswith('Stable'):
                stable_id = int(line[line.rfind('-') + 1:])
                tuples = []
            elif len(line.strip()) == 0:
                stable_terms = collapse(*tuples) 
                original_topic_ids = '\t'.join([t[0] for t in tuples])
                top_n = sorted(stable_terms.items(), key=lambda x: x[1])[:n]
                topics['\t'.join(map(str, [stable_id, original_topic_ids]))] = [token[0] for token in top_n]
            else:
                line = line.split()
                tuples.append((line[0].strip(":"), line[1], line[2:]))
    return topics


def write_out(path, dictionary):
    with open(path, 'wb') as f_out:
        for key in sorted(dictionary.keys(), key = lambda k: int(k[:k.find('\t')])):
            line = '{}\t'.format(key)
            line += ' '.join(dictionary[key])
            f_out.write(line + '\r\n')
                
                
if __name__ == '__main__':

    msg = 'usage: >>$ python summarize_stable.py <RELATIVE PATH> <INT>'
    try: 
        filepath = os.path.abspath(sys.argv[1])
        pivot = filepath.rfind('.')
        outpath = filepath[:pivot] + '-summary' + filepath[pivot:]
        if not os.path.isfile(filepath):
            msg += '\n(Arg1 must be an existing file.  Supplied: {})'.format(filepath)
            raise IOError(msg)
        top = sys.argv[2] 
        try: 
            top = int(top)
        except ValueError:
            msg += '\n(Arg2 must be an int.  Supplied: {})'.format(top)
            raise IOError(msg)
    except IndexError:
        raise IOError(msg)
        
    topics = process(filepath, top)
    write_out(outpath, topics)
    