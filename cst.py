#!/usr/bin/python3

#CST:xheger00

import sys
import argparse
import os		
import re	


helpMsg = """--------------------------------------------------------------------------------
Basic statistics for C source files.
Usage: python3 cst.py [--input=FILEORDIR] [--nosubdir] [--output=FILENAME] -k|-o|-i|-w=PATTERN|-c [-p]

--help		-	shows help
--input		-	file or directory to be analyzed
--nosubdir	-	subdirectories won't be searched for files
--output	-	output file
-k		-	number of keywords in the file(s)
-o		-	number of operators in the file(s)
-i		-	number of identificators in the file(s)
-w		-	number of found PATTERNs in the file(s)
-c		-	number of commented characters in the file(s)
-p		-	absoluthe paths of the file(s) won't be included in the output
--------------------------------------------------------------------------------\n"""

keywords = ["auto","break","case","char","const","continue","default","do",
			"double","else","enum","extern","float","for","goto","if","inline",
			"int","long","register","restrict","return","short","signed",
			"sizeof","static","struct","switch","typedef","union","unsigned",
			"void","volatile","while","_Bool","_Complex","_Imaginary"]
			
datatypes = ["char","double","float","int","long","short","signed",
			 "unsigned","_Bool","_Complex","_Imaginary"]

operatorsRegexps = [r"\<\<\=",r"\>\>\=",r"\>\>",r"\<\<",r"\|\|",r"\|\=",
					r"\!\=",r"\^\=",r"\>\=",r"\<\=",r"\+\=",r"\-\=",r"\*\=",
					r"\/\=",r"\%\=",r"\&\=",r"\=\=",r"\-\>",r"\&\&",r"\+\+",
					r"\-\-",r"\+",r"\-",r"\*+",r"\/",r"\%",r"\<",r"\>",r"\!",
					r"\~",r"\&",r"\|",r"\^",r"\=",r"[^\.]\.[^\.]"]


##### Definice funkci #####
#/**
# * Prohledava souborovy system a hleda soubory s priponou *.c nebo *.h.
# * Zacina hledat v adresari na ktery ukazuje promenna path obsahujici 
# * absolutni cestu. V zavislosti jestli byl nastaven parametr --nosubdir, bude
# * nebo nebude prohledavat do hloubky. Cesty k nalezenym souborum uklada do 
# * globalni promenne listOfFiles.
# * @param absolutni cesta adresare, ktery se ma prohledat
# */
def getFileList(path):
	if(args.nosubdir == False):
		for file in os.listdir(path):
			tempPath = os.path.join(path, file)	
			if (file.endswith(".c") or file.endswith(".h")):
				listOfFiles.append(tempPath)
			elif os.path.isdir(tempPath):
				getFileList(tempPath) #Prohledavani do hloubky je rekurzivni

	else:
		for file in os.listdir(path):
			tempPath = os.path.join(path, file)	
			if (file.endswith(".c") or file.endswith(".h")):
				listOfFiles.append(tempPath)
	return

#/**
# * Ve stringu content, ktery dostane jako parametr vyhleda, spocita a odstrani
# * komentare. Radkove komentare nalezne podle ridici sekvence // a odstrani
# * zbytek radku. Blokove komentare odstrani od /* po */ vcetne. Vraci tuple 
# * [string s odstranenimi komentari, pocet znaku v techto komentarich].
# * @param string ze ktereho chceme odstranit a spocitat komentare
# * @return string s odstranenimi komentari
# * @return int s poctem znaku v komentarich
# */
def stripComments(content):
	count = 0
	startPos = 0
	# // komentare
	while(content.find('//', startPos) != -1):
		startPos = content.find('//', startPos)
		endPos = content.find('\n', startPos)
		if(endPos == -1): #Kdyby uz tam nebyl newline(konec souboru)
			endPos = len(content) #Tak to strihni az do konce souboru
		#Kontrola jestli nejsem uprostred retezce	
		tempString = content[0:startPos]
		#Pokud je pocet " do bodu ridici sekvence lichy jsem uprostred retezce
		if((tempString.count('\"') % 2)!=0):
			startPos = endPos #Pokracovat tam kde bych to normalne strihnul
			continue
			
		tempString = content[startPos:endPos]
		count += len(tempString)+1 #Kvuli nestrihani newlinu, rozhaze to soubor
		content = content.replace(tempString, ' ',1)
	
	startPos = 0
	# /**/ komentare
	while(content.find('/*', startPos) != -1):
		startPos = content.find('/*', startPos)
		endPos = content.find('*/', startPos)
		if(endPos == -1): #Kdyby uz tam nebyl newline(konec souboru)
			endPos = len(content) #Tak to strihni az do konce souboru
		#Kontrola jestli nejsem uprostred retezce
		tempString = content[0:startPos]
		#Pokud je pocet " do bodu ridici sekvence lichy jsem uprostred retezce
		if((tempString.count('\"') % 2)!=0):
			startPos = endPos #Pokracovat tam kde bych to normalne strihnul
			continue
		
		tempString = content[startPos:endPos+2]
		count += len(tempString)
		content = content.replace(tempString, ' ',1)
		
	return [content,count]
	
