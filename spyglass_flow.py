import re
import xlsxwriter


#Functions 

##Functions
def nextword(target, source):
    for i, w in enumerate(source):
        if w == target:
            if (not (source[i + 1].__contains__('rst'))) is not None:
                return source[i + 1]
            else:
                return "None"

def port_append(port, pass_op, clk):
    if pass_op == 1:
        if not port in op_fail_list:
            if port in op_pass_list:
                if(op_pass_list[op_pass_list.index(port)+1] != clk):
                   file_log.write("Error: More than one clk for Output port : ")
                   file_log.write(str(port))
            else:
                op_pass_list.append(port)
                op_pass_list.append(clk)
    else:
        op_fail_list.append(port)
        if port in op_pass_list:
            op_pass_list.remove(port)
            op_pass_list.pop(op_pass_list.index(port)+1)

            
def remove_duplicates(list_to_check):
    list_to_check = list(dict.fromkeys(list_to_check))

def extract_signals(list_to_ext, mode):
    list_fin=[];
    if len(list_to_ext) != 0 :
        for item in list_to_ext:
            item=re.sub(' +',' ',item) ## removes multiple spaces
            item = re.sub('[()|^?:;!,-]+', ' ', item)
            item = re.sub('[\(\[].*?[\)\]]+', '', item) # remove bit positions
            item = item.strip()
            if mode == "input": 
                list_fin.insert(len(list_fin), item[5:].strip())
            elif mode== "output":
                if(item.startswith("output reg")):
                    list_fin.insert(len(list_fin), item[10:].strip())
                else:
                    list_fin.insert(len(list_fin), item[6:].strip())
            elif mode == "wire": 
                list_fin.insert(len(list_fin), item[4:].strip())
            elif mode == "logic":
                 list_fin.insert(len(list_fin), item[5:].strip())
            elif mode == "reg":
                list_fin.insert(len(list_fin), item[3:].strip())
    return list_fin



workbook = xlsxwriter.Workbook('Signal_ext.xlsx')


# Clocks list 
clk0_flat_list=[]
clk1_flat_list=[]
clk2_flat_list=[]

file_input_files = open("input_files.txt", "r")
inputfilelines = file_input_files.readlines()


