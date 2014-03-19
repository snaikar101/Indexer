import StringIO
import gzip
import heapq
import sys
import math

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
		self.of = gzip.open("final_indx",'wb') #final output remove gzip. for debug mode
		self.lexf = gzip.open("final_lex",'wb') #final lexicon structure remove gzip. for debug mode
		self.r=11                               #total number of files
		self.sz=int(math.floor(524288000*2/100/(self.r+1)))
		
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
	#Sets data for lexicon so no need of extra parse		
	def write_final(self,tok,invitem):
		#print sys.getsizeof(self.outputBuffer+invitem)
		if sys.getsizeof(self.outputBuffer+invitem) > self.sz:
			n=self.outputBuffer[:-1].rfind('\n')
			lst = self.outputBuffer[n+1:]
			if lst[0:len(tok)] == tok:
				self.of.write(self.outputBuffer[:-len(lst)])
				#print(self.outputBuffer[:-len(lst)])
				self.outputBuffer=lst+ invitem[len(tok):]+'\n'
				self.ls[-1][2]=self.ls[-1][2]+(len(invitem.split(' '))-1)/2
				print("Written")
				
			else:
				self.ls.append([tok,self.of.tell(),(len(invitem.split(' '))-1)/2])
				self.of.write(self.outputBuffer)
				#print(self.outputBuffer)
				print("Written")
				self.outputBuffer=invitem+'\n'
				
		else:
			n=self.outputBuffer[:-1].rfind('\n')
			lst = self.outputBuffer[n+1:]
			if lst[0:len(tok)] == tok:
				self.outputBuffer=self.outputBuffer.rstrip()+invitem[len(tok):]+'\n'
				self.ls[-1][2]=self.ls[-1][2]+(len(invitem.split(' '))-1)/2
			else:
				self.ls.append([tok,self.of.tell()+len(self.outputBuffer),(len(invitem.split(' '))-1)/2])
				#print tok + ":" + str(of.tell()+len(self.outputBuffer))
				self.outputBuffer=self.outputBuffer+invitem+'\n'
	#Write to lexcon file			
	def writeLex(self):
		print ("Writting lexicons")
		for lexicon in self.ls:
			self.lexf.write(str(lexicon[0])+" "+str(lexicon[1])+" "+str(lexicon[2])+"\n")		
				
def main():
	merge = Merge()
	f=[] #File pointers list
	fr=[] #Input read buffers
	heap_items=[]
	for i in range(merge.r):
		f.append(gzip.open("temp_"+str(i),'rb'))
	print("files opened")
	for i in range(merge.r):
		fr.append(merge.readInput(f[i],merge.sz))
		merge.constructHeap(fr[i][0].split('\n'),heap_items,i) #put first set in heap appends a marker to last element
	
	while len(heap_items)>0:
			tok,doc_id, hi =heapq.heappop(heap_items) #pop tokens
			if tok != '':
				merge.write_final(tok,hi.invitem)
			if hi.is_last== True:      #if last element of file read the next set of data
				if fr[hi.fl][1]:		#checks if file is not empty 
					fr[hi.fl]=merge.readInput(f[hi.fl],merge.sz)
					merge.constructHeap(fr[hi.fl][0].split('\n'),heap_items,hi.fl)
	merge.writeLex()   #Writes lexicon details to file
if __name__=='__main__':
	main() 
		
