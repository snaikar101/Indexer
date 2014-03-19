This Assignment is written in python. 
Below are the files
1. readgz.py [Set the the  root file location self.rootDirectory]
2. split.py  [File size of the desired output sizes ts in main]
3. merge.py  [Set self.r to total files generated in by split.py and self.sz to ram ]

readgz.py
------------
This file will generate the temproary inverted index structure[inv_ind.gz] and Doc_id postings [doc_id url count]. 
We have created FileReader class. In main, we will first instantiate FileReader class. debug_set is set to false, so that we can write it to compressed file i.e. Gzip file. 
We will first read all the files from nz2_merged directory and validate the index and data file names with regular expression. 
We will read the index file and corresponding data file together, parse it and write it into the final inverted index file,  'ind_inv' for every 5 index,data files. 
We have used the C parser given by you and modified by viraj shah. 
We will call process_tok function, which puts all the token to hashtable. The key of this hashtable is the token and the value is the count of the token. 
We have assigned the docId in the order the pages are parsed. 
We will finally write the docID, URL and number of words into a compressed file 'doc.gz'. The Final inverted index structure will be in the form, word docId number_of_words. 
readgz.py will take 2 minutes, 40 seconds to complete for 2% of data and 2hr 30 minutes for complete set. 

split.py
-----------

This python code will split the actual inv_ind file into several files of 500MB[2% of 500MB for NZ2] each and sort each file using unix sort. This code will first open the temp file, read each line from index file, check if temp has reached 500MB[2% of 500MB for NZ2] and append the line if it has not yet reached the maximum size. 
After splitting file, each file is then sorted using UNIX sort. Finally it will return the number of temp files created. 
For 2% of data, we are using 2% of 500MB. split.py will take 57 seconds and 40 minutes for complete set.

Merge.py
------------
Merge.py will merge all the temp files created by split.py code. This code will even create lexicon structure. At first, we will initialise Merge class which will have 1 output buffer, file pointers of Lexicon file and sorted Index file. Here, we are using r+1 files, r for input buffer and 1 for output buffer. In the first step, we will read data from all input buffers, construct the heap and finally get the top value until heap is empty. write_final method will create a lexicon structure. 
The size of data is 2% of 500MB / (r+1)
Time: 3 minutes, 4 seconds

Final Result and its size
-----------------------------
Final lexicon file size: 2.3MB
Final compressed Index file size: 34.8MB
doc.gz: 880KB

Known Defects
----------------
Parser returns &nbsp;

Things That will be done in next project
-------------------------------------------
Index compression
No location in postings
Modify merge.py to accomodate different passes for IO effecient merge sort

