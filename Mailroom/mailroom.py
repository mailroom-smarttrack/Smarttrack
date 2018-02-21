from appJar import gui
import MySQLdb
import datetime
from zebra import zebra
from PIL import Image, ImageTk
import io
import socket
import sys
import wmi
from ipaddress import ip_address
c = wmi.WMI ()
 
 
localip =""
for interface in c.Win32_NetworkAdapterConfiguration (IPEnabled=1):
  print (interface.Description)
  for ip_address in interface.IPAddress:
      if (len(ip_address.split('.')) == 4):
          localip =   ip_address        
          print (ip_address)
          
    



#clock

db_info = {'user':'mailroom' , 'password':'mailroom' , 'host':localip , 'database':'smarttrack'}
print(db_info)
db = MySQLdb.connect(user=db_info['user'], password=db_info['password'], host=db_info['host'], database=db_info['database'])

cursor=db.cursor()


sql_select_emp='SELECT concat(EmpFirstName, \' \' , EmpLastName) FROM smarttrack.employees;'
sql_select_sender = 'SELECT SenName FROM smarttrack.senders;'
sql_select_carrier = 'SELECT CPaCarier, CPaSize, CPaServiceStart, CPaServiceLenght, CpaMaskStart, CpaMaskLenght, CpaMaskValue, CpaServiceValue, CpaSystemServices, CPaName, CpaServiceDesciption FROM smarttrack.carriersservices where  CPaSize = %s ;'
sql_select_check_carrier = 'SELECT CPaCarier, CPaSize, CPaServiceStart, CPaServiceLenght, CpaMaskStart, CpaMaskLenght, CpaMaskValue, CpaServiceValue, CpaSystemServices, CPaName, CpaServiceDesciption FROM smarttrack.carriersservices where  CPaName like %(CPaName)s  group by CPaName;' 
sql_select_carrier_name = 'SELECT DISTINCT  CPaName FROM smarttrack.carriersservices ;'
sql_insert_itemlog = 'INSERT INTO smarttrack.itemlog (itemlog.IloStaCode, itemlog.IloStaGroup, itemlog.IloID, itemlog.IloTrackingNo, itemlog.IloCarrier, itemlog.IloSender, itemlog.IloEmployeeFirstName, itemlog.IloEmployeeLasttName, itemlog.IloLocName, itemlog.IloLocID, itemlog.IloService, itemlog.IloServiceDescripton, itemlog.IloDateTime, itemlog.IloUseName, itemlog.IloStatusID) VALUES (%(IloStaCode)s, %(IloStaGroup)s, %(IloID)s, %(IloTrackingNo)s, %(IloCarrier)s, %(IloSender)s, %(IloEmployeeFirstName)s, %(IloEmployeeLasttName)s, %(IloLocName)s, %(IloLocID)s, %(IloService)s, %(IloServiceDescripton)s, %(IloDateTime)s, %(IloUseName)s, %(IloStatusID)s);'
sql_insert_itemstatus = 'INSERT INTO smarttrack.itemstatus (itemstatus.IeSStaCode, itemstatus.IeSStaGroup, itemstatus.IeSID, itemstatus.IeSTrackingNo, itemstatus.IeSCarrier, itemstatus.IeSSender, itemstatus.IeSEmployeeFirstName, itemstatus.IeSEmployeeLastName, itemstatus.IeSLocName, itemstatus.IeSLocID, itemstatus.IeSService, itemstatus.IeSServiceDescripton, itemstatus.IeSDateTime, itemstatus.IeSUseName, itemstatus.IeSStatusID) VALUES (%(IloStaCode)s, %(IloStaGroup)s, %(IloID)s, %(IloTrackingNo)s, %(IloCarrier)s, %(IloSender)s, %(IloEmployeeFirstName)s, %(IloEmployeeLasttName)s, %(IloLocName)s, %(IloLocID)s, %(IloService)s, %(IloServiceDescripton)s, %(IloDateTime)s, %(IloUseName)s, %(IloStatusID)s);'
sql_select_search = "SELECT IloTrackingNo, IloSender, IloCarrier, REPLACE(REPLACE(IloStatusID, 'DE', 'Deliver'), 'RE', 'Receive') as status, IloDateTime  FROM smarttrack.itemlog where "
sql_select_sign = "SELECT SigSignature FROM smarttrack.signatures where SigID = (SELECT IloSigID  FROM smarttrack.itemlog  where IloStatusID = 'DE' and IloTrackingNo = %(trackid)s  ORDER BY IloAutoID DESC LIMIT 1)"
sql_select_sign1 = "SELECT SigSignature FROM smarttrack.signatures where SigID =  42523"
sql_select_receiver =  "SELECT IloDateTime , IloPadLocation, IloSigID FROM smarttrack.itemlog where IloStatusID = 'DE' and  IloTrackingNo = %(trackid)s"
sql_insert_employees = 'insert into smarttrack.employees (employees.EmpFirstName, employees.EmpLastName) values  (%(emp_first)s , %(emp_last)s)'
sql_insert_sender = "INSERT INTO smarttrack.senders ( senders.SenName , senders.SenAccount ) values (%(sender_name)s , %(sender_account)s)"
list_box_control = ""
list_pos = -1
tmp_carrier = []


