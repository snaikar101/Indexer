import gzip
import re
import os
import glob
import sys
import math
import heapq

class list ():
	def __init__(self, term, frequency, inv_indxlist):
		self.term=term
		self.frequency = frequency
		self.valueList = []
		self.seek=0
		self.valueList = inv_indxlist


class searchquery ():
	def __init__(self):
		self.listcount=0

	def openList(self,pos,freq):
		# open index structure and seek to pos
		p= gzip.open("file_prefixindex",'rb')
		p.seek(int(pos))
		
		for line in p:
			word,value = line.split(' ',1)
			vlist= value.split()
			break
		vlist=[int(i) for i in vlist]
		valueList = [] 
		for i in range(0,len(vlist),2):
			templist=[]
			templist.append(vlist[i])
			templist.append(vlist[i+1])
			valueList.append(templist)
		# Create a list object and return the list object with all values set
		lsobj = list(word,freq,valueList)
		return lsobj

	def closeList(self,p):
		lp.close()

	def getFreq(self,lp):
		currposition = lp.seek
		return lp.valueList[currposition][1]

	#def nextGEQ(self,listobj,k):
		#length=len(listobj.valueList)
		#curr=listobj.seek
		#chunknumber = curr/20
		#seekpos=curr%20
		#f=True
		#z=True
		#for i in range(chunknumber*20+20,length,20):
			#z=False
			#if k==listobj.valueList[i][0]:
				#listobj.seek=i
				#return k
			
			#if k<listobj.valueList[i][0]:
				#f=False
				#curr=i-20
				#end=min(i,length)
				#break
		
		#if f==True:
			#if z==True:
				#curr=chunknumber
				#end = length
			#else:
				#curr=i
				#end=length
		
		#temp=listobj.valueList[curr][0]
		#j=curr
		#for j in range(curr+1,end):
			#temp=temp+listobj.valueList[j][0]
			##print j, temp
			#if temp >= k:
				#listobj.seek=j
				#return temp
		##print "j: ",j
		#if j+1==length:
			#listobj.seek=j
			#return -1
		#if j==end-1:
			#listobj.seek=j+1
			#return listobj.valueList[end][0]


	
	def nextGEQ(self,listobj,k):
		
		length=len(listobj.valueList)
		#if k is less than the first element in the list, return the first element
		if listobj.seek==0 and k<=listobj.valueList[0][0]:
			return listobj.valueList[0][0]

		else: 
			curr=listobj.seek
			chunknumber = curr/20
			seekpos=curr%20
			# If list is less than 20, then there is only 1 chunk. curr and end are set appropriately
			if length<20:
				curr=0
				end=length
			# last chunk
			elif chunknumber*20+20 > length:
				curr=chunknumber*20
				end=length
				
			else: 
				end=length
				# Check k with the first value of each chunk and set curr and end appropriately
				for i in range(chunknumber*20+20,length,20):
					# if found in 1st element, set seek position and return k
					if k==listobj.valueList[i][0]:
						listobj.seek=i
						return k
					# k lies in previous chunk
					if k<listobj.valueList[i][0]:
						curr=i-20
						end=i
						break
					#last chunk
					else:
						curr=i
						end=length
				
				# if seek is already in last chunk, set last chunk to search					
				if curr+20 > length:
					curr=chunknumber*20
					end=length

			#Decompressing the chunk
			temp=listobj.valueList[curr][0]
			for j in range(curr+1,end):
				temp=temp+listobj.valueList[j][0]
				if temp >= k:
					listobj.seek=j
					return temp
			# if not found, return -1
			if j+1==length:
				listobj.seek=j
				return -1
			# if k lies between the last element in chunk and 1st element in next chunk, return 1st element from next chunk
			if j==end-1:
				listobj.seek=j+1
				return listobj.valueList[end][0]

			
def main():
	
	fp=open('docmavavg.txt','r') #This file contains max doc id and avg doc length
	tfp=fp.readline()
	maxdocID=int(tfp.split(' ')[0])
	doc_avg=float(tfp.split(' ')[1])
	fp.close()
	
	# Storing index file into memory
	fp=gzip.open("file_prefixlex",'rb')
	lex={}
	for line in fp:
		word,value = line.split(' ',1)
		vsp=value.rstrip(os.linesep).split()
		ft=float(vsp[1])
		lv = math.log10( (float(maxdocID)-ft+0.5)/(ft+0.5)) 
		lex[word]=[vsp[0],vsp[1],lv]
	fp.close()
	print "Lexicon Structure Loaded"
	docfp=gzip.open('doc.gz','r')
	docurl={}
	b=0.75
	k1=1.2
	for line in docfp:
		tfp=line.split(' ')
		k=float(k1*((1-b)+(b*float(tfp[2])/doc_avg)))
		docurl[int(tfp[0])] = [tfp[1],tfp[2],k] 
	docfp.close()
	
	print "Doc url Structure Loaded"
	
	searchString = ""
	while(True):
		
		searchString = raw_input("Enter Search String\n")

		searchList = searchString.split()

		# Using CLass 
		obj = searchquery()

		
		#list of pointers
		lp=[]
		for i in range(0,len(searchList)):
			word=searchList[i]
			if word in lex:
				#Creating list of pointers 
				lp.append(obj.openList(lex[word][0], lex[word][1]))
		
		lp.sort(key=lambda l:len(l.valueList))
			
	
		did = 0
		hp = []
		while did <= maxdocID and did!= -1 :
			# get next post from shortest list
			if len(lp) != 0:
				did = obj.nextGEQ(lp[0], did)
			else:
				did = -1
			#print "in next main:",did
			if did == -1:
				break
			d=did
			for i in range(1,len(lp)):
			
				d=obj.nextGEQ(lp[i], did)
				#print "in next main:", d
				
				if d != did:
					break
				
			
			if d==-1:
				#print "i am never -1"
				break
			
			if d != did:
				did=d
				continue
		
			
			bm25=0.0
			for i in range(0,len(lp)):
				fdt=obj.getFreq(lp[i])
				k=docurl[did][2]
				tbm25=lex[lp[i].term][2] * ( (k1+1)*fdt / (k+fdt)  )
				bm25=bm25+tbm25
			
			if len(hp) < 10:
				heapq.heappush(hp,[(bm25),docurl[did]])
			else:
				heapq.heapreplace(hp,[(bm25),docurl[did]])
		
			#print "bm25:",bm25 , "url: ",docurl[did][0] , "did:" , did
			did=did+1
	
		print "your Result are:"
		hp.sort(reverse=True)
		for i in range(0,len(hp),1):
			r=hp[i]
			print "url",r[1][0] ," score:", r[0]
		searchString = ""
		obj=None
		lp=None
		hp=None

if __name__== '__main__':
	main()




