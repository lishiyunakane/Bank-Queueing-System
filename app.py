import pandas as pd
from collections import deque
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class Client:
    def __init__(self,type):
        self.ID = None
        self.type = type
        self.status = "Waiting" ## default status is "waiting", then can be changed into "Served", if not responsed, become missed
        self.counter = None ## counter can be 1, 2, 3
        self.branch = None

    def __repr__(self):
        return self.ID

class Counter:
    def __init__(self,ID,service):
        self.ID = ID
        self.service = service
        self.status = "On"

    def __repr__(self):
        pass

Branch_Counter = pd.DataFrame(columns = ['clients_list','missed_client','queue_P','queue_C','queue_S','Counter_list'],index = ['Branch_A','Branch_B'])
Branch_Counter.at['Branch_A','queue_P']= deque()
Branch_Counter.at['Branch_A','queue_C']= deque()
Branch_Counter.at['Branch_A','queue_S']= deque()
Branch_Counter.at['Branch_A','Counter_list']= [Counter(1,"C"),Counter(2,"P"),Counter(3,"P")]
Branch_Counter.at['Branch_A','clients_list']= []
Branch_Counter.at['Branch_A','missed_client']= []
Branch_Counter.at['Branch_A', 'stop_start_P'] = False
Branch_Counter.at['Branch_A', 'stop_start_C'] = False
Branch_Counter.at['Branch_A', 'stop_start_S'] = False

Branch_Counter.at['Branch_B','queue_P']= deque()
Branch_Counter.at['Branch_B','queue_C']= deque()
Branch_Counter.at['Branch_B','queue_S']= deque()
Branch_Counter.at['Branch_B','Counter_list']= [Counter(1,"C"),Counter(2,"P"),Counter(3,"P")]
Branch_Counter.at['Branch_B','clients_list']= []
Branch_Counter.at['Branch_B','missed_client']= []
Branch_Counter.at['Branch_B', 'stop_start_P'] = False
Branch_Counter.at['Branch_B', 'stop_start_C'] = False
Branch_Counter.at['Branch_B', 'stop_start_S'] = False

queue_count_PA = 0
queue_count_CA = 0
queue_count_SA = 0

queue_count_PB = 0
queue_count_CB = 0
queue_count_SB = 0

####  Cover Page ####
@app.route("/")
def coverpage():
    return render_template("coverpage.html")


##### Client Part ######

@app.route("/take_number/walk_in")
def index1():
    return render_template("client_walk_in_branch.html")


@app.route("/take_number/mobile")
def index2():
    return render_template("client_mobile_branch.html")



@app.route("/take_number/waiting_count")
def waiting_count():
    branch_number = request.args.get("branch")
    branch_name = 'Branch_'+branch_number
    names = globals()
    global queue_count_PA, queue_count_CA, queue_count_SA,queue_count_PB, queue_count_CB, queue_count_SB
    waiting_count_P = len(Branch_Counter.loc[branch_name,"queue_P"])
    waiting_count_C = len(Branch_Counter.loc[branch_name,"queue_C"])
    waiting_count_S = len(Branch_Counter.loc[branch_name,"queue_S"])
    return jsonify({"Count":{"P": waiting_count_P, "C": waiting_count_C, "S": waiting_count_S}})