def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict( (getattr(socket, n), n)
                 for n in dir(socket)
                 if n.startswith(prefix)
                 )
    
def sendip(ip,epl):
    families = get_constants('AF_')
    types = get_constants('SOCK_')
    protocols = get_constants('IPPROTO_')

# Create a TCP/IP socket
    sock = socket.create_connection((ip, 9100))

    print >>sys.stderr, 'Family  :', families[sock.family]
    print >>sys.stderr, 'Type    :', types[sock.type]
    print >>sys.stderr, 'Protocol:', protocols[sock.proto]
    print >>sys.stderr

    try:
    
        # Send data
        #message = "^XA^PR12^LRY^MD30^PW440^LL400^PON^CFd0,50,15^FO0,20^FB440,2,0,C^FDSIU JACKY^FS^CFd0,30,18^FO5,85^FDSender:^FS^CF00,70,30^FO5,120^FB440,1,0,L^FDSARA JIMMERSON^FS^CF00,30,30^FO0,190^FB440,1,0,C^FD2018-02-12 19:36:43^FS^FO100,210^BQN,2,9^FDQA,021222193643^FS^PQ1^XZ"
        message = epl
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)

        amount_received = 0
        amount_expected = len(message)
    
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
        

    

def load_auto_name(sql_select_user):    
    cursor.execute(sql_select_user)
    employee_name = cursor.fetchall()
    emp_name = [""]
    for name in employee_name:
        emp_name.append(name[0])     
    return emp_name
    
def update_emp(name):
    update_listbox(name,sql_select_emp)

def update_sender(name):
    update_listbox(name,sql_select_sender)

def update_carrier(name):
    update_listbox(name,sql_select_carrier_name)
    check_carrier_name()
    
def submit_sender(name):    
    print(app.getEntry(name))
    if len(app.getListBox("list")) ==0:
        print("show add sender windows")    
        app.showSubWindow("Add Sender")
        app.setEntry("Sender Name: ", app.getEntry(name))
    
        

def submit_emp(name):
    print(app.getEntry(name))
    if len(app.getListBox("list")) ==0:
        print("show add emp windows")
        app.setEntry("Employee First Name: ", app.getEntry(name))
        app.setEntry("Employee Last Name: ", "")
        app.showSubWindow("Add Employee")
    else:
        app.setFocus("       Sender ")   
        
def add_emp(name):
    emp_first = str(app.getEntry("Employee First Name: "))
    emp_last = str(app.getEntry("Employee Last Name: "))
    val = {"emp_first" : emp_first , 
           "emp_last" : emp_last}
    print(name , val)    
    try:        
        cursor.execute(sql_insert_employees ,val)
        db.commit()
    except:
        print(cursor._last_executed )
        raise    
    app.setEntry("   Employee ", emp_first+" "+emp_last, callFunction=True)
    app.hideSubWindow("Add Employee")
    