#/**
# * Ve stringu content, ktery dostane jako parametr vyhleda a odstrani makra.
# * Makro nalezne podle znaku # a odstrani zbytek radku vcetne.
# * @param string ze ktereho chceme odstranit makra
# * @return string s odstranenimi makry
# */
def stripMacros(content):
	startPos = 0
	while(content.find('#', startPos) != -1):
		startPos=content.find('#', startPos)
		endPos =content.find('\n', startPos)
		if(endPos == -1):
			endPos = len(content)
		tempString = content[startPos:endPos]
		content = content.replace(tempString, '',1)
			
	return content
	
#/**
# * Ve stringu content, ktery dostane jako parametr vyhleda a odstrani retezce.
# * Retezce nalezne podle dvojice znaku "" a odstrani vse mezi nimi vcetne.
# * @param string ze ktereho chceme odstranit retezce
# * @return string s odstranenimi retezci
# */
def stripStrings(content):
	startPos = 0
	while(content.find('\"', startPos) != -1):
		startPos=content.find('\"', startPos)
		endPos =content.find('\"', startPos+1)
		if(endPos == -1):
			endPos = len(content)
		tempString = content[startPos:endPos+1]
		content = content.replace(tempString, ' ',1)
		
	return content

#/**
# * Ve stringu content, ktery dostane jako parametr vyhleda a odstrani znakove 
# * literaly. Ty nalezne podle dvojice znaku '' a odstrani vse mezi nimi vcetne.
# * @param string ze ktereho chceme odstranit znakove literaly
# * @return string s odstranenimi znakovymi literaly
# */
def stripLits(content):
	startPos = 0
	while(content.find('\'', startPos) != -1):
		startPos=content.find('\'', startPos)
		endPos =content.find('\'', startPos+1)		
		
		if(endPos == -1):
			endPos = len(content)
		tempString = content[startPos:endPos+1]
		content = content.replace(tempString, ' ',1)
	return content
	
#/**
# * Ve stringu content, ktery dostane jako parametr vyhleda a odstrani klicova  
# * slova. Ty nalezne pomoci regularnich vyrazu vytvorenych z listu keywords
# * ktery obsahuje vsechny klicova slova C99.
# * @param string ze ktereho chceme odstranit klicova slova
# * @return string s odstranenimi klicovymi slovy
# */	
def stripKeywords(content):
	for keyword in keywords:
			regexp = r"\W?" + keyword + r"\W"
			content = re.sub(regexp, ' ', content)
	return content
	
#/**
# * BETA verze
# * Ve stringu content, ktery dostane jako parametr vyhleda a odstrani  
# * deklarace na pointery a zakladni tvary ciselnych konstant. Ty nalezne  
# * pomoci regularnich vyrazu. Pro jednoduche datove typy se vytvareji
# * regularni vyrazy z listu datatypes. Struct ma vlastni regexp. Ciselne
# * konstanty to najde jenom v nekterych tvarech.
# * @param string ze ktereho chceme odstranit deklarace a ciselne konstanty
# * @return string s odstranenimi deklaracemi a ciselnymi konstantami
# */
def stripDeclarations(content):
	tempList = list()
	for datatype in datatypes:
			#regexp na hledani deklaraci pointeru jednoduchych datovych typu
			regexp = datatype + r"\s*\(?\*+\s*[a-zA-Z_]+?\w*"
			tempList = re.findall(regexp, content, flags=re.IGNORECASE)
			for item in tempList:
				content = content.replace(item, '',1)
			
	#regexp na hledani deklaraci pointeru na structy			
	regexp = "struct\s+[a-zA-Z_]+?\w*\s*\*\s*[a-zA-Z_]+?\w*" 
	tempList = re.findall(regexp, content, flags=re.IGNORECASE)
	for item in tempList:
		content = content.replace(item, '',1)
	
	#regexp na hledani jednoduchych ciselnych konstant
	regexp = "[.]?[0-9]*[eE][\+|\-]?[0-9]+[fFlL]?" 
	tempList = re.findall(regexp, content, flags=re.IGNORECASE)
	for item in tempList:
		content = content.replace(item, '',1) 
	
	return content
				