@app.route("/take_number/generate_number/<prefix>")
def generate_number(prefix):
    names = globals()
    global queue_count_PA, queue_count_CA, queue_count_SA,queue_count_PB, queue_count_CB, queue_count_SB
    branch_number = request.args.get("branch")
    branch_name = 'Branch_'+branch_number

    ##### CRO #####
    if prefix == 'P' and Branch_Counter.loc[branch_name, "stop_start_P"] == True:
        return jsonify({"number": None})
    elif prefix == 'C' and Branch_Counter.loc[branch_name, "stop_start_C"] == True:
        return jsonify({"number": None})
    elif prefix == 'S' and Branch_Counter.loc[branch_name, "stop_start_S"] == True:
        return jsonify({"number": None})
    ##### CRO #####

    client = Client(prefix)
    client.branch = branch_number
    if prefix == 'P':
        names['queue_count_P'+branch_number] += 1
    elif prefix == 'C':
        names['queue_count_C'+branch_number] += 1
    elif prefix == 'S':
        names['queue_count_S'+branch_number] += 1

    if prefix == 'P' and names['queue_count_P'+branch_number] < 10:
        number = prefix + "00" + str(names['queue_count_P'+branch_number])
    elif prefix == 'P' and names['queue_count_P'+branch_number] >= 10 and names['queue_count_P'+branch_number] < 100:
        number = prefix + "0" + str(names['queue_count_P'+branch_number])
    elif prefix == 'P' and names['queue_count_P'+branch_number] >= 100 and names['queue_count_P'+branch_number] < 1000:
        number = prefix + str(names['queue_count_P'+branch_number])
    elif prefix == 'C' and names['queue_count_C'+branch_number] < 10:
        number = prefix + "00" + str(names['queue_count_C'+branch_number])
    elif prefix == 'C' and names['queue_count_C'+branch_number] >= 10 and names['queue_count_C'+branch_number] < 100:
        number = prefix + "0" + str(names['queue_count_C'+branch_number])
    elif prefix == 'C' and names['queue_count_C'+branch_number] >= 100 and names['queue_count_C'+branch_number] < 1000:
        number = prefix + str(names['queue_count_C'+branch_number])
    elif prefix == 'S' and names['queue_count_S'+branch_number] < 10:
        number = prefix + "00" + str(names['queue_count_S'+branch_number])
    elif prefix == 'S' and names['queue_count_S'+branch_number] >= 10 and names['queue_count_S'+branch_number] < 100:
        number = prefix + "0" + str(names['queue_count_S'+branch_number])
    elif prefix == 'S' and names['queue_count_S'+branch_number] >= 100 and names['queue_count_S'+branch_number] < 1000:
        number = prefix + str(names['queue_count_S'+branch_number])
    else:
        number = None
    client.ID = number
    Branch_Counter.loc[branch_name,"clients_list"].append(client)
    if prefix == 'P':
        client.type = 'P'
        Branch_Counter.loc[branch_name,"queue_P"].append(client)
    elif prefix == 'C':
        Branch_Counter.loc[branch_name,"queue_C"].append(client)
        client.type = 'C'
    elif prefix == 'S':
        client.type = 'S'
        Branch_Counter.loc[branch_name,"queue_S"].append(client)
    return jsonify({"number": client.ID})


##### CRO Part ######

@app.route("/CRO")
def cro_control_page():
    client_counts_A = {"P": {"Waiting": 0, "Served": 0, "Missed": 0},
                       "C": {"Waiting": 0, "Served": 0, "Missed": 0},
                       "S": {"Waiting": 0, "Served": 0, "Missed": 0}}
    clients_list_A = Branch_Counter.loc["Branch_A", "clients_list"]
    for client in clients_list_A:
        client_counts_A[client.type][client.status] += 1

    client_counts_B = {"P": {"Waiting": 0, "Served": 0, "Missed": 0},
                       "C": {"Waiting": 0, "Served": 0, "Missed": 0},
                       "S": {"Waiting": 0, "Served": 0, "Missed": 0}}
    clients_list_B = Branch_Counter.loc["Branch_B", "clients_list"]
    for client in clients_list_B:
        client_counts_B[client.type][client.status] += 1

    return render_template("cro_branch.html", client_counts_A=client_counts_A, client_counts_B=client_counts_B)


@app.route("/api_cro/stop_confirm_api/", methods=['POST', 'GET'])
def stop_confirm_api():
    if request.method == "GET":
        prefix = request.args.get("type")
        branch_name = request.args.get("branch")

    if prefix == 'Personal':
        Branch_Counter.loc[branch_name, "stop_start_P"] = True
    elif prefix == 'Business':
        Branch_Counter.loc[branch_name, "stop_start_C"] = True
    elif prefix == 'Senior':
        Branch_Counter.loc[branch_name, "stop_start_S"] = True
    return jsonify({"result": "False"})


@app.route("/api_cro/start_confirm_api", methods=['POST', 'GET'])
def start_confirm_api():
    if request.method == "GET":
        prefix = request.args.get("type")
        branch_name = request.args.get("branch")
    if prefix == 'Personal':
        Branch_Counter.loc[branch_name, "stop_start_P"] = False
    elif prefix == 'Business':
        Branch_Counter.loc[branch_name, "stop_start_C"] = False
    elif prefix == 'Senior':
        Branch_Counter.loc[branch_name, "stop_start_S"] = False
    return jsonify({"result": "True"})





##### Counter Part ######

@app.route("/queue_status")
def counter():
    return render_template("staff_branch.html")

@app.route('/branch_<branch_name>/queue_status/counter_<int:counter_number>')
def user(branch_name,counter_number):
    return render_template('staff_branch.html', branch_name = branch_name, counter_number=counter_number)

