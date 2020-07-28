# written by Clay Riley 2017, following Yijun Shao et al. 2016

import os
import re
import numpy as np
from scipy.sparse import csr_matrix, dok_matrix
from tk import tk2 as tk
import itertools

np.seterr(all='raise')  # don't allow ZeroDivisionErrors to slip by


def read_topics(filenames, min_count=1):
    '''
    reads the files and returns a dict of dicts of dicts.
    --- The first layer's keys are the filenames
    --- The second' keys are topic ID strings from those filenames
    --- The third's keys are word strings, and values are wordcounts.
    Throws out words with counts below a set minimum.
    '''
    type_re = re.compile(r'''\b\d+\s(.+?)\s''')
    topic_re = re.compile(r'''(\s\d+:\d+)\b''')
    dicts = {}
    vocab = set([])
    for filename in filenames:
        if filename[-3:]=='.db':
            continue
        else:
            dicts[filename] = {}
            with open(filename,'r') as f:
                for line in f:
                    try:
                        type = type_re.findall(line)[0]
                        topics = [t.strip(' ') for t in topic_re.findall(line)]

                        staging_dict = {}  # stage additions to the output
                        frequency = 0
                        for pair in topics:
                            pivot = pair.find(':')
                            topic = int(pair[:pivot])
                            count = int(pair[pivot+1:])
                            frequency += count  # update frequency of this word
                            if topic not in staging_dict:  # add dict if needed
                                staging_dict[topic] = {}
                            staging_dict[topic][type] = count

                        if frequency >= min_count:  # check if minimum is met
                            for topic in staging_dict:
                                if topic not in dicts[filename]:  # add dict if needed
                                    dicts[filename][topic] = {}
                                # add current word to all topics it's found in
                                dicts[filename][topic].update(staging_dict[topic])
                            vocab.add(type)  # add to vocab

                    except IndexError:
                        raise IndexError('Bad input in file {}: line without type!'.format(filename))
    print '{} word types in vocabulary.'.format(len(vocab))
    return dicts, vocab

''' for each model: dok[topic, vocab_index] = word counts'''
def sparsify(dictionaries, vocab):
    ''' place dicts in COO format and convert to CSR matrix '''

    out = {}
    sorted_v = sorted(vocab)
    indexed_v = {sorted_v[i]:i for i in range(len(sorted_v))} #print indexed_v
    for model in dictionaries:
        dok = dok_matrix((len(dictionaries[model].keys()),len(sorted_v) + 1))
        for topic in range(len(dictionaries[model].keys())):
            for t in dictionaries[model][topic]:
                dok[topic,indexed_v[t]] = dictionaries[model][topic][t]
            #print dok.toarray() #dok.shape #sorted_v #indexed_v
            # add bias term for smoothing to last column
            dok[topic,len(sorted_v)] = 0.1
        out[model] = csr_matrix(dok)
    return out


def cosine_sparse(v1,v2):
    try:
        return 1 - ((v1.multiply(v2).sum()) /
                    (np.sqrt(v1.power(2).sum()) * np.sqrt(v2.power(2).sum())))
    except FloatingPointError as e:
        print '\n'.join([(v1.multiply(v2).sum()), np.sqrt(v1.power(2).sum()) *
                         np.sqrt(v2.power(2).sum()), v1, v2])
        raise e


def align_sparse_topic_triples(csrs, cutoff, vocab):
    try:
        a, b, c = (sorted(csrs.keys())[i] for i in range(3))
    except IndexError:
        raise IndexError('Function align_topic_triples() requires 3 models '
                         'to draw topics from.  Check input dictionary.')
    else:
        stable_topics = []
        index, sizes, triples = 0, [], {}

        # store all qualifying triples and their sizes

        print 'Stabilizing: storing all qualifying triples and their sizes. ("." = 500k)'
        considered = 0  # number of triples considered thus far

        for i in range(csrs[a].shape[0]):
            for j in range(csrs[b].shape[0]):
                size_ab = cosine_sparse(csrs[a][i], csrs[b][j])
                if size_ab < cutoff:
                    for k in range(csrs[c].shape[0]):
                        considered += 1
                        # progress report
                        if considered % 500000 == 0:
                            print '+500k:',
                            tk.elapsed()
                        if considered % 10000000 == 0:
                            print '{} considered so far'.format(considered)
                        size_ac = cosine_sparse(csrs[a][i], csrs[c][k])
                        if size_ac < cutoff:
                            size_bc = cosine_sparse(csrs[b][j], csrs[c][k])
                            if size_bc < cutoff:
                                triples[index] = (i,j,k)
                                index += 1
                                sizes.append(max([size_ab, size_bc, size_ac]))
                            else: # b and c disqualify this triple.
                                continue
                        else: # a & c rule out this triple; no need to get bc
                            # still only one triple has been considered
                            continue
                else: # a and b disqualify all remaining c vectors!
                    for k in range(csrs[c].shape[0]):
                        considered += 1
                        # progress report
                        if considered % 500000 == 0:
                            print '+500k:',
                            tk.elapsed()
                        if considered % 10000000 == 0:
                            print '{} considered so far'.format(considered)
                    continue

        tk.elapsed()
        print '{} of {} triples found below the cutoff.'.format(len(sizes), considered)
        print 'Stabilizing: sorting qualifying triples by size.'

        indices = list(np.argsort(sizes))[::-1]

        tk.elapsed()
        print 'Stablizing: drawing the best out of {} qualifying triples. '.format(len(sizes))

        used_a, used_b, used_c = set([]), set([]), set([])
        index_vocab = {i:sorted(vocab)[i] for i in range(len(vocab))}  # inverted index
        while len(indices) > 0:  # loop until no possible stable topics remain
            triple = triples.pop(indices.pop())
            #print triple

            if any([triple[0] in used_a, triple[1] in used_b,
                    triple[2] in used_c]):
                continue  # we've used a member of this triple already: skip it

            else:  # store this triple and its associated IDs
                d = {'counts': {},
                     'ids': {[a, b, c][i]: triple[i] for i in range(3)}}

                # store averaged word counts from these topics
                averaged = (csrs[a][triple[0]]+csrs[b][triple[1]]+csrs[c][triple[2]])/3
                print 'store averaged word counts from these topics: '
                print averaged
                avg_dok = averaged.todok()
                ''' avg_dok: (0, 6230) 134.6666667'''
                for k in avg_dok.keys():
                    index = index_vocab.get(k[1], None)
                    if index is not None:
                        d['counts'][index] = avg_dok.get(k)
                stable_topics.append(d)
                # add these topics to used sets
                used_a.add(triple[0])
                used_b.add(triple[1])
                used_c.add(triple[2])

        print '\n{} stable topics identified.'.format(len(stable_topics))
        return stable_topics


