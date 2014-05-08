import StringIO
import gzip
import heapq
import sys
import math
import time

class HeapItem:
	def __init__(self,tok,invitem,fl,is_last):
		self.tok=tok
		self.invitem=invitem
		self.fl=fl
		self.is_last = is_last
		

class Merge:
	def __init__(self):
		self.ls=[]
		self.outputBuffer=''   #output buffer
		self.of = None #final output remove gzip. for debug mode
		self.lexf = None #final lexicon structure remove gzip. for debug mode
		self.r=11                               #total number of files
		self.sz=int(math.floor(524288000*2/100/(self.r+1)))
		self.chunckSize=20
		
	#reads files of size sz into input buffer
	def readInput(self,f,sz):
		eof=False
		fr=f.read(sz)
		n=fr.rfind('\n')
		print(len(fr))
		if len(fr) < sz:
			eof=True
			print("reached end of file")
			return (fr,False)
		else:
			f.seek(n-sz+1,1)
			return (fr[:n-sz],True)
		
	#To construct heap Token , docid
	def constructHeap(self,fr1,heap_items,fl):
		#fr1=self.readInput(f1,sz)[0].split('\n')
		i=len(fr1)
		for fr in fr1:
			tok=fr.split(' ')
			if len(tok)>2:
				doc_id=int(fr.split(' ')[1])
			else:
				doc_id=0
			if i==1:
				#print("I am lsat"+str(fl))
				hi=HeapItem(tok[0],fr,fl,True)
			else:
				hi=HeapItem(tok[0],fr,fl,False)
			i=i-1
				
			heapq.heappush(heap_items,(tok[0],doc_id,hi))
			
			
	#Writes to final output index when ever the output buffer is full 
	#it also merges two lists of same token
	
	def write_final(self,tok,invitem):
		#print sys.getsizeof(self.outputBuffer+invitem)
		if sys.getsizeof(self.outputBuffer+invitem) > self.sz:
			n=self.outputBuffer[:-1].rfind('\n')
			lst = self.outputBuffer[n+1:]
			if lst[0:len(tok)] == tok:
				compData=self.chunckCompress(self.outputBuffer[:-len(lst)])
				self.of.write(compData)
				#print(self.outputBuffer[:-len(lst)])
				self.outputBuffer=lst+ invitem[len(tok):]+'\n'
				#self.ls[-1][2]=self.ls[-1][2]+(len(invitem.split(' '))-1)/2
				print("Written")
				
			else:
				#self.ls.append([tok,self.of.tell(),(len(invitem.split(' '))-1)/2])
				compData=self.chunckCompress(self.outputBuffer)
				#exit(0)
				self.of.write(compData)
				#print(self.outputBuffer)
				print("Written")
				self.outputBuffer=invitem+'\n'
				
		else:
			n=self.outputBuffer[:-1].rfind('\n')
			lst = self.outputBuffer[n+1:]
			if lst[0:len(tok)] == tok:
				self.outputBuffer=self.outputBuffer.rstrip()+invitem[len(tok):]+'\n'
				#self.ls[-1][2]=self.ls[-1][2]+(len(invitem.split(' '))-1)/2
			else:
				#self.ls.append([tok,self.of.tell()+len(self.outputBuffer),(len(invitem.split(' '))-1)/2])
				#print tok + ":" + str(of.tell()+len(self.outputBuffer))
				self.outputBuffer=self.outputBuffer+invitem+'\n'
	
	#Write to lexcon file			
	def writeLex(self):
		print ("Writting lexicons")
		for lexicon in self.ls:
			self.lexf.write(str(lexicon[0])+" "+str(lexicon[1])+" "+str(lexicon[2])+"\n")
	
	#Applies chunk compression to the data
	#Sets data for lexicon so no need of extra parse
	def chunckCompress(self,posting_list):
		loc=self.of.tell()
		fps=''
		for posting in posting_list.split('\n'):
			ps = posting.split(' ')
			ps_size=len(ps)
			fps=fps+ps[0]
			self.ls.append([ps[0],loc,(ps_size-1)/2])
			for i in range(1,len(ps),2):
				if ((i-1)/2)%self.chunckSize == 0:
					fps=fps+' '+ps[i]+' '+ps[i+1]
				else:
					#fps=fps+' '+ps[i]+' '+ps[i+1]
					fps=fps+' '+str(int(ps[i])-int(ps[i-2]))+' '+ps[i+1]
			fps=fps+'\n'
			n=fps[:-1].rfind('\n')
			loc=loc+len(fps[n+1:])
			
		return fps
				

def nwaymerge(s,e,memory,file_prefix,final_file):
	merge = Merge()
	f=[] #File pointers list
	fr=[] #Input read buffers
	merge.of = gzip.open(final_file+'index','wb') #final output remove gzip. for debug mode
	merge.lexf = gzip.open(final_file+'lex','wb') #final lexicon structure remove gzip. for debug mode
	heap_items=[]
	merge.sz=int(math.floor(memory/(e-s+2)))
	for i in range(s,e+1):
                f.append(gzip.open(file_prefix+str(i),'rb'))
	print("files opened")
	for i in range(e-s+1):
		fr.append(merge.readInput(f[i],merge.sz))
		merge.constructHeap(fr[i][0].split('\n'),heap_items,i) #put first set in heap appends a marker to last element
	
	while len(heap_items)>0:
		tok,doc_id, hi =heapq.heappop(heap_items) #pop tokens
		if tok != '':
			merge.write_final(tok,hi.invitem)
		if hi.is_last== True:      #if last element of file read the next set of data
			if fr[hi.fl][1]:                #checks if file is not empty 
				fr[hi.fl]=merge.readInput(f[hi.fl],merge.sz)
				merge.constructHeap(fr[hi.fl][0].split('\n'),heap_items,hi.fl)
	
	merge.writeLex()   #Writes lexicon details to file
	
				
def main():
	nwaymerge(0,11,20000000,'temp_','file_prefix')
	#~ merge = Merge()
	#~ f=[] #File pointers list
	#~ fr=[] #Input read buffers
	#~ heap_items=[]
	#~ for i in range(merge.r):
		#~ f.append(gzip.open("temp_"+str(i),'rb'))
	#~ print("files opened")
	#~ for i in range(merge.r):
		#~ fr.append(merge.readInput(f[i],merge.sz))
		#~ merge.constructHeap(fr[i][0].split('\n'),heap_items,i) #put first set in heap appends a marker to last element
	#~ 
	#~ while len(heap_items)>0:
			#~ tok,doc_id, hi =heapq.heappop(heap_items) #pop tokens
			#~ if tok != '':
				#~ merge.write_final(tok,hi.invitem)
			#~ if hi.is_last== True:      #if last element of file read the next set of data
				#~ if fr[hi.fl][1]:		#checks if file is not empty 
					#~ fr[hi.fl]=merge.readInput(f[hi.fl],merge.sz)
					#~ merge.constructHeap(fr[hi.fl][0].split('\n'),heap_items,hi.fl)
	#~ merge.writeLex()   #Writes lexicon details to file
	
if __name__=='__main__':
	start_time = time.time()
	main()
	print (time.time() - start_time)/60, "Minutes"