def add_sender(name):
    sender_name = str(app.getEntry("Sender Name: "))
    sender_account = str(app.getEntry("Sender Account: "))
    val = {"sender_name" : sender_name , 
           "sender_account" : sender_account}
    print(name , val)    
    try:        
        cursor.execute(sql_insert_sender ,val)
        db.commit()
    except:
        print(cursor._last_executed )
        raise    
    app.setEntry("       Sender ", sender_name, callFunction=True)
    app.hideSubWindow("Add Sender")
    
    

def check_carrier_name():    
    print(sql_select_check_carrier)
    val = {'CPaName' : str(app.getEntry("       Carrier ")+"%")}
    cursor.execute(sql_select_check_carrier, val)
    global tmp_carrier    
    tmp_carrier = cursor.fetchall()[0]
    print(tmp_carrier)
       

def update_listbox(entry,sql):
    global list_pos
    list_pos = -1
    ent = app.getEntry(entry)    
    global list_box_control
    list_box_control = entry    
    app.updateListBox("list", (s for s in load_auto_name(sql) if ent.lower() in s.lower() ) , select=False) 
                    
    
def list_box_change():
    if not list_box_control=="": 
        listbox = app.getListBox("list")         
        if listbox:
            print(list_box_control)        
            print(listbox)
            app.setEntry(list_box_control, listbox[0], callFunction=False)
            if list_box_control == "       Carrier ":
                check_carrier_name()
            
        
        
def keyPress(key):
    global list_pos    
    if key == "<Down>": 
        print(list_pos)               
        list_pos +=1
    if key == "<Up>":
        print(list_pos)
        if  list_pos > 0:
            list_pos -=1        
    app.selectListItemAtPos("list", list_pos , callFunction=True)

def press(btn):
    print(btn)    


    
def gen_zpl(sender, receiver, dt , code):
        zpl = "^XA^PR12^LRY^MD30^PW440^LL400^PON^CFd0,50,15^FO0,20^FB440,2,0,C^FD" + str(receiver)
        zpl += "^FS^CFd0,30,18^FO5,85^FDSender:^FS^CF00,70,30^FO5,120^FB440,1,0,L^FD" + str(sender)
        zpl += "^FS^CF00,30,30^FO0,190^FB440,1,0,C^FD" + str(dt).split('.')[0]
        zpl += "^FS^FO100,210^BQN,2,9^FDQA,"+str(code)
        zpl += "^FS^PQ1^XZ"
        print(zpl)
        #sendip('10.17.204.201',zpl)
        z=zebra("Zebra ZP 500 (EPL)")
        z.output(zpl)


def check_carrier():
    tracking = app.getEntry("   Tracking# ")        
    val = (int(len(tracking)),)
    print(val)
    cursor.execute(sql_select_carrier, val)
    carrier_info = cursor.fetchall()        
    print(tracking)
    return_val = ('','','','','','','','','','','')    
    for rule in carrier_info:
        #print(rule)        
        sub_service = tracking[(rule[2]-1):(rule[2]+rule[3]-1)]
        sub_mask = tracking[(rule[4]-1):(rule[4]+rule[5]-1)]
        #print (sub_service + " " + sub_mask)         
        if sub_service == rule[7] and sub_mask == rule[6]:
            print (sub_service + " " + sub_mask)
            print(rule)
            return_val = rule
            break
        return_val = rule
    #print("return: ")
    #print(return_val)
    app.setEntry("       Carrier ", return_val[9], callFunction=False)
    app.setEntry("    Service ", return_val[10], callFunction=False)
    if   (len(tracking) == 34):
        app.setEntry("   Tracking# ", tracking[22:34], callFunction=False)
    global tmp_carrier
    tmp_carrier =  return_val     

    