## calling next button
## input the counter number, output is the ID of the next client for this counter
@app.route("/branch_<branch_name>/queue_status/counter_<int:counter_number>/next") 
def calling_next(branch_name,counter_number): 
    branch_name = 'Branch_'+str(branch_name)
    #print(branch_name)
    names = globals()
    counter = next((each for each in Branch_Counter.loc[branch_name,'Counter_list'] if each.ID == counter_number),None) # find out the corresponding counter object
    if not Branch_Counter.loc[branch_name,'queue_S']:
        if counter.service == "C":
            if Branch_Counter.loc[branch_name,'queue_C']:
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)] = Branch_Counter.loc[branch_name,'queue_C'].popleft()
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].status = "Served"
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].counter = counter_number
                calling_res = "Now the calling client is "+ names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].ID
                return jsonify(calling_res=calling_res)
            elif Branch_Counter.loc[branch_name,'queue_P']:
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)] = Branch_Counter.loc[branch_name,'queue_P'].popleft()
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].status = "Served"
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].counter = counter_number
                calling_res = "Now the calling client is "+ names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].ID
                return jsonify(calling_res=calling_res)
            else:
                calling_res = "No client in the queue!"
                return jsonify(calling_res= "No client in the queue!")
        elif counter.service == "P":
            if Branch_Counter.loc[branch_name,'queue_P']:
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)] = Branch_Counter.loc[branch_name,'queue_P'].popleft()
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].status = "Served"
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].counter = counter_number
                calling_res = "Now the calling client is "+ names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].ID
                return jsonify(calling_res=calling_res)
            elif Branch_Counter.loc[branch_name,'queue_C']:
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)] = Branch_Counter.loc[branch_name,'queue_C'].popleft()
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].status = "Served"
                names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].counter = counter_number
                calling_res = "Now the calling client is "+ names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].ID
                return jsonify(calling_res=calling_res)
            else:
                calling_res = "No client in the queue!"
                return jsonify(calling_res= "No client in the queue!")
    else: 
        names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)] = Branch_Counter.loc[branch_name,'queue_S'].popleft()
        names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].status = "Served"
        names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].counter = counter_number
        calling_res = "Now the calling client is "+ names['now_client_for_branch'+str(branch_name)+'_counter'+str(counter_number)].ID
        return jsonify(calling_res=calling_res)


# change the status to missed button. 
# input is counter number. it will automatically get the last clients the counter called and change the client status into missed, and put into the client into the missed list for this counter
# output is the ID of last client missed
@app.route("/branch_<branch_name>/queue_status/counter_<int:counter_number>/missed") # 1 for C, 2 and 3 for P
def missed(branch_name,counter_number):
    branch_name = 'Branch_'+str(branch_name)
    names = globals()
    missed = names['now_client_for_branch'+ str(branch_name)+'_counter'+str(counter_number)]
    missed.status = "Missed"
    #counter = next((each for each in Counter_list if each.ID == counter_number),None)
    Branch_Counter.loc[branch_name,'missed_client'].append(missed)
    missed_res = missed.ID + " has been missed."
    return jsonify(missed_res = missed_res) 

# reschedule button
# input is the counter number and ID of the client need to reschedule
# output is new missed list for the counter. if the client is not in this counter, give the warning
@app.route("/branch_<branch_name>/queue_status/counter_<int:counter_number>/reschedule") # 1 for C, 2 and 3 for P
def reschedule(branch_name,counter_number):
    branch_name = 'Branch_' + str(branch_name)
    ID_Reschedule = request.args.get("rescheduleid")
    #print(ID_Reschedule)
    Get_Client = False
    for i, val in enumerate(Branch_Counter.loc[branch_name,'missed_client']):
        if val.ID == ID_Reschedule:
            Branch_Counter.loc[branch_name,'missed_client'][i].status = "Waiting"
            reschedule_client = Branch_Counter.loc[branch_name,'missed_client'][i]
            Branch_Counter.loc[branch_name,'missed_client'].pop(i)
            Get_Client = True
    if Get_Client:
        if reschedule_client.type == "C":
            Branch_Counter.loc[branch_name,'queue_C'].insert(2,reschedule_client)
        elif reschedule_client.type == "P":
            Branch_Counter.loc[branch_name,'queue_P'].insert(2,reschedule_client)
        elif reschedule_client.type == "S":
            Branch_Counter.loc[branch_name,'queue_S'].insert(2,reschedule_client)
        reschedule_res = "{} has been successfully reschedule!".format(ID_Reschedule) 
        return  jsonify(reschedule_res=reschedule_res)
    else:
        reschedule_res = "Sorry, {} is not missed".format(ID_Reschedule) 
        return jsonify(reschedule_res=reschedule_res)

if __name__ == '__main__':
    app.run()
