import os
import gzip
import sys

class Spliter ():
	
	def __init__(self,temp_size,debug_set):
		self.temp_size=temp_size
		self.file_sie=os.path.getsize("inv_ind.gz")  
		self.inv_h = gzip.open("inv_ind.gz","rb")
		self.debug_set=debug_set
		
	#sort the files in temp and compress and write to other file
	def sort_temp(self,i):
			temp_ind_lst = os.popen('sort -k1,1 -k2,2n temp')
			if self.debug_set == False:
				temp = gzip.open('temp_'+str(i),'wb')
			else:
				temp = open('temp_'+str(i),'w')
			for ind in temp_ind_lst:
				temp.write(ind)
			temp.close()
	
			
def main():
	inv_h = gzip.open("inv_ind.gz","rb")
	i=0
	ts=524288000*2/100  #When running for nz
	spliter = Spliter(ts,False)
	c=0
	temp_ind_lst = []
	for line in inv_h:
		if c==0:
			temp=open('temp','w')
			print ("writing to:"+'temp_'+str(0))
			c=1
		if temp.tell()+sys.getsizeof(line) < spliter.temp_size :
			temp.write(line)
			temp_ind_lst.append(line)
			
		else:
			temp.close()
			spliter.sort_temp(i)
			i=i+1
			temp_ind_lst = []
			print ("writing to:"+'temp_'+str(i))
			temp=open('temp','wb')			
			temp.write(line)
	
	spliter.sort_temp(i)
	print (i+1)			
		
if __name__== '__main__':
	main()