def print_label():
    tracking = app.getEntry("   Tracking# ")
    sender = app.getEntry("       Sender ")
    emp = app.getEntry("   Employee ")
    
    if str(emp)=="" or str(sender) == "" or str(tracking)=="" :
        return
    
    dt =datetime.datetime.now() 
    date_ = str(dt).split(' ')[0].split('-')
    time_ = str(dt).split(' ')[1].split('.')[0].split(':')
    app.setEntry(" Date/Time ", str(dt).split('.')[0], callFunction=False)
    ids = date_[1]+date_[2]+str(int(date_[0])-1996)+time_[0]+time_[1]+time_[2]
    db_val = {
            'IloStaCode' : '4',
            'IloStaGroup' : '1',
            'IloID' : ids,
            'IloTrackingNo' :  tracking,
            'IloCarrier' : tmp_carrier[0],
            'IloSender' : sender,
            'IloEmployeeFirstName' : emp.split(' ')[0],
            'IloEmployeeLasttName' : emp.split(' ')[1],
            'IloLocName' : '1',
            'IloLocID' : '00100B001001001001',
            'IloService' : tmp_carrier[8],
            'IloServiceDescripton' : tmp_carrier[10],
            'IloDateTime' : dt.strftime('%Y-%m-%d %H:%M:%S') ,
            'IloUseName' : 'ADMINISTRATOR USER',
            'IloStatusID' : 'RE'        
        }
    print(db_val)
    try:
        cursor.execute(sql_insert_itemlog ,db_val)
        cursor.execute(sql_insert_itemstatus ,db_val)
        db.commit()
    except:
        print(cursor._last_executed )
        raise    
    gen_zpl(app.getEntry("       Sender "),app.getEntry("   Employee "), dt , ids)
    app.clearAllEntries(callFunction=False)
    app.clearAllListBoxes(callFunction=False)
    
    
def Quick_track_go():
    print("Quick_track_go") 
    radio_btn =app.getRadioButton("choose_mth")
    trackid = str(app.getEntry("tid"))
    sql = sql_select_search 
    if radio_btn == "Tracking Number":
        print(radio_btn + trackid)
        sql  += "IloTrackingNo = %s"
    else:
        print("not Tracking Number " + trackid)
        sql  += "IloID = %s ORDER BY IloAutoID DESC LIMIT 100"    
    cursor.execute(sql, [trackid])
    track = cursor.fetchall()
    print (track)
    update_Grid(track,"g1")
    
    

def update_Grid(data,whichone):
    g1_data = []
    for row in data:
        tmp_row = []
        for item in row:
            tmp_row.append(str(item))
        g1_data.append(tmp_row)
    print(g1_data)
    app.deleteAllGridRows(whichone)
    app.addGridRows(whichone, g1_data)
    
def search_reset():
    print("search_reset")
    app.deleteAllGridRows("g1")
    app.clearAllOptionBoxes(callFunction=False)
    app.clearAllCheckBoxes(callFunction=False)
    app.clearAllEntries(callFunction=False)
    app.setDatePicker("from-date", date=(datetime.datetime.now()-datetime.timedelta(weeks=26)) )
    app.setDatePicker("to-date", date=(datetime.datetime.now()+datetime.timedelta(days=1)) )

def track_search():    
    print("track_search")
    sql = sql_select_search
    add_and = ""
    if app.getCheckBox("By Employee"):
        sql +="concat(itemlog.IloEmployeeFirstName, ' ' , itemlog.IloEmployeeLasttName) = %(empname)s "
        add_and = " and "
        print("Employee")
    if app.getCheckBox("By Sender"):
        sql += add_and
        sql +="IloSender = %(sender)s "
        add_and = " and "
        print("Sender")
    if app.getCheckBox("By Carrier"):        
        print("Carrier")
        sql += add_and
        sql +="IloCarrier =(SELECT distinct(CPaCarier) FROM smarttrack.carriersservices where CPaName = %(carrier)s)  "
        add_and = " and "     
    sql += add_and + "IloDateTime between %(startdate)s and %(enddate)s ORDER BY IloAutoID DESC LIMIT 100"
    print(app.getDatePicker('from-date'))
    print(app.getDatePicker('to-date'))
    to_date= str(app.getDatePicker('to-date')) + " 23:59:59"
    val = { 'empname' : str(app.getOptionBox('by-employee')),
           'sender' : str(app.getOptionBox('by-sender')) ,
           'carrier' : str(app.getOptionBox('by-carrier')),
           'startdate' : str(app.getDatePicker('from-date')),
           'enddate' : to_date
    }
    print(sql)
    print(val)
    try:
        cursor.execute(sql, val)
        track = cursor.fetchall()
    except:
        print(cursor._last_executed )
        raise 
    print (track)
    update_Grid(track,"g1")
        

