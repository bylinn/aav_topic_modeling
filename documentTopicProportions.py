"""

A script to report the prevalence of stabilized topics within notes.  Notes must 
have a preset minimum composition of at least 2 of the 3 original topics that 
form the stabilized topic in order to be detected here.  This minimum 
composition should be set during model creation.  That is, only topics that are 
recorded in the appropriate MALLET "document-topic composition" files for each 
model will be used by this script.  

Note that the value for each stable topic's proportion will be set to the mean 
proportion for all of its component topics.

Stabilization technique follows Shao et al. 2016.

USAGE: >$ python documentTopicProportions.py <DTC File 1> <DTC File 2> <DTC File 3> [<output>]
<DTC File>: a path to a file containing document-topic composition numbers for the notes to check.
The files should be in the order that the inferencers are combined in the stable topics--probably "1, 2, 3".
<output>: a filepath to write output to

@csr18 2017.12.19

@lw592 2018.02.18:
    revised the script and fit for the topic analysis project in terms of the labeling. 
@lw592 2019.03.25
	the format of the documents filename may change, thus, revise scripts to get the path/doc_id
"""

import os, sys, argparse, csv

A, B, C = 0, 1, 2
STABLE_MEMBERS = {A: {}, B: {}, C: {}, 'stable':{} }

def getMembers(STABLE_TOPICS):
    """populate the stable members dictionary"""
    global STABLE_MEMBERS
    with open(STABLE_TOPICS, 'r') as topics: ## have to be use rb!! 
        next(topics)  # skip the header
        for ids in topics:
            #print ids
            stable, a, b, c = ids.split()
            STABLE_MEMBERS['stable'][stable] = (a, b, c)
            STABLE_MEMBERS[A][a] = stable
            STABLE_MEMBERS[B][b] = stable
            STABLE_MEMBERS[C][c] = stable
                
def checkForTargets(compositions_1, compositions_2, compositions_3):
    """given three doc-topic-composition files, identify which stable topics 
       are considered present in their documents and return them"""
    compositions = (compositions_1, compositions_2, compositions_3)
    #print(compositions, list(compositions[model] for model in [A, B, C]))
    found = {}
    for model in [A, B, C]:  # find stable topics in composition files
        with open(compositions[model], 'rb') as documents:  ## have to use 'rb' otherwise the float numbers won't be read!!!
            #print(compositions[model])
            next(documents)  # skip header
            #for num, doc in enumerate(documents):
            for doc in documents:
            
                #if num > 2: break
                
                data = doc.split()
                doc_id, doc_name, components = data[0].decode(), data[1].decode(), data[2:]
               
                #print(doc_id, doc_name)
                #doc_id = doc_id.decode()
                #print(doc_id)
                if doc_id not in found: 
                    found[doc_id] = {}
                    found[doc_id]['doc_name'] = doc_name
                # get all topic-proportion pairs in this document:
                components = [components[i:i+2] for i in range(0, len(components), 2)]
                
                #print components
                for topic, proportion in components:
                    #print topic, proportion
                    stable = STABLE_MEMBERS[model].get(topic.decode(), None)
                    #if model != 0: print(model, stable)
                    if stable is not None:  #this topic is among the stable topics
                        #if num==0: print doc_id, stable, model, topic, proportion
                        if stable in found[doc_id].keys():
                            #print 'app'
                            try:
                                found[doc_id][stable].append(float(proportion))
                            except ValueError:  # bad proportion / broken data (seems to be a giant string that can't eval to float)
                                continue  # skip this 
                        else:
                            found[doc_id][stable] = [float(proportion)]
                        #if stable == '0': print found[doc_id] #stable in found[doc_id]
    for doc_id in found:  # keep only consistently-found topics
        #print(list(found[doc_id].keys()))
        for stable in list(found[doc_id].keys()):
            
            if stable == 'doc_name':  ## if the key is doc_name then continue; 
                continue
            if len(found[doc_id][stable]) < 2:  # only found by one model: clean up
                found[doc_id].pop(stable)
            else:  # take mean proportion
                found[doc_id][stable] = sum(found[doc_id][stable])/float(len(found[doc_id][stable]))
                
    return found
    

