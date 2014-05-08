import gzip
import zlib
import parser
import re
import os
import sys
from cStringIO import StringIO
import urllib2
import time

class Page:
	
	def __init__(self,url,no_words):
		self.url=url
		self.no_words=no_words
		

class FileReader:
	
	def __init__(self,debug_set):
		self.rootDirectory = "/home/santu/Index/nz10/data"
		self.t_count=0
		self.page_table={}   #Doc_id url count
		self.temp_index={}   #Hash of postings
		self.doc_id=0
		self.f_html =None
		self.f_index =None
		self.docavg=0.0
		if debug_set:
			self.doc_file= open('doc.txt','w')
			self.ind_file= open('inv_ind.txt','w')
		else:
			self.doc_file= gzip.open('doc.gz','wb')
			self.ind_file= gzip.open('inv_ind.gz','wb')
	
	#write doc_id url count to file	
	def writeDoc(self):
		for k,v in self.page_table.iteritems():
			self.docavg=float((((float(k)-1)*float(self.docavg))+float(v.no_words))/float(k))
			self.doc_file.write(str(k)+" "+str(v.url)+" "+str(v.no_words)+"\n")		
		
		for k,v in self.temp_index.iteritems():
			self.ind_file.write(str(k)+" "+str(v)+"\n")
		
		fdoc=open('docmavavg.txt','w')
		fdoc.write(str(self.doc_id)+' '+str(self.docavg))
		fdoc.close()	
			
	#Find the word in the hash table and appends to postings
	def addToHash(self,doc_id,tempHash):
		for k,v in tempHash.iteritems():
			if k in self.temp_index:
				self.temp_index[k] = str(self.temp_index[k])+" "+str(doc_id)+" "+str(v)
			else:
				self.temp_index[k]= str(doc_id)+" "+str(v)
	
	#process the tockens returned from parser
	def process_tok(self,tok,doc_id,tempHash):
		if tok in tempHash:
			tempHash[tok] =tempHash[tok]+1
		else:
			tempHash[tok]= 1
			
	#Write from hash table to index and truncate the hash table
	def writeToIndex(self):
		for k,v in self.temp_index.iteritems():
			self.ind_file.write(str(k)+" "+str(v)+"\n")
		self.temp_index={}
	#returns true for valid tokens could be enhanced  
	def validToken(self,tok):
		if len(str(tok)) > 45:
			return False
		if re.search('^[a-zA-Z0-9]+$', tok.split(' ')[0]):
			return True
		return False
		
	
def main():
	fr= FileReader(False)
	c=1
	prog = re.compile(r'^[0-9]+_data')  #to match index files
	for root, dirs, files in os.walk(fr.rootDirectory):
		
		for f in files:
			
			if prog.match(f):
				i=f.split('_')[0]+'_index'
				print("current Data file: "+os.path.join(root,f)+ "Size: "+str(c))					
				if c%5 == 0:      #after reading every 5 data files write the data on hash table to temp index structure
					fr.writeToIndex()
					#break
				c=c+1
				fr.f_html = gzip.open(os.path.join(root,f), 'rb')  #open  data_ file
				fr.f_index = gzip.open(os.path.join(root,i), 'rb') #open html_file
				for line in fr.f_index:
					try:
						_split = re.compile(r'[\0%s]' % re.escape(''))  #remove \0 from file possible defect
						i_data=[]
						i_data=line.split()
						url = i_data[0]
						url = url.strip()
						html_str=fr.f_html.read(int(i_data[3]))  # read html of the size[got from index]
						html_str=_split.sub('',html_str) 
						if i_data[6] !='ok' and i_data[6] !='200':
							break			
						pool=html_str+html_str+"123456";  
						p_tok_t=[]
						p_tok_t=parser.parser(urllib2.unquote(url), html_str,pool, len(html_str)+1,len(html_str)+1) #returns token
						p_tok=str(p_tok_t[1]).split('\n')  
						no_words=0
						fr.doc_id=fr.doc_id+1
						tempHash={}
						for tok in p_tok:      #porsess the tokens returned from file
							if fr.validToken(tok):
								fr.process_tok(tok.split(' ')[0],fr.doc_id,tempHash)
								no_words=no_words+1				
								
						fr.addToHash(fr.doc_id,tempHash)
						page = Page(url,no_words)
						fr.page_table[fr.doc_id]=page
						
					except TypeError,e:
						i_data=[]
						i_data=line.split()
						url = i_data[0]
						url = url.strip()
						print(url)
						
						
				fr.f_html.close()
				fr.f_index.close()
				
	
	fr.writeDoc()   #write doc_id url count to file
	fr.ind_file.close()
	fr.f_html.close()
	fr.f_index.close()
	
if __name__== '__main__':
	start_time = time.time()
	main()
	print (time.time() - start_time)/60, "Minutes"
