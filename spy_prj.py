# import pandas as pd
import itertools
import re

file_log = open("aon_osc_wakeup.txt", "w")
file_log.write("Welcome to Python Spyglass Flow \n")

file_log_str = open("aon_osc_wakeup_string.txt", "w")


# file_log.write("Welcome to Python Spyglass Flow \n")

##Functions
def nextword(target, source):
    for i, w in enumerate(source):
        if w == target:
            if (not (source[i + 1].__contains__('rst'))) is not None:
                return source[i + 1]
            else:
                return "None"


# Open file and read lines
textfile = open("aon_osc_wakeup.v", "r")
textfilelines = textfile.readlines()
textfile_to_str = open("aon_osc_wakeup.v", "r")
textfilelines_str = textfile_to_str.read()
pattern = re.compile(r'//[^\n]*|/\*.*?\*/', re.DOTALL | re.MULTILINE)
textfilelines_str = re.sub(pattern, "", textfilelines_str)
#file_log_str.write("Welcome")
#file_log_str.write(textfilelines_str)

assign_val=re.findall(r"assign\s+[\w_0-9]+\s*.*;{1}",textfilelines_str)

#always_var=re.findall(r"always\s+[^assign|endmodule|always]*$",textfilelines_str)
always_var=re.findall(r"always\s+(?:(?!always|assign|endmodule).)*",textfilelines_str, re.DOTALL)

file_log_str.write("\n Assign statements : \n")
file_log_str.write(str(assign_val))

file_log_str.write("\n Always Block : \n")
file_log_str.write(str(always_var))

#for always_stmt in always_var:
    #always_stmt_sp=re.sub(' +',' ',always_stmt) ## removes multiple spaces
    #print(always_stmt_sp)




#for alwys_stmt in always_var:
  #  alwys_stmt_sp=re.sub(' +',' ',alwys_stmt) ## removes multiple spaces
   # alwys_stmt_sp=re.sub(r'\n\s*\n', '\n\n',alwys_stmt_sp)
  #  print(alwys_stmt_sp)


############################################################################ Old section
# Declarations
always_blk_found = 0
clk_domain = ""
none_clk = "''"
block_count = 0
block_run = 0
if_block_on = 0
signal_word = []

clk_list = []
clk_list_tot = []
clk_list_tot_0 = []
clk_list_tot_1 = []
clk_list_tot_2 = []
flat_list_0 = []
flat_list_1 = []

for line in textfilelines:
    # Remove white spaces & comment sections in the line 
    line = line.strip()
    matchObj = re.match(r'\s*(.*)(//).*', line)
    if matchObj:
        # file_log.write("matchObj.group() : ")
        # file_log.write(str(matchObj.group(1)))
        line = matchObj.group(1)
    else:
        line = line

    if line.__contains__('always') and (not (line.__contains__('*'))) and line.__contains__('posedge'):
        file_log.write("line now is : ")
        file_log.write(str(line))
        file_log.write("\n")
        clk_domain_tot = line.split("posedge", 1)[1].split()[0]
        # print("line: ", line)
        clk_list_tot.append(clk_domain_tot)

# Remove duplicates 
clk_list_tot = list(dict.fromkeys(clk_list_tot))

file_log.write("Clocks used in module : ")
file_log.write(str(clk_list_tot))
file_log.write("\n")
file_log.write("No. of Clocks : ")
file_log.write(str(len(clk_list_tot)))
file_log.write("\n")

if (len(clk_list_tot) == 1):
    clk_list_tot_0.append(clk_list_tot[0])
elif (len(clk_list_tot) == 2):
    clk_list_tot_1.append(clk_list_tot[1])
elif (len(clk_list_tot) == 3):
    clk_list_tot_2.append(clk_list_tot[2])
elif (len(clk_list_tot) == 0):
    file_log.write("No clocks were used in this module\n")

