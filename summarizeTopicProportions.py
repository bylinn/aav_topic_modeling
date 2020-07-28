"""
Generate statistical file from component file
Output: a csv file with row are topics and columns being time slices for the total of topic proportions, total document counts, document proportion, and patient proportion. 
@lw592 2018.01.30
@1w592 2019.03.26: update the file for analyze AAV clinical notes, for which, we will get the trends before and after the diagnosis of AAV. 

"""

import os, sys, argparse, csv
import numpy as np
from corpus import MyCorpus

A, B, C = 0, 1, 2
STABLE_MEMBERS = {A: {}, B: {}, C: {}, 'stable':{} }
#label_index = list(range(-24, 76))  # generate a list of labels
label_index = np.arange(-24, 62, 2).tolist()
label_index = list(map(str, label_index))
print(label_index)
TOPIC_MATRIX = {} # at document level
TOPIC_MATRIX_PT = {} # at patient level
STABLE_SUMMARY = {}
DOC_COUNTS = {}
PT_IDs = {}
CORPUS_SIZE = {}

def getMembers(STABLE_TOPICS):
    """populate the stable members dictionary"""
    global STABLE_MEMBERS 
    with open(STABLE_TOPICS, 'r') as topics:
        next(topics)  # skip the header
        for ids in topics:
            #print (ids)
            stable, a, b, c = ids.split()
            
            STABLE_MEMBERS['stable'][str(stable)] = (a, b, c)
            STABLE_MEMBERS[A][a] = str(stable)
            STABLE_MEMBERS[B][b] = str(stable)
            STABLE_MEMBERS[C][c] = str(stable)
        
