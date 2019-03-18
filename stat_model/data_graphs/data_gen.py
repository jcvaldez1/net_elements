import sys
import ast

def gen_input(tuple_list):
    x = []
    y = []

    for theTuple in tuple_list:
        x.append(theTuple[1])
        y.append(theTuple[2])

    return x,y

def str_process( dict_vals, key_list):
    headers = " ".join(key_list) + "\n"
    length = len(dict_vals[key_list[0]])
    for x in range(0,length):
        if x == 0:
            stringy = ""
            for y in range(0,len(key_list)):
                stringy = stringy + "0 "   
            headers = headers + stringy + "\n"
                    
        stringy = ""
        for y in key_list:
            try:
                stringy = stringy + str(dict_vals[y][x]) + " "   
            except:
                stringy = stringy + " "
        headers = headers + stringy + "\n"
    print(headers)
    pass



def generate(gen_file, syn_file):
    
    gen = open(gen_file, "r")
    syn = open(syn_file, "r")
    
    gen_list = gen.read()
    gen_split = gen_list.split('$')
    GENresponseDistrib   = ast.literal_eval(gen_split[0])
    GENrequestDistrib    = ast.literal_eval(gen_split[1])
    GENdelayDistrib      = ast.literal_eval(gen_split[2])

    syn_list = syn.read()
    syn_split = syn_list.split('$')
    SYNresponseDistrib   = ast.literal_eval(syn_split[0])
    SYNrequestDistrib    = ast.literal_eval(syn_split[1])
    SYNdelayDistrib      = ast.literal_eval(syn_split[2])

    gen_req_x, gen_req_y = gen_input( GENrequestDistrib)
    syn_req_x ,syn_req_y = gen_input( SYNrequestDistrib)
    temp_list = ['gen_req_x', 'gen_req_y', 'syn_req_x', 'syn_req_y']
    temp_dict = {'gen_req_x':gen_req_x, 'gen_req_y':gen_req_y, 'syn_req_x':syn_req_x, 'syn_req_y':syn_req_y}
    str_process( temp_dict, temp_list[0:2])
    str_process( temp_dict, temp_list[2:4])
    
    gen_res_x, gen_res_y = gen_input( GENresponseDistrib)
    syn_res_x ,syn_res_y = gen_input( SYNresponseDistrib)
    temp_list = ['gen_res_x', 'gen_res_y', 'syn_res_x', 'syn_res_y']
    temp_dict = {'gen_res_x':gen_res_x, 'gen_res_y':gen_res_y, 'syn_res_x':syn_res_x, 'syn_res_y':syn_res_y}
    str_process( temp_dict, temp_list[0:2])
    str_process( temp_dict, temp_list[2:4])

    gen_del_x, gen_del_y = gen_input( GENdelayDistrib)
    syn_del_x ,syn_del_y = gen_input( SYNdelayDistrib)
    temp_list = ['gen_del_x', 'gen_del_y', 'syn_del_x', 'syn_del_y']
    temp_dict = {'gen_del_x':gen_del_x, 'gen_del_y':gen_del_y, 'syn_del_x':syn_del_x, 'syn_del_y':syn_del_y}
    str_process( temp_dict, temp_list[0:2])
    str_process( temp_dict, temp_list[2:4])
    pass



if __name__ == "__main__":
    generate(sys.argv[1],sys.argv[2])