#################################
# Gather all signals in RHS#####
#################################
# Always block 
file_log.write("\nAlwyas block: Gathering RHS signals... \n")
for line in textfilelines:
    line = line.strip()
    if not (line.startswith('//')):
        matchObj = re.match(r'\s*(.*)(//).*', line)
        if matchObj:
            # file_log.write("matchObj.group() : ")
            # file_log.write(str(matchObj.group(1)))
            line = matchObj.group(1)
        else:
            line = line

        # always line execution
        if "always" in line and (not (line.__contains__('*'))) and line.__contains__('posedge'):
            always_blk_found = 1
            clk_domain = line.split("posedge", 1)[1].split()[0]
            # file_log.write("clk domain is : ")
            # file_log.write(str(clk_domain))
            clk_list.append(clk_domain)
            clk_list = list(dict.fromkeys(clk_list))

        if always_blk_found == 1 and (clk_domain is not None):
            if line.__contains__('begin'):
                block_count = block_count + 1
                block_run = 1

            if (line.__contains__('end')) and (not line.__contains__('endcase')):
                block_count = block_count - 1

            # Append the reg signal (in RHS) to the total CLk list 
            if block_run == 1 and line.__contains__('<='):
                line_sp = line.split()
                signal = line_sp[0].split()
                signal[0] = re.sub('[\(\[].*?[\)\]]+', '', signal[0])
                clk_list.append(signal[0])

            # At the end of block, remove the duplicates in clk_list array and attach it to corresponding to total clk list. Reset the list, blk related variables 
            if block_count == 0 and block_run == 1 and always_blk_found == 1:
                clk_list = list(dict.fromkeys(clk_list))
                if clk_list_tot[0] in clk_list:
                    clk_list_tot_0 = clk_list_tot_0 + clk_list
                elif (clk_list_tot[1] in clk_list) and len(clk_list_tot) == 2:
                    clk_list_tot_1 = clk_list_tot_1 + clk_list
                always_blk_found = 0
                block_run = 0
                clk_list = []

if (len(clk_list_tot) == 1):
    clk_list_tot_0 = list(dict.fromkeys(clk_list_tot_0))
    file_log.write("\nSignals & clk in first domain:\n")
    file_log.write(str(clk_list_tot_0))
    file_log.write("\n")
elif (len(clk_list_tot) == 2):
    clk_list_tot_0 = list(dict.fromkeys(clk_list_tot_0))
    clk_list_tot_1 = list(dict.fromkeys(clk_list_tot_1))
    file_log.write("\nSignals & clk in first domain:\n")
    file_log.write(str(clk_list_tot_0))
    file_log.write("\n")
    file_log.write("\nSignals & clk in Second domain:\n")
    file_log.write(str(clk_list_tot_1))
elif (len(clk_list_tot) == 3):
    clk_list_tot_0 = list(dict.fromkeys(clk_list_tot_0))
    clk_list_tot_1 = list(dict.fromkeys(clk_list_tot_1))
    clk_list_tot_2 = list(dict.fromkeys(clk_list_tot_2))
    file_log.write("\nSignals & clk in first domain:\n")
    file_log.write(str(clk_list_tot_0))
    file_log.write("\n")
    file_log.write("\nSignals & clk in Second domain:\n")
    file_log.write(str(clk_list_tot_1))
    file_log.write("\n")
    file_log.write("\nSignals & clk in Third domain:\n")
    file_log.write(str(clk_list_tot_2))
    file_log.write("\n")
elif (len(clk_list_tot) == 0):
    file_log.write("\nNo clocks were used in this module\n")
    file_log.write("\n")

file_log.write("\n#############################################################\n")


#for asgn_stmt in assign_val:
#    asgn_stmt_sp=re.sub(' +',' ',asgn_stmt) ## removes multiple spaces
#    asgn_stmt_sp = re.sub('[()=|&^?:;!,-]+', ' ', asgn_stmt_sp)
#    asgn_stmt_sp = re.sub('[\(\[].*?[\)\]]+', '', asgn_stmt_sp) # remove bit positions
#    print(asgn_stmt_sp.split()[1:])

#    for item in asgn_stmt_sp.split()[2:]:
#        print(item)
#        if item in clk_list_tot_0:
#            print("clk_list_tot_0")
#        elif item in clk_list_tot_1:
#            print("clk_list_tot_1")
#        else:
#            print("is missing")