def write_stable_topics(stable_topics, filename, n=50):
    '''
    Writes two text files:
    --- /path/to/<filename>-counts.txt
        containing stable topic id, followed by the top n words in that topic
    --- /path/to/<filename>-ids.txt
        containing stable topic id, followed by the model-specific topic ids
        that compose it.
    '''
    with open(filename +'-counts.txt', 'wb') as f_counts, \
        open(filename + '-ids.txt', 'wb') as f_ids:

        # write informative headers to file
        f_counts.write('STABLE_ID ' + ' '.join('TOP_{}'.format(i)
                                               for i in range(n)) + '\n')
        f_ids.write('STABLE_ID ' +
                    ' '.join('ID_FOR_MODEL_{}'.format(m)
                             for m in sorted(stable_topics[0]['ids'])) + '\n')

        for i in range(len(stable_topics)):
            # write ids to file
            f_ids.write('{} {}'.format(i, ' '.join(str(stable_topics[i]['ids'][key]) for key in sorted(stable_topics[i]['ids']))) + '\t\n')
            # write top n words to file
            top_n = []
            sorted_n = sorted(stable_topics[i]['counts'].items(), key=lambda x: x[1], reverse=True)
            for j in range(min(n,len(sorted_n))):
                top_n.append(sorted_n[j][0])  # [0] is the word in item tuple
            f_counts.write('{} {}'.format(i, ' '.join(top_n) + '\t\n'))


# How to use:
'''
test_docs = [os.path.join('C:','mallet','tutorial-word_topic_counts'+which+'.txt') for which in ['','-b','-c']]

stable_topics = align_topic_triples(read_topics(test_docs,min_count=2), 0.7)

for t in stable_topics:
    print t['ids']
    print t['counts']
    print

write_stable_topics(stable_topics,os.path.join(os.getcwd(),'test'),n=5)
'''


def main():
    """
    model_dir = os.path.abspath(os.path.join(os.getcwd(),
                tk.confirm('Enter the path to the directory containing ONLY the'
                           ' word-topic-count text files for models to stabilize: ')))
    write_path = os.path.abspath(os.path.join(os.getcwd(),
                 tk.confirm('Enter the output directory path: ')))
    write_name = tk.confirm('Enter the desired name for associated output files: ')
    while True:
        try: cutoff = float(tk.confirm('Enter the cutoff parameter: '))
        except ValueError: continue
        else: break
    minimum = tk.confirm('Enter the minimum frequency per word: ',tk.choose_digits)[0]
    """

    model_dir = os.path.abspath(os.path.join(os.getcwd(),
                                             raw_input(
                                                 'Enter the path to the directory containing ONLY the'
                                                 ' word-topic-count text files for models to stabilize: ')))
    write_path = os.path.abspath(os.path.join(os.getcwd(),
                                              raw_input(
                                                  'Enter the output directory path: ')))
    write_name = raw_input('Enter the desired name for associated output files: ')
    # write_name = string.strip(write_name)

    while True:
        try: cutoff = float(raw_input('Enter the cutoff parameter: '))
        except ValueError: continue
        else: break
    while True:
        try: minimum = int(raw_input('Enter the minimum frequency per word: '))
        except ValueError: continue
        else: break

    'Palliative_Readmissions_ML\\100k_wordcounts'

    documents = [os.path.abspath(os.path.join(model_dir, f)) for f in os.listdir(model_dir)]
    print
    tk.elapsed()
    print 'Document paths stored.  Reading topics (tossing words less ' \
          'frequent than {} in dataset)...'.format(minimum)
    topics, vocab = read_topics(documents,
                         min_count=minimum,
                         #max_topics=175  # no significant effect was found.
                         )
    print 'Topics read.  Sparsifying...'
    tk.elapsed()
    sparse_matrices = sparsify(topics,vocab)
    print 'Sparsified.  Stabilizing...'
    tk.elapsed()
    stable_topics = align_sparse_topic_triples(sparse_matrices,cutoff, vocab)
    print 'Topics stabilized.  Writing...'
    tk.elapsed()
    write_stable_topics(stable_topics,os.path.join(write_path, write_name))
    print 'Topics written.'
    tk.elapsed()


if __name__ == '__main__':
    main()