def grid_detail(btn):
    grid_row = app.getGridRow("g1", btn) 
    app.setEntry("Tracking Number: ", str(grid_row[0]), callFunction=False)
    trackid = {"trackid" : str(grid_row[0]) } 
    print(trackid )
    data = []
    data3 = []
    try:
        print(sql_select_sign)
        cursor.execute(sql_select_sign, trackid)
        data = cursor.fetchall()
        cursor.execute(sql_select_detail, trackid)
        data2 = cursor.fetchall()
        update_Grid(data2,"g2")
        cursor.execute(sql_select_receiver, trackid)
        data3 = cursor.fetchall()        
    except:
        print("grid_detail")
        print(cursor._last_executed )
        raise
    if data3:
        app.setEntry("Date And Time: ", str(data3[0][0]), callFunction=False)
        app.setEntry("Delivered To: ", str(data3[0][1]), callFunction=False)
    if data:        
        photo = ImageTk.PhotoImage(Image.open(io.BytesIO(data[0][0])))
        app.setImageData("signature_img", photo, fmt="PhotoImage")
    app.showSubWindow("Package Detail")
    
    
 
    
   
    



with gui("MailRoom System Version 1.0", bg="teal") as app:        
    app.setFont (size=25, family="Tahoma")
    app.setSize("fullscreen")
    app.showTitleBar()
    app.setLocation("CENTER")    
    app.bindKey("<Up>", keyPress)
    app.bindKey("<Down>", keyPress)        
    app.startTabbedFrame("TabbedFrame")
    app.startTab("Receiving")
    app.setBg("teal")
    app.setStretch("both")
    with app.labelFrame("Receive Package",    rowspan=1, sticky="news", expand="both"):
        
        app.addLabelEntry("   Tracking# ",  row=2, column=0, colspan=2 )
        app.setEntrySubmitFunction("   Tracking# ", check_carrier)        

        app.addLabelEntry("   Employee ", row=3, column=0, colspan=2  )
        app.setEntryChangeFunction("   Employee ", update_emp)
        app.setEntrySubmitFunction("   Employee ", submit_emp)         

        app.addLabelEntry("       Sender " ,  row=4, column=0, colspan=2 )
        app.setEntryChangeFunction("       Sender ", update_sender)
        app.setEntrySubmitFunction("       Sender ", submit_sender)          
        app.addLabelEntry("       Carrier " ,  row=5, column=0, colspan=1 )
        app.setEntryChangeFunction("       Carrier ", update_carrier)   
        app.addLabelEntry("    Service " ,  row=5, column=1, colspan=1 )
        app.addLabelEntry(" Date/Time ",  row=6, column=0, colspan=2 )
    
    with app.labelFrame("",   rowspan=1, sticky="news", expand="both"):
        app.addListBox("list",[" "],  row=0, column=0, colspan=4)
        app.setListBoxChangeFunction("list",list_box_change)        
        app.button("Print Label",print_label ,   pos=(1, 0))
        app.button("Multiples", press ,  pos=(1, 1))
        app.button("Reprint Last", press , pos=(1, 2))        
    app.stopTab()
    
    app.startTab("Search")    
    app.setBg("teal")
    app.setStretch("column")
    app.setSticky("nesw")
    with app.labelFrame("Quick Track", row=0, column=0,  rowspan=1, sticky="news", expand="both"):
        app.setStretch("column")
        app.addRadioButton("choose_mth", "Tracking Number", row=0, column=0)
        app.addRadioButton("choose_mth", "Label ID", row=0, column=1)
        app.addEntry("tid", row=1, column=0, colspan = 2)
        app.addButton("Go", Quick_track_go, row=1, column=3)
        
    with app.labelFrame("Time ",  row=0, column=1, rowspan=1, sticky="news", expand="both"):
        app.setStretch("column")        
        app.addLabel("l1", "Start date  ", row=0, column=0)
        app.addDatePicker("from-date", row=0, column=1)
        app.setDatePicker("from-date", date=(datetime.datetime.now()-datetime.timedelta(weeks=26)) )
        app.addLabel("l2", "  End Date  ", row=0, column=2)
        app.addDatePicker("to-date", row=0, column=3)
        app.setDatePicker("to-date", date=datetime.datetime.now() )
        
    app.setStretch("column")
    with app.labelFrame("Detailed Search ",  row=1, column=0, rowspan=1,colspan=4 ,sticky="news", expand="column"):
        app.setStretch("column")
        app.addCheckBox("By Employee",  row=0, column=0)
        app.addOptionBox("by-employee", load_auto_name(sql_select_emp),  row=0, column=1)
        app.addCheckBox("By Sender",  row=1, column=0)
        app.addOptionBox("by-sender", load_auto_name(sql_select_sender),  row=1, column=1)
        app.addCheckBox("By Carrier",  row=2, column=0)
        app.addOptionBox("by-carrier", load_auto_name(sql_select_carrier_name),  row=2, column=1)
    app.setStretch("column")
    app.addButton("Reset", search_reset, row=2, column=0)
    app.addButton("Search", track_search, row=2, column=1)    
    app.setStretch("both")
    with app.labelFrame("Search Result",  row=3, column=0, rowspan=10,colspan=4 ,sticky="news", expand="both"):
        app.setFont (size=20, family="Tahoma")
        app.addGrid("g1",
                    [["TRACKING NO", "SENDER", "CARR", "STATUS", "DATE & TIME"]],
                    action=grid_detail ,  row=0, column=0, actionHeading = "           ",  actionButton = "Detail")  
           
    app.stopTab()
    app.stopTabbedFrame()
    #--------------------
    #app.startTab("Package Detail")
    app.startSubWindow("Package Detail", title="Package Detail" , modal=True)        
    app.setBg("teal")
    app.setStretch("both")
    app.setSticky("nesw")
    app.setSize("1500x600")
    app.setLocation("CENTER")
    with app.labelFrame("Track ",  row=0, column=0, rowspan=1,colspan=10 ,sticky="news", expand="both"):
        app.setStretch("column")
        app.addLabelEntry("Tracking Number: ",row=0, column=0)
        app.setFont (size=20, family="Tahoma")
        app.addGrid("g2",
                    [["TRACKING NO", "EMPLOYEE","SENDER", "CARRIER", "DATE & TIME","STATUS" ]],
                      row=1, column=0)  
        app.setStretch("both")
        with app.labelFrame("Delivery Detail ",  row=2, column=0, rowspan=5,colspan=10 ,sticky="news", expand="both"):
            app.setStretch("column")
            app.addLabelEntry("Date And Time: ",row=0, column=0)
            app.addLabelEntry("Delivered To: ",row=0, column=1)
            app.setStretch("both")
            app.setSticky("news")
            
            app.addImage("signature_img", "test.gif", row=1, column=0 ,  colspan=2)
            
            
    app.stopSubWindow()
    #app.stopTab()
    #--------------------------------
    app.startSubWindow("Add Employee", title="Add Employee" , modal=True)        
    app.setBg("teal")
    app.setStretch("both")
    app.setSticky("nesw")
    #app.setSize("1500x600")
    app.setLocation("CENTER")
    app.setFont (size=20, family="Tahoma")
    with app.labelFrame("Add Employee ",  row=0, column=0, rowspan=1,colspan=1 ,sticky="news", expand="both"):
        app.addLabelEntry("Employee First Name: ",row=0, column=0 )
        app.addLabelEntry("Employee Last Name: ",row=1, column=0 )        
        app.addButton("Add Employee" , add_emp , row=2, column=0 )        
    app.stopSubWindow()
    
    app.startSubWindow("Add Sender", title="Add Sender" , modal=True)        
    app.setBg("teal")
    app.setStretch("both")
    app.setSticky("nesw")
    #app.setSize("1500x600")
    app.setLocation("CENTER")
    app.setFont (size=20, family="Tahoma")
    with app.labelFrame("Add Sender ",  row=0, column=0, rowspan=1,colspan=1 ,sticky="news", expand="both"):
        app.addLabelEntry("Sender Name: ",row=0, column=0 )
        app.addLabelEntry("Sender Account: ",row=1, column=0 )        
        app.addButton("Add Sender" , add_sender , row=2, column=0 )        
    app.stopSubWindow()


    