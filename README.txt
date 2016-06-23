# cst.py
python3 School assigment

documentation: CST-doc.pdf

--------------------------------------------------------------------------------
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
--------------------------------------------------------------------------------