###### Zacatek Programu ######

#Zadny parametr
if(len(sys.argv)==1):
	sys.stdout.write(helpMsg)
	sys.exit(1)

#Jeden parametr a to --help
if(len(sys.argv)==2 and sys.argv[1] == '--help'):
	sys.stdout.write(helpMsg)
	sys.exit(0)

#Vytvoreni tridy dedicnosti z argparse, kvuli vlastnim chybam
class MyParser(argparse.ArgumentParser):
	def error(self, message):
		raise SystemExit 

parser = MyParser(add_help=False)
parser.add_argument('--help',action='store_true')
parser.add_argument('--input', nargs=1)
parser.add_argument('--nosubdir',action='store_true')
parser.add_argument('--output', nargs=1)
parser.add_argument('-k',action='count')
parser.add_argument('-o',action='count')
parser.add_argument('-i',action='count')
parser.add_argument('-w', nargs=1, action='append')
parser.add_argument('-c',action='count')
parser.add_argument('-p',action='count')

#Inicializace flagu
kFlag = 0
oFlag = 0
iFlag = 0
wFlag = 0
cFlag = 0
dirFlag = 1 #Kvuli chyba 21, nastavi se na 0 pokud cilem je jedinny soubor

try:
	args = parser.parse_args()
	#Pokud byl nastaven help, err1, help muze byt pouze kdyz je volan sam
	if(args.help == True):
		raise SystemExit
	#Pokud byl parametr pouzit, ulozi se do flagu pocet kolikrat byl pouzit
	if(args.k != None): 
		kFlag = args.k
	if(args.o != None):
		oFlag = args.o
	if(args.i != None):
		iFlag = args.i
	if(args.w != None):
		wFlag = len(args.w)
	if(args.c != None):
		cFlag = args.c
	#Pokud je soucet flagu rozdilny od jedne(tzn. nebyl pouzit zadny nebo vic)
	if((kFlag+oFlag+iFlag+wFlag+cFlag)!= 1): 
		raise SystemExit
	#Pokud je nastaven parametr -p vic nez jednou
	if((args.p != None) and args.p > 1):
		raise SystemExit
except:
	sys.stderr.write("Wrong script arguments.\n")
	sys.exit(1)
  

listOfFiles = list() #Seznam s cestami k validnim souborum

#Hledani validnich souboru
if(args.input == None): #Cil je cwd
	cwd = os.getcwd()
	getFileList(cwd) 
else:
	absPathInput = os.path.abspath(args.input[0])
	if(os.path.isfile(absPathInput)): #Cil je soubor
		#Kombinace --nosubdiru a zadaneho souboru, chyba
		if(args.nosubdir == True):
			sys.stderr.write("Wrong script arguments. --nosubstring cannot be entered when targeting a single file.\n")
			sys.exit(1)
		else:
			dirFlag = 0
			listOfFiles.append(absPathInput)
			
	elif(os.path.isdir(absPathInput)): #Cil je adresar
			getFileList(absPathInput)
	else:
		sys.stderr.write("Failed to locate the file/directory.\n")
		sys.exit(2)

		
contentOfFiles = list() #Obsahy nalezenych souboru
		
### Otevirani souboru ###
for file in listOfFiles:
	try:
		fileHandle = open(file, 'r', encoding='ISO-8859-2')
		contentOfFiles.append(fileHandle.read())
		fileHandle.close()
	except:
		if(dirFlag == 1):
			sys.stderr.write("Failed to open one of the input files.\n")
			sys.exit(21)
		else:
			sys.stderr.write("Failed to open the input file.\n")
			sys.exit(2)


##### Hlavni zpracovani #####
resultsList = list() #List s vysledky
tempList = list()
count = 0

#Odstraneni "\\n(backslash + newline)" ze vsech souboru
for content in contentOfFiles:
	content = content.replace('\\\n', '')
	tempList.append(content)

	
