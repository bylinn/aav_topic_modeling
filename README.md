# topic_modeling

-- Generate stable topics
After running the Mallet, LDA-based topic modeling, to generate three topic models, use the topic_distance.py to generate stable topics. 

Commands: 
python2 topic_distance.py 
folder_path\wc 
folder_path 
stable 
.7 
50

python2 review_stable.py folder_path\stable-ids.txt folderpath

python2 summarize_stable.py folder_path\stable-review.txt 15 


---  Generate the stable topic document proportion for each docuemnt, be aware that the print out file will still be *byte* format. 

generate the filename_months_to_dx.txt file with the fields: filename, and the months to diagnosis (or initial treatment)

Commands:
python documentTopicProportions.py folder_path\stable-ids.txt folder_path\dtc-1.txt folder_path\dtc-2.txt folder_path\dtc-3.txt folder_path\filename_months_to_treatment.txt folder_path\compositions.csv


--- Generate summary of the topics over months prior to or post the treatment.  

Commands:
python summarizeTopicProportions.py folder_path\stable-ids.txt folder_path\compositions.csv folder_path\stable-review-summary.txt folder_path\\corpus.txt folder_path\filename_months_to_treatment.txt folder_path\summaries.csv 
 
 