'''read in the composition file and get the '''    
def getTopicProportions(composition_file):
    global TOPIC_MATRIX
    global TOPIC_MATTRIX_PT

    
    for i in label_index:
        
        TOPIC_MATRIX[i]= {}
        TOPIC_MATRIX_PT[i] = {}
        DOC_COUNTS[i] = 0
        PT_IDs[i] = set()
        for topic in STABLE_MEMBERS['stable']:
            #initialize the matrix for each topics
            TOPIC_MATRIX[i][topic] = [float(0)]
            TOPIC_MATRIX_PT[i][topic] = {'0'}
    
    print(STABLE_MEMBERS['stable'].keys())
    if '38' in STABLE_MEMBERS['stable'].keys():
        print ("*****stable topis are strings and can be found in the keys!!******")

    if '21' in STABLE_MEMBERS['stable']:
        print("******stable topis can be found in the dictionary!!*******")

    
    with open(composition_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        #i= next(reader)
        #print('column names')
        #print(i)
        count = 0
        for row in reader:
            count = count + 1 
            if count<2:
                print(row)
##            if row['label'] == '0':
            # print (row.items())
            for (k, v) in row.items():  # go over each column name and value

##                if count < 4:
##                    if k in STABLE_MEMBERS['stable']:
##                        print(k + ' ' + ' is in the Stable member keys')
##                    elif k in STABLE_MEMBERS['stable'].keys():
##                        print('string ' + k + ' is in the key list ')
##                    else:
##                        print('do not sure what is ' + k + ' type ')
                
                if k in STABLE_MEMBERS['stable']:
                    # please check the label file and see what the column name used. 
                    #print('-------------: ' + row['doc_month_label']) 
                    if v !='' and row['doc_month_labels'] in label_index: # '999' encountered,so add restriction
                        #print('+++++++++++++++++++')
                        label_ind = row['doc_month_labels']
##                        EMPI = ''
##                        if 'Epic' in row['docID']:
##                            EMPI = row['docID'][row['docID'].find('_')+1:row['docID'].find('_')+10]
##                        elif 'rpdr' in row['docID']:
##                            EMPI = row['docID'].split('_')[3]
                        #print(' row[\'docID\']: ' + row['docID'])
                        #print(CORPUS_SIZE['corpus_doc_tokens'][100])
                        doc_token_counts = CORPUS_SIZE['corpus_doc_tokens'][int(row['docID'])]['word_counts']
                        #print('for doc ' + row['docID'] +  ', the topic ' + k + ' the number of tokens is ' + str(v) + '*' + str(doc_token_counts) )
                        doc_topic_token_counts = int(round(float(v) * doc_token_counts))
                        #if doc_topic_token_counts > 1:
                            #print('for doc ' + row['docID'] +  ', the topic ' + k + ' the number of tokens is ' + str(doc_topic_token_counts) )
##                        PT_IDs[label_ind].add(EMPI)
##                        DOC_COUNTS[label_ind] += 1
                        TOPIC_MATRIX[label_ind][k].append(doc_topic_token_counts)  # append the value into the appropriate list
#                        TOPIC_MATRIX_PT[label_ind][k].add(EMPI)
                    # based on column name k

def getStableTopicsSummaries(topic_file):
    with open(topic_file, 'r') as topicfile:
        for line in topicfile:
            summary = line.split("\t")
            STABLE_SUMMARY[summary[0]] = summary[4]
    print(len(STABLE_SUMMARY))

def writeCsv(out_file):
    with open(out_file, 'w') as csv_file:

        writer = csv.DictWriter(csv_file, lineterminator = '\n',
                                fieldnames = ['topic', 'summary'] + ['count_' + l for l in sorted(label_index, key=lambda x: int(x)) ] +
                                			['prop_' + l for l in sorted(label_index, key=lambda x: int(x)) ])


        writer.writeheader()


        for topic in STABLE_MEMBERS['stable'].keys():
            row =  {'topic': 'T_' + topic}
            for i in label_index:
                if i == '0': # there is no document labeled as 0. 
                    continue
                #print(TOPIC_MATRIX['0'][topic])
##                topic_label_score_sums[topic][i] = sum(TOPIC_MATRIX[i][topic])
##                topic_label_doc_counts[topic][i] = len(TOPIC_MATRIX[i][topic])
##                row['sum_score_' + i]=  sum(TOPIC_MATRIX[i][topic])
                label_topic_doc_counts =  len(TOPIC_MATRIX[i][topic])
                row['count_' + i] = label_topic_doc_counts
 #               row['prop_' + i] = float(label_topic_doc_counts/DOC_COUNTS[i])
                topic_token_counts = sum(TOPIC_MATRIX[i][topic])
                #print('total counts for topic '+ topic + ' is ' + str(topic_token_counts))
                row['prop_' + i] = float(topic_token_counts)/float(CORPUS_SIZE['corpus_total_tokens'][i])
#                row['pt_prop_' + i] = float((len(TOPIC_MATRIX_PT[i][topic])-1)/len(PT_IDs[i]))
            row['summary'] = STABLE_SUMMARY[topic]
            writer.writerow(row)

    # print out the patient numbers for each time slice
##    for i in label_index:
##        print('Patient number in time slice ' + i + ':' + str(len(PT_IDs[i])))
##

def main():

    global STABLE_MEMBERS
    global CORPUS_SIZE
    
    ap = argparse.ArgumentParser(description="Write out stable topic proportions for all documents in corpus.")
    ap.add_argument('stable', help='path to stable doc ids')
    ap.add_argument("composition_file", help='path to document-topic compositions file for first of three models')
    ap.add_argument("stable_summary", help='path to the stable topics summary file')
    ap.add_argument("doc_size_file", help='path to the corpus file containing the document id, word counts, and tokens')
    ap.add_argument("doc_label_file", help='path to the file of labels for each documents')
    ap.add_argument("output_file", help='path to csv file to write proportions to')

    args = ap.parse_args()
    if not all([os.path.isfile(f) for f in [args.stable, args.composition_file, args.stable_summary]]):
        raise IOError()
    if not args.output_file.endswith('.csv'):
        raise IOError()

    print('get corpus size by document and time slice...')
    mycorpus = MyCorpus()
    CORPUS_SIZE = mycorpus.get_corpus_size_from_files(args.doc_size_file, args.doc_label_file)

    print('identifying topics')
    getMembers(args.stable)
    print('get compositions...')
    getTopicProportions(args.composition_file)

    getStableTopicsSummaries(args.stable_summary)
    print('writing compositions...')

    writeCsv(args.output_file)
	

if __name__ == '__main__':
    main()