# assign statements
file_log.write("Assign Statements: Gathering RHS signals & checking for CDC... \n")
for i in range(2):
 for line in textfilelines:
    line = line.strip()
    if not (line.startswith('//')):
        matchObj = re.match(r'\s*(.*)(//).*', line)
        if matchObj:
            # file_log.write("matchObj.group() : ")
            # file_log.write(str(matchObj.group(1)))
            line = matchObj.group(1)
        else:
            line = line

        # assign statement section
        if "assign" in line:
            file_log.write("\n#############################################################\n")
            assign_blk_found = 1;
            dep_signal = []
            dep_signal_list = []
            line = line.split(";")[0]
            line = line.strip()
            if(i == 1):
                file_log.write("Assign statement : \n")
                file_log.write("           ")
                file_log.write(line)
            line = list(line.split(" "))
            temp_list = line
            # Remove empty list items
            line = list(filter(None, temp_list))
            source_signal = line[1]
            source_signal = re.sub('[\(\[].*,?[\)\]]+', '', source_signal)
            dep_signal = line[3:]
            # print(line)
            if dep_signal is not None:
                for indiv_signal in dep_signal:
                    # print("indiv signal", indiv_signal)
                    indiv_signal = re.sub('[()=|&^?:!,-]+', '', indiv_signal)
                    # print("indiv signal", indiv_signal)
                    indiv_signal = re.sub('[(){}-]+', '', indiv_signal)
                    indiv_signal = re.sub('[\(\[].*?[\)\]]+', '', indiv_signal)

                    # indiv_signal = re.sub('[" "]+', '', indiv_signal)
                    # print(indiv_signal)
                    if indiv_signal and not indiv_signal[
                                            :1].isdigit() and not "+" in indiv_signal and not "-" in indiv_signal:
                        # print("indiv signal 2 ", indiv_signal)
                        if not (
                                '!' in indiv_signal or '^' in indiv_signal or '&' in indiv_signal or '<' in indiv_signal or '>' in indiv_signal):
                            # print("inside", indiv_signal)
                            indiv_signal = re.sub('[~]+', '', indiv_signal)
                            dep_signal_list.append(indiv_signal)
            if (i == 1):
                file_log.write("\n\nSource signal list : ")
                file_log.write(str(source_signal))
                file_log.write("\n")
            # print(source_signal)
            # print("dep signal : ", dep_signal_list)

            if (len(dep_signal_list)) != 0:
                if (i == 1):
                    file_log.write("\nDependant signal list : ")
                    file_log.write("\n".join(dep_signal_list))
                    file_log.write("\n")
            else:
                if (i == 1):
                    file_log.write("\nNo dependency ")
                    file_log.write("\n")

            clk0_source = 0
            clk1_source = 0
            if (len(dep_signal_list)) != 0:
                if dep_signal_list[0] in clk_list_tot_0:
                    clk0_source = 1
                    for signal_check in dep_signal_list[1:]:
                        if signal_check.startswith('rgb_') or signal_check.startswith('ST_') or "por_n" in signal_check:
                            # print("signal_check in : ", signal_check)
                            clk0_source = clk0_source + 1
                        elif (signal_check) in clk_list_tot_0:
                            clk0_source = clk0_source + 1
                        else:
                            print("signal not found :", signal_check)
                elif dep_signal_list[0] in clk_list_tot_1 and (len(clk_list_tot) == 2):
                    clk1_source = 1
                    for signal_check in dep_signal_list[1:]:
                        if signal_check.startswith('rgb_') or signal_check.startswith('ST_') or "por_n" in signal_check:
                            clk1_source = clk1_source + 1
                        elif (signal_check) in clk_list_tot_1:
                            clk1_source = clk1_source + 1
                        else:
                            print("signal not found :", signal_check)
                file_log.write("\n")
                if (len(dep_signal_list) == clk0_source):
                    clk_list_tot_0.append(source_signal)
                    if (i == 1):
                        file_log.write("\nClock 0 List is updated: \n")
                        file_log.write(" ".join(clk_list_tot_0))
                        file_log.write("\n")

                elif (len(dep_signal_list) == clk1_source) and (len(clk_list_tot) == 2):
                    clk_list_tot_1.append(source_signal)
                    if (i == 1):
                        file_log.write("\nClock 1 List is updated: \n")
                        file_log.write(",".join(clk_list_tot_1))
                        file_log.write("\n")

                else:
                    if (i == 1):
                        file_log.write("\nAsync error in Combo loop : \n")
                        file_log.write(str(source_signal))
                        file_log.write("\n")

file_log.write("\n####################################################\n")

flat_list_0 = list(dict.fromkeys(clk_list_tot_0))
flat_list_1 = list(dict.fromkeys(clk_list_tot_1))

file_log.write("Clock 0 complete list : \n")
file_log.write(",".join(flat_list_0))
file_log.write("\n")
file_log.write("Clock 1 complete list : \n")
file_log.write(",".join(flat_list_1))
file_log.write("\n")

file_log.write("\n##########################\n")
file_log.write("Checking CDC starts here \n")
file_log.write("\n##########################\n")

dept_list = []
dept_sig_list = []

regex = re.compile('0123456789')