for line in inputfilelines:
    print(line)
    file_name=line.strip()
    textfile = open(file_name, "r")
    textfilelines = textfile.readlines()
    file_log_str=file_name+".txt"
    file_log = open(file_log_str, "w")
    file_log.write("Welcome to Python Spyglass Flow \n")    
    file_log.write("\n#############################################################\n")
    file_log.write("File now is : ")
    file_log.write(str(line))
    file_log.write("\n")
    
    ## get logic, wire, IOs
    textfile_to_str = open(file_name, "r")
    textfilelines_str = textfile_to_str.read()
    pattern = re.compile(r'//[^\n]*|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    textfilelines_str = re.sub(pattern, "", textfilelines_str)

    #####################################################
    pattern = re.compile(r'//[^\n]*|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    textfilelines_str = re.sub(pattern, "", textfilelines_str)

    input_val=re.findall(r"input\s+[\w_0-9]+\s*.*;{1}",textfilelines_str)
    output_val=re.findall(r"output\s+[\w_0-9)]+\s*.*;{1}",textfilelines_str)
    wire_val =re.findall(r"wire\s+[\w_0-9]+\s*.*;{1}",textfilelines_str) 
    reg_val =re.findall(r"reg\s+[\w_0-9]+\s*.*;{1}",textfilelines_str) 
    logic_val =re.findall(r"logic\s+[\w_0-9]+\s*.*;{1}",textfilelines_str) 


    output_val_rw=[item for item in output_val if not '=' in item]

    file_log.write("\n Input statements : \n")
    file_log.write(str(input_val))
    file_log.write("\n")
    file_log.write("\n Output statements : \n")
    file_log.write(str(output_val))
    file_log.write("\n")

    file_log.write("\n Input statements : \n")
    for ip_port in input_val:
        ip_port=re.sub(' +',' ',ip_port) ## removes multiple spaces
        ip_port = re.sub('[()|^?:;!,-]+', ' ', ip_port)
        ip_port = re.sub('[\(\[].*?[\)\]]+', '', ip_port) # remove bit positions
        print(ip_port.strip())

    input_port_list     =   extract_signals(input_val, "input")
    output_port_list    =   extract_signals(output_val, "output")
    wire_port_list      =   extract_signals(wire_val, "wire")
    logic_port_list     =   extract_signals(logic_val, "logic")
    reg_port_list       =   extract_signals(reg_val, "reg")

    file_log.write("\n Input ports  : \n")
    file_log.write(str(input_port_list))
    file_log.write("\n")
    file_log.write("\n Output ports  : \n")
    file_log.write(str(output_port_list))
    file_log.write("\n")
    file_log.write("\n Wire ports  : \n")
    file_log.write(str(wire_port_list))
    file_log.write("\n")
    file_log.write("\n Logic ports  : \n")
    file_log.write(str(logic_port_list))
    file_log.write("\n")
    file_log.write("\n Reg ports  : \n")
    file_log.write(str(reg_port_list))
    file_log.write("\n")
        
       

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
    op_pass_list=[]
    op_fail_list=[]


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
    file_log.write("\nAlways block: Gathering RHS signals... \n")
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
                    if (i == 1):
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
                    clk2_source = 0

                    if (len(dep_signal_list)) != 0:
                        if dep_signal_list[0] in clk_list_tot_0:
                            clk0_source = 1
                            for signal_check in dep_signal_list[1:]:
                                if signal_check.startswith('rgb_') or signal_check.startswith(
                                        'ST_') or "por_n" in signal_check:
                                    # print("signal_check in : ", signal_check)
                                    clk0_source = clk0_source + 1
                                elif (signal_check) in clk_list_tot_0:
                                    clk0_source = clk0_source + 1
                                else:
                                    print("signal not found :", signal_check)
                        elif dep_signal_list[0] in clk_list_tot_1 and (len(clk_list_tot) == 2):
                            clk1_source = 1
                            for signal_check in dep_signal_list[1:]:
                                if signal_check.startswith('rgb_') or signal_check.startswith(
                                        'ST_') or "por_n" in signal_check:
                                    clk1_source = clk1_source + 1
                                elif (signal_check) in clk_list_tot_1:
                                    clk1_source = clk1_source + 1
                                else:
                                    print("signal not found :", signal_check)
                                    
                        elif dep_signal_list[0] in clk_list_tot_2 and (len(clk_list_tot) == 3):
                            clk2_source = 1
                            for signal_check in dep_signal_list[1:]:
                                if signal_check.startswith('rgb_') or signal_check.startswith(
                                        'ST_') or "por_n" in signal_check:
                                    clk2_source = clk2_source + 1
                                elif (signal_check) in clk_list_tot_2:
                                    clk2_source = clk2_source + 1
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
                                      
                        elif (len(dep_signal_list) == clk2_source) and (len(clk_list_tot) == 3):
                            clk_list_tot_2.append(source_signal)
                            if (i == 1):
                                file_log.write("\nClock 2 List is updated: \n")
                                file_log.write(",".join(clk_list_tot_2))
                                file_log.write("\n")

                        else:
                            if (i == 1):
                                file_log.write("\nAsync error in Combo loop : \n")
                                file_log.write(str(source_signal))
                                file_log.write("\n")

    flat_list_0 = list(dict.fromkeys(clk_list_tot_0))
    flat_list_1 = list(dict.fromkeys(clk_list_tot_1))
    flat_list_2 = list(dict.fromkeys(clk_list_tot_2))

    file_log.write("Clock 0 complete list : \n")
    file_log.write(",".join(flat_list_0))
    file_log.write("\n")
    file_log.write("Clock 1 complete list : \n")
    file_log.write(",".join(flat_list_1))
    file_log.write("\n")
    file_log.write("Clock 2 complete list : \n")
    file_log.write(",".join(flat_list_2))
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
                block_dep_num=[]
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
                    #print("BLock dep num in begin :", block_count)

                # Trying to print block -> debug purpose
                # if(block_count != 0):
                #    file_log.write(str(line))
                #    file_log.write("\n")

                if (line.__contains__('end')) and (not line.__contains__('endcase')):
                    # print("block count end line :  ", line)
                    block_count = block_count - 1
                    if (block_count == 0):
                        dept_sig_list = []
                    if(len(block_dep_num) != 0):
                        del dept_sig_list[len(dept_sig_list)-block_dep_num[-1]:]
                        #print("dept sig num after checking : ", block_dep_num)
                    #file_log.write("\ndept sig num after end : " )
                    #file_log.write(str(block_dep_num))
                    #file_log.write("\n")

                signal_word = []
                sig_ext = 0

                if block_run == 1 and line.__contains__('<='):
                    matchObj = re.match(r'\s*(.*)(;).*', line)
                    if matchObj:
                        # print("matchObj.group() : ", matchObj.group(1))
                        line_sp = matchObj.group(1)
                    else:
                        line_sp = line
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
                    line = re.sub('\'+', '&', line)
                    line_sp = re.search('\((.*)\)', line)


                    # print("line sp is : ", line_sp)
                    if line_sp is not None:
                        # print("Inside dep signals attach loop ")
                        # print(line_sp.group(0))
                        line = line_sp.group(1)
                        # print(line)
                        # print(dept_sig_list)
                        if len(dept_sig_list) != 0:
                            line = re.sub('\'+', '&', line)
                            dept_sig_list_new = line.split()
                            #print("new dept list ", dept_sig_list_new)
                            dept_sig_list = dept_sig_list + dept_sig_list_new
                            # print("Previous line dept sig list: ", dept_sig_list)
                        else:
                            dept_sig_list = line.split()
                        if dept_sig_list[0] != "//":
                            #file_log.write(str(dept_sig_list))
                            for x in dept_sig_list:
                                #print("x is :", x)
                                if "=" in x:
                                    dept_sig_list.remove(x)
                                elif "&" in x:
                                    dept_sig_list.remove(x)
                                elif "por" in x:
                                    dept_sig_list.remove(x)

                            #print("dept append after for : ", dept_sig_list)

                            dept_sig_list = [re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", dept_sig_list) for dept_sig_list in
                                             dept_sig_list]
                            # print("dept append : ", dept_sig_list)

                            for dept_sig in dept_sig_list:
                                # print("dept append before : ", dept_sig)
                                if (dept_sig.startswith('P_')):
                                    # print("start with P_")
                                    dept_sig_list.remove(dept_sig)
                                elif len(dept_sig) < 2:
                                    # print("start with P3_")
                                    dept_sig_list.remove(dept_sig)
                                elif ("=" in dept_sig) or ("&" in dept_sig) or ("^" in dept_sig) or ("+" in dept_sig) or (
                                        "<=" in dept_sig) or (
                                        "|" in dept_sig) or ("\"" in dept_sig) or ("por" in dept_sig) or (
                                        dept_sig.startswith('/"')) or (")" in dept_sig):
                                    # print("start with P4_")
                                    dept_sig_list.remove(dept_sig)

                            #file_log.write(str(dept_sig_list))
                            #file_log.write(str(block_dep_num))
                            #file_log.write("\n")
                            #file_log.write(str(len(block_dep_num)))

                            block_dep_num.append(len(dept_sig_list))
                            #print("dept sig num after begin computation : ", block_dep_num)
                            #file_log.write("\ndept sig num after begin computation : " )
                            #file_log.write(str(block_dep_num))
                            #file_log.write("\n")

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
                    fail_signal = 0
                    if (signal_word[0] in flat_list_0) and (signal_word[0] != "//"):
                        for item in signal_word[2:]:
                            #print("item is : ", item)
                            item.strip("(")
                            item = re.sub('[(){},-]+', '', item)
                            item = re.sub('[\(\[].*?[\)\]]+', '', item)

                            # print("item : ", item)
                            if item.isalnum and (not ("+" in item)) and (not "'" in item) and (not "<=" in item) and (
                                    not "meta" in signal_word[0] and not (
                                    item.startswith('rgb_') or item.startswith('ST_') or item.startswith(
                                '=') or "por_n" in item)) and len(item) > 2:
                                #print("item is : ", item)
                                if item in flat_list_0:
                                    # print("Pass: ", item + "         Source: ", signal_word[0])
                                    file_log.write("\nPASS: Source signal :")
                                    file_log.write(str(item))
                                    file_log.write("  Registered signal :")
                                    file_log.write(str(signal_word[0]))
                                    file_log.write("\n")
                                    port_append(signal_word[0], 1, flat_list_0[0])

                                else:
                                    # print("Fail: ", item + "         Source: ", signal_word[0] + "      Clock: ",
                                    file_log.write("\nFAIL: Source signal :")
                                    file_log.write(str(item))
                                    file_log.write("  Registered signal :")
                                    file_log.write(str(signal_word[0]))
                                    file_log.write("  Registered Clock :")
                                    file_log.write(str(clk_list_tot[0]))
                                    file_log.write("\n")
                                    fail_signal = 1
                                    port_append(signal_word[0], 0, flat_list_0[0])

                    elif (signal_word[0] in flat_list_1) and (signal_word[0] != "//") and (len(clk_list_tot) == 2):
                        for item in signal_word[2:]:
                            item = re.sub('[(){},-]+', '', item)
                            item = re.sub('[\(\[].*?[\)\]]+', '', item)
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
                                    port_append(signal_word[0], 1, flat_list_1[0])
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
                                    fail_signal = 1
                                    port_append(signal_word[0], 0, flat_list_1[0])

                    if_block_on = 0


    output_list_f=[]            
    for item in output_port_list:
        print(item)
        if item in flat_list_0:
            output_list_f.append(item)
            output_list_f.append(flat_list_0[0])
        elif item in flat_list_1:
            output_list_f.append(item)
            output_list_f.append(flat_list_1[0])

    logic_list_f=[]
    for item in logic_port_list:
        if item in flat_list_0:
            logic_list_f.append(item)
            logic_list_f.append(flat_list_0[0])
        elif item in flat_list_1:
            logic_list_f.append(item)
            logic_list_f.append(flat_list_1[0]) 
            
    reg_list_f=[]        
    for item in reg_port_list:
        if item in flat_list_0:
            reg_list_f.append(item)
            reg_list_f.append(flat_list_0[0])
        elif item in flat_list_1:
            reg_list_f.append(item)
            reg_list_f.append(flat_list_1[0]) 

    #remoe duplicates
    op_fail_list = list(dict.fromkeys(op_fail_list))
    #op_pass_list = list(dict.fromkeys(op_pass_list))

    file_log.write(" Output Final list :")
    file_log.write(str(output_list_f))
    file_log.write("\n")
    file_log.write(" Output Final pass list :")
    file_log.write(str(op_pass_list))
    file_log.write("\n")
    file_log.write(" Output Final fail list :")
    file_log.write(str(op_fail_list))
    file_log.write("\n")


    # Write the signals of particular module into a separate work sheet 
    worksheet = workbook.add_worksheet(file_name)
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()
    row = 0
    column = 0

    for index in range(int(len(input_port_list))):
        # write operation perform
        worksheet.write(row, column, input_port_list[index], cell_format)
        worksheet.write(row, column+1," ", cell_format)
        worksheet.write(row, column+2,"Input", cell_format)
        row += 1

    for index in range(int(len(op_pass_list)/2)):
        # write operation perform
        worksheet.write(row, column, op_pass_list[index*2], cell_format)
        worksheet.write(row, column+1,op_pass_list[index * 2 + 1], cell_format)
        worksheet.write(row, column+2,"Output", cell_format)
        row += 1
        
    for index in range(int(len(op_fail_list))):
        # write operation perform
        worksheet.write(row, column, op_fail_list[index], cell_format)
        worksheet.write(row, column+1," ", cell_format)
        worksheet.write(row, column+2,"Output", cell_format)
        row += 1
     
    for index in range(int(len(logic_list_f)/2)):
        # write operation perform
        worksheet.write(row, column, logic_list_f[index*2], cell_format)
        worksheet.write(row, column+1,logic_list_f[index * 2 + 1], cell_format)
        worksheet.write(row, column+2,"Wire", cell_format)
        row += 1
        
        
    for index in range(int(len(reg_list_f)/2)):
        # write operation perform
        worksheet.write(row, column, reg_list_f[index*2], cell_format)
        worksheet.write(row, column+1,reg_list_f[index * 2 + 1], cell_format)
        worksheet.write(row, column+2,"reg", cell_format)
        row += 1 


 
    # clk 0 :
    if(len(flat_list_0) > 0): 
     try:
        if flat_list_0[0] in clk0_flat_list or (len(clk0_flat_list) == 0 and len(clk1_flat_list) == 0 and len(clk2_flat_list) == 0):
            file_log.write("\n Clock 0.1 update in process \n")
            clk0_flat_list = clk0_flat_list + flat_list_0
        elif flat_list_0[0] in clk1_flat_list:
            file_log.write("\n Clock 0.2 update in process \n")
            clk1_flat_list = clk1_flat_list + flat_list_0
        elif flat_list_0[0] in clk2_flat_list:
            file_log.write("\n Clock 0.3 update in process \n")
            clk2_flat_list = clk2_flat_list + flat_list_0
        else:
            file_log.write("\nError in Appending signals related to clocks : Clk 0 \n")
     except IndexError:
            file_log.write("\nNo signals to append related to clocks : Clk 0 \n")
        
        
    # clk 1 :
    if(len(flat_list_1) > 0):
     try:
        if flat_list_1[0] in clk0_flat_list :
            file_log.write("\n Clock 1.1 update in process \n")
            clk0_flat_list = clk0_flat_list + flat_list_1
        elif flat_list_1[0] in clk1_flat_list or (len(clk0_flat_list) > 0 and len(clk1_flat_list) == 0 and len(clk2_flat_list) == 0):
            file_log.write("\n Clock 1.2 update in process \n")
            clk1_flat_list = clk1_flat_list + flat_list_1
        elif flat_list_1[0] in clk2_flat_list:
            file_log.write("\n Clock 1.3 update in process \n")
            clk2_flat_list = clk2_flat_list + flat_list_1
        else:
            file_log.write("\nError in Appending signals related to clocks : Clk 1 \n")
     except IndexError:
            file_log.write("\nNo signals to append related to clocks : Clk 1 \n")

    # clk 2 :
    if(len(flat_list_2) > 0): 
     try:
        if flat_list_2[0] in clk0_flat_list :
            file_log.write("\n Clock 2.1 update in process \n")
            clk0_flat_list = clk0_flat_list + flat_list_2
        elif flat_list_2[0] in clk1_flat_list:
            file_log.write("\n Clock 2.2 update in process \n")
            clk1_flat_list = clk1_flat_list + flat_list_2
        elif flat_list_2[0] in clk2_flat_list or (len(clk0_flat_list) > 0 and len(clk1_flat_list) > 0 and len(clk2_flat_list) == 0):
            file_log.write("\n Clock 2.3 update in process \n")
            clk2_flat_list = clk2_flat_list + flat_list_2
        else:
            file_log.write("\nError in Appending signals related to clocks : Clk 2 \n")
     except IndexError:
            file_log.write("\nNo signals to append related to clocks : Clk 2 \n")
             
      
    #clk0_flat_list = list(dict.fromkeys(clk0_flat_list))
    #clk1_flat_list = list(dict.fromkeys(clk1_flat_list))
    #clk2_flat_list = list(dict.fromkeys(clk2_flat_list))


    file_log.write("\n#############################################################\n")

    file_log.write("Inter Clock list : \n")
    file_log.write("Clock 0 list : \n")
    file_log.write(",".join(clk0_flat_list))
    file_log.write("\n")
    file_log.write("Clock 1 list : \n")
    file_log.write(",".join(clk1_flat_list))
    file_log.write("\n")
    file_log.write("Clock 2 list : \n")
    file_log.write(",".join(clk2_flat_list))
    file_log.write("\n")

    ########################################################################################################


workbook.close()
file_input_files.close()