#Parametr -w
if(wFlag == 1):
	for content in tempList:
		count = content.count(args.w[0][0]) #Obsah -w je ulozen v listu listu
		resultsList.append(count) #Ulozeni vysledku do listu
		
		
#Parametr -c
elif(cFlag == 1):
	for content in tempList:
		tempString,count = stripComments(content)
		resultsList.append(count)

	
#Parametr -k
#Odstrani se retezce, komentare, makra a pomoci
#regexpu se vyhledaji klicova slova.
elif(kFlag == 1):
	for content in tempList:
		tempString = stripStrings(content)
		tempString, tempInt = stripComments(tempString)		
		tempString = stripMacros(tempString)		
		for keyword in keywords:
			regexp = r"\W?" + keyword + r"\W"
			keywordList = re.findall(regexp, tempString)						
			count += len(keywordList)

		resultsList.append(count)
		count = 0	
		
	
#Parametr -i
#Odstrani se retezce, znakove literaly, komentare, makra, klicova slova,
#deklarace a ciselne konstanty. Zustat by meli akorat identifikatory.
elif(iFlag == 1):
	regexp = r"[a-zA-Z_]+\w*" #Regexp na identifikatory
	for content in tempList:
		tempString = stripStrings(content)
		tempString = stripLits(tempString)
		tempString, tempInt = stripComments(tempString)		
		tempString = stripMacros(tempString)
		tempString = stripKeywords(tempString)
		identifierList = re.findall(regexp, tempString)
		count = len(identifierList)
		resultsList.append(count)

		
#Parametr -o
#Odstrani se retezce, znakove literaly, komentare, makra,deklarace a 
#ciselne konstanty. Potom se za pomoci regexpu pro opeatory
#naleznou vsechny operatory a zaroven se odstrani(aby se neprekryvali).
elif(oFlag == 1):	
	for content in tempList:
		tempString = stripStrings(content)
		tempString = stripLits(tempString)
		tempString = stripDeclarations(tempString)
		tempString, tempInt = stripComments(tempString)
		tempString = stripMacros(tempString)
		for regexp in operatorsRegexps:
			tempString,tempInt = re.subn(regexp, '', tempString)
			count += tempInt
		resultsList.append(count)		
		count = 0	

#### TISK-related zalezitosti ####	

#Pokud parametr -p vymazou se absolutni cesty
if(args.p == True):
	tempList = []
	for file in listOfFiles:
		tempList.append(file[(file.rfind('/')+1):])
	listOfFiles = tempList

#Pripsani vysledku k cestam souboru
tempList = []
i = 0
for file in listOfFiles:
	tempString = str(file) + ' ' + str(resultsList[i])
	tempList.append(tempString)
	i += 1
	
#Pripsani CELKEM
tempString = "CELKEM:" + ' ' + str(sum(resultsList))
tempList.append(tempString)

#Nejdelsi retezec, je potreba k urceni spravneho poctu mezer
maxLen = 0
for file in tempList:
	if(len(file) > maxLen):
		maxLen = len(file)

#Pridani mezer
finalResultsList = list()
for file in tempList:
	difference = maxLen - len(file) #Rozdil mezi nejdelsim radkem a aktualnim
	spaceString = ''
	for i in range(0,difference): #Pridavani mezer
		spaceString = spaceString + ' '
	spacePos = file.find(' ') #Nalezeni mezery = kam pridat dalsi mezery
	finalResultsList.append(file[:spacePos] + spaceString + file[spacePos:])

#Odstraneni CELKEM ze seznamu(nesmi tam byt kvuli razeni)
tempStr = finalResultsList.pop(len(finalResultsList)-1)
#Sort
finalResultsList.sort()
#Vraceni CELKEM na konec
finalResultsList.append(tempStr)

if(args.output != None): #Pokud je nastaven --output
	absPathOutput = os.path.abspath(args.output[0]) #absolutni cesta
	try:
		fileHandle = open(absPathOutput, 'w', encoding='ISO-8859-2')
	except:
		sys.stderr.write("Failed to open ouput file.\n")
		sys.exit(3)
else: #Jinak je vypis na standartni vystup
	fileHandle = sys.stdout

	
#### TISK ####
for file in finalResultsList:
	tempString = file + "\n"
	fileHandle.write(tempString)

fileHandle.close()
sys.exit(0)				
###### KONEC ######