# Right side of always block and comparison
for line in textfilelines:

    line = line.strip()
    # print("line is : ", line)
    if not (line.startswith('//')):
        matchObj = re.match(r'\s*(.*)(//).*', line)
        if matchObj:
            line = matchObj.group(1)
        else:
            line = line
        if "always" in line and (not (line.__contains__('*'))) and line.__contains__('posedge'):
            file_log.write("\n#############################################################\n")
            always_blk_found = 1
            clk_domain = line.split("posedge", 1)[1].split()[0]
            # print("clk domain is: ", clk_domain)
            clk_list.append(clk_domain)
            # print("clk domain : ", clk_domain)
            clk_list = list(dict.fromkeys(clk_list))
            # print("clk list : ", clk_list)

        if always_blk_found == 1 and (clk_domain is not None):
            if line.__contains__('begin'):
                # print("block count begin line :  ", line)
                block_count = block_count + 1
                block_run = 1
                # print("BLock count  in begin :", block_count)

            # Trying to print block -> debug purpose
            # if(block_count != 0):
            #    file_log.write(str(line))
            #    file_log.write("\n")

            if (line.__contains__('end')) and (not line.__contains__('endcase')):
                # print("block count end line :  ", line)
                block_count = block_count - 1
                if (block_count == 0):
                    dept_sig_list = []
                # print("BLock count  in end :", block_count)

            signal_word = []
            sig_ext = 0

            if block_run == 1 and line.__contains__('<='):
                matchObj = re.match(r'\s*(.*)(;).*', line)
                if matchObj:
                    # print("matchObj.group() : ", matchObj.group(1))
                    line_sp = matchObj.group(1)
                else:
                    line_sp = line
                # print("Line conta. <= :  ", line_sp)
                # line_sp = re.sub('[()=|&^?:!-]+', '', line_sp)
                # print("indiv signal", indiv_signal)
                # line_sp = re.sub('[(){}-]+', '', line_sp)
                # line_sp = re.sub('[\(\[].*?[\)\]]+', '', line_sp)
                signal = line_sp.split()
                # signal_word = []
                # print("<= line split : ", line_sp)

                for word in signal:
                    signal_word.append(word)
                    # print("signal_word is" , signal_word)

                if dept_sig_list is not None:
                    # print("dept append initial : ", dept_sig_list)
                    for dept_append in dept_sig_list:
                        if not ("<=" in dept_append) and not dept_append.startswith('P_') and not len(dept_append) < 2:
                            signal_word.append(dept_append)
                        # print("dept append : ", dept_append)
                sig_ext = 1

            if block_run == 1 and (line.__contains__('else') or line.__contains__('if')):
                if_block_on = 1

            if (if_block_on == 1) and (not (line.__contains__('<=')) and (not (line.startswith('//')))):
                # print("line is ", line)
                # line = line.strip('(')
                line_sp = re.search('\((.*)\)', line)

                # handle diff. symbols inlsit
                # line_sp = re.sub('[(){}-]+', '', line_sp)
                # line_sp = re.sub('[\(\[].*?[\)\]]+', '', line_sp)
                # line_sp.replace("<", "")

                # print("line sp is : ", line_sp)
                if line_sp is not None:
                    # print("Inside dep signals attach loop ")
                    # print(line_sp.group(0))
                    line = line_sp.group(1)
                    # print(line)
                    # print(dept_sig_list)
                    if len(dept_sig_list) != 0:
                        # print("Previous line dept sig list: ", dept_sig_list)
                        dept_sig_list_new = line.split()
                        dept_sig_list = dept_sig_list + dept_sig_list_new
                        # print("Previous line dept sig list: ", dept_sig_list)
                    else:
                        dept_sig_list = line.split()
                    # print("dept_sig_list is ", dept_sig_list)
                    if dept_sig_list[0] != "//":
                        # print("dept sig list :" , dept_sig_list)
                        for x in dept_sig_list:
                            # x = x.replace("<", " ")
                            # x = x.replace(">", " ")
                            # print("x is : ", x)
                            if "=" in x:
                                # print("x 1  is : ", x)
                                dept_sig_list.remove(x)
                            elif '\'' in x:
                                # print("x 2  is : ", x)
                                dept_sig_list.remove(x)
                            # elif x.isalpha():
                            # print("x 3  is : ", x)
                            # dept_sig_list.remove(x)
                            # print("x is : ", x)

                        # print("dept append after for : ", dept_sig_list)

                        # for characters in dept_sig_list:
                        # if not (any(characters.isalpha() for char in characters)):
                        #   dept_sig_list.remove(characters)
                        # print("dept append before for : ", dept_sig_list)
                        dept_sig_list = [re.sub(r"[-()\"#/@;:<>&{}`+=~|.!?,]", "", dept_sig_list) for dept_sig_list in
                                         dept_sig_list]
                        # print("dept append : ", dept_sig_list)

                        for dept_sig in dept_sig_list:
                            # print("dept append before : ", dept_sig)
                            if (dept_sig.startswith('P_')):
                                # print("start with P_")
                                dept_sig_list.remove(dept_sig)
                                # print(dep_signal_list)
                            # elif dept_sig.isnumeric:
                            # print("start with P2_")
                            # dept_sig_list.remove(dept_sig)
                            elif len(dept_sig) < 2:
                                # print("start with P3_")
                                dept_sig_list.remove(dept_sig)
                            elif ("=" in dept_sig) or ("&" in dept_sig) or ("^" in dept_sig) or ("+" in dept_sig) or (
                                    "<=" in dept_sig) or (
                                    "|" in dept_sig) or ("\"" in dept_sig) or ("por" in dept_sig) or (
                                    dept_sig.startswith('/"')) or (")" in dept_sig):
                                # print("start with P4_")
                                dept_sig_list.remove(dept_sig)

                        # print("dept sig after checking : ", dept_sig_list)

            if block_count == 0 and block_run == 1 and always_blk_found == 1:
                clk_list = list(dict.fromkeys(clk_list))
                # print("block count: " , block_count)
                if clk_list_tot[0] in clk_list:
                    clk_list_tot_0.append(clk_list)
                elif clk_list_tot[1] in clk_list:
                    clk_list_tot_1.append(clk_list)
                always_blk_found = 0
                block_run = 0
                if_block_on = 0
                clk_list = []
                dept_list = []
                dept_sig_list = []

            if sig_ext == 1:
                # print("Block signals :", signal_word)
                file_log.write("\nBlock signals :")
                file_log.write(",".join(signal_word))
                signal_word[0] = re.sub('[\(\[].*?[\)\]]+', '', signal_word[0])
                if (signal_word[0] in flat_list_0) and (signal_word[0] != "//"):
                    for item in signal_word[2:]:
                        item.strip("(")
                        item = re.sub('[(){},-]+', '', item)
                        item = re.sub('[\(\[].*?[\)\]]+', '', item)

                        # print("item : ", item)
                        if item.isalnum and (not ("+" in item)) and (not "'" in item) and (not "<=" in item) and (
                                not "meta" in signal_word[0] and not (
                                item.startswith('rgb_') or item.startswith('ST_') or item.startswith(
                            '=') or "por_n" in item)) and len(item) > 2:
                            # print(item)
                            if item in flat_list_0:
                                # print("Pass: ", item + "         Source: ", signal_word[0])
                                file_log.write("\nPASS: Source signal :")
                                file_log.write(str(item))
                                file_log.write("  Registered signal :")
                                file_log.write(str(signal_word[0]))
                                file_log.write("\n")


                            else:
                                # print("Fail: ", item + "         Source: ", signal_word[0] + "      Clock: ",
                                file_log.write("\nFAIL: Source signal :")
                                file_log.write(str(item))
                                file_log.write("  Registered signal :")
                                file_log.write(str(signal_word[0]))
                                file_log.write("  Registered Clock :")
                                file_log.write(str(clk_list_tot[0]))
                                file_log.write("\n")

                elif (signal_word[0] in flat_list_1) and (signal_word[0] != "//") and (len(clk_list_tot) == 2):
                    for item in signal_word[2:]:
                        item = re.sub('[(){},-]+', '', item)
                        item = re.sub('[\(\[].*?[\)\]]+', '', item)
                        # print(item_temp)
                        if item.isalnum and (not ("+" in item)) and (not "'" in item) and (not "<=" in item) and (
                                not "meta" in signal_word[0] and not (
                                item.startswith('rgb_') or item.startswith('ST_') or item.startswith(
                            '=') or "por_n" in item)) and len(item) > 2:
                            # print(item)
                            if item in flat_list_1:
                                # print("Pass: ", item + "         Source: ", signal_word[0])
                                file_log.write("\nPASS: Source signal :")
                                file_log.write(str(item))
                                file_log.write("  Registered signal :")
                                file_log.write(str(signal_word[0]))
                                file_log.write("\n")
                            else:
                                # print("Fail: ", item + "         Source: ", signal_word[0] + "      Clock: ",
                                file_log.write("\nFAIL: Source signal :")
                                file_log.write(str(item))
                                file_log.write("  Registered signal :")
                                file_log.write(str(signal_word[0]))
                                file_log.write("\n")
                                file_log.write("  Registered Clock :")
                                file_log.write(str(clk_list_tot[1]))
                                file_log.write("\n")

                if_block_on = 0
                # signal_word=[]
textfile.close()
file_log.close()
file_log_str.close()
