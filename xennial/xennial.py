import re, os

#features:
# take in.txt and process it into out.txt
# processing includes:
#  - automatically numbering lines
#  - lines after a line that starts with a number are automatically numbered
#  - lines that start with def '\w+' are remembered as a replacement for '\w+', 
#    which can then be used in e.g. goto '\w+'
#  - '\w+'(...) is treated as a function call, and the arguments are automatically numbered
#    e.g.: 
#       999
#       def 'foo' ... -> 1000 ...
#       2000 'foo'(1,r2,3,r5=4,5) -> 2000 r1=1:r3=3:r5=4:r6=5:gosub 1000

linestart=1
linediff=1 #some VERY weird nonsense with =1
_l=linestart
lines=[]
replacement_str=""
replacements={}
with open("C:/Code/reaktor/xennial/in.txt", "r") as in0:
    with open("C:/Code/reaktor/xennial/out.txt", "w") as out0:
        for line in in0:
            if len(line.strip())==0: #if empty do nothing
                lines.append(line)
                continue
            #if line starts with a number, change _l to that number
            m=re.match(r" *(\d+)",line)
            if m:
                _l=int(m.group(1))+linediff
                lines.append(line)
                continue
            #if (stripped) starts with '\w+', add to replacement_str and replacements and remove it.
            m=re.match(r" *(def *('\w+') *)", line)
            line="{0} {1}".format(_l, line)
            if m:
                replacement_str+="{0}|".format(m.group(2))
                replacements[m.group(2)]="{0}".format(_l)
                line=line.replace(m.group(1), "", 1)
            lines.append(line)
            _l+=linediff
        replacement_str="({0})".format(replacement_str.strip("|"))
        # print(replacement_str)
        # print(replacements)
        for i in range(len(lines)):
            #if line has '\w+'( then start consuming text until balanced ) is found.
            #replace all a,b,..., with r1=a:r2=b:...:gosub replacements[\w+]
            #if any start with r\d+= then do not add 
            m=re.compile(r"{0} *\(".format(replacement_str)).search(lines[i])
            while m:
                currpos=m.end()
                args=[]
                argpos=currpos
                depth=1
                while depth>0 and currpos<len(lines[i]):
                    if lines[i][currpos]=="(":
                        depth+=1
                    elif lines[i][currpos]==")":
                        depth-=1
                    elif lines[i][currpos]=="," and depth==1:
                        args.append(lines[i][argpos:currpos])
                        argpos=currpos+1
                    currpos+=1
                if depth!=0:
                    raise Exception("Unbalanced parentheses at {0}".format(i))
                if lines[i][argpos:currpos-1].strip(" ")!="":
                    args.append(lines[i][argpos:currpos-1])
                    argnum=1
                    for argn in range(len(args)):
                        argm=re.match(r" *r(\d+)=", args[argn])
                        if argm:
                            argnum=int(argm.group(1))+1
                        else:
                            args[argn]="r{0}={1}".format(argnum, args[argn])
                            argnum+=1
                args.append("gosub {0}".format(replacements[m.group(1)]))
                lines[i]=lines[i][:m.start()]+":".join(args)+lines[i][currpos:]
                m=re.compile(r"{0} *\(".format(replacement_str)).search(lines[i])
            #replace all instances of the keys in replacements with the values
            m=re.compile(replacement_str).search(lines[i])
            while m:
                # print("found")
                lines[i]=lines[i].replace(m.group(0), replacements[m.group(0)])
                m=re.compile(replacement_str).search(lines[i])

            out0.write(lines[i])
    in0.close()
    out0.close()