def label(doc_ID):
    if doc_ID.startswith(b'd01m'): return 23
    elif doc_ID.startswith(b'd02m'): return 22
    elif doc_ID.startswith(b'd03m'): return 21
    elif doc_ID.startswith(b'd04m'): return 20
    elif doc_ID.startswith(b'd05m'): return 19
    elif doc_ID.startswith(b'd06m'): return 18
    elif doc_ID.startswith(b'd07m'): return 17
    elif doc_ID.startswith(b'd08m'): return 16
    elif doc_ID.startswith(b'd09m'): return 15
    elif doc_ID.startswith(b'd10m'): return 14
    elif doc_ID.startswith(b'd11m'): return 13
    elif doc_ID.startswith(b'd12m'): return 12
    elif doc_ID.startswith(b'd13m'): return 11
    elif doc_ID.startswith(b'd14m'): return 10
    elif doc_ID.startswith(b'd15m'): return 9
    elif doc_ID.startswith(b'd16m'): return 8
    elif doc_ID.startswith(b'd17m'): return 7
    elif doc_ID.startswith(b'd18m'): return 6
    elif doc_ID.startswith(b'd19m'): return 5
    elif doc_ID.startswith(b'd20m'): return 4
    elif doc_ID.startswith(b'd21m'): return 3
    elif doc_ID.startswith(b'd22m'): return 2
    elif doc_ID.startswith(b'd23m'): return 1
    elif doc_ID.startswith(b'd24m'): return 0
    else: return 999

def labelText(label):
    if label == 0: return 'd24m'
    elif label == 1: return 'd23m'
    elif label == 2: return 'd22m'
    elif label == 3: return 'd21m'
    elif label == 4: return 'd20m'
    elif label == 5: return 'd19m'
    elif label == 6: return 'd18m'
    elif label == 7: return 'd17m'
    elif label == 8: return 'd16m'
    elif label == 9: return 'd15m'
    elif label == 10: return 'd14m'
    elif label == 11: return 'd13m'
    elif label == 12: return 'd12m'
    elif label == 13: return 'd11m'
    elif label == 14: return 'd10m'
    elif label == 15: return 'd09m'
    elif label == 16: return 'd08m'
    elif label == 17: return 'd07m'
    elif label == 18: return 'd06m'
    elif label == 19: return 'd05m'
    elif label == 20: return 'd04m'
    elif label == 21: return 'd03m'
    elif label == 22: return 'd02m'
    elif label == 23: return 'd01m'
    else: return 'bad_filename'
    
def writeCsv(docs, docLabels, csv_file):
    writer = csv.DictWriter(csv_file, lineterminator='\n', 
                            fieldnames=["docID", "doc_name", "doc_month_labels"] + 
                                       sorted(STABLE_MEMBERS['stable'].keys(), 
                                              key=lambda x: int(x)))
    writer.writeheader()
    
    for count, doc_id in enumerate(sorted(docs.keys())):
        docs[doc_id]["docID"] = doc_id
        #print(docs[doc_id]["doc_name"])
        docs[doc_id]["doc_month_labels"] = docLabels.get(docs[doc_id]["doc_name"], None)
        #print(docLabels[docs[doc_id]["doc_name"]])
        writer.writerow(docs[doc_id])
        if count%2500==0:
            #print(docs[doc_id])
            print('+2.5k...')#,end='')
      

def main():

    global STABLE_MEMBERS
    
    ap = argparse.ArgumentParser(description="Write out stable topic proportions for all documents in corpus.")
    ap.add_argument('stable', help='path to stable doc ids')
    ap.add_argument("dtc_1", help='path to document-topic compositions file for first of three models')
    ap.add_argument("dtc_2", help='path to document-topic compositions file for second of three models')
    ap.add_argument("dtc_3", help='path to document-topic compositions file for third of three models')
    ap.add_argument("doc_labels", help='path to document label file')
    ap.add_argument("ouput_file", help='path to csv file to write proportions to')
    args = ap.parse_args()
    if not all([os.path.isfile(f) for f in [args.stable, args.dtc_1, args.dtc_2, args.dtc_3, args.doc_labels]]):
        raise IOError()
    if not args.ouput_file.endswith('.csv'):
        raise IOError()
    with open(os.path.abspath(args.ouput_file), 'w') as f_out:
        print('identifying topics...')
        getMembers(args.stable)    
        print('generating compositions...')
        found = checkForTargets(args.dtc_1, args.dtc_2, args.dtc_3)

        docLabels = {}
        print(os.path.abspath(args.doc_labels))
        with open(os.path.abspath(args.doc_labels), 'r') as f_label:
            next(f_label)
            for line in f_label:
                ##components = line.split(';')
                components = line.split("\t") ## it needs to be changed based on the sperator used in the document
                docLabels[components[0]] = components[1].strip() ## get the label for each document   
            print('writing compositions...')
            print(len(docLabels))
            writeCsv(found, docLabels, f_out)

if __name__ == '__main__':
    main()
