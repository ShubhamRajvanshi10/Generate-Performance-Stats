import os, json
import requests
from statistics import mean
from configparser import ConfigParser


def getavg(testrun, groupID, graphID, vectorName):
    SummaryJFile = '/home/netstorm/DotNet/logs/TR{}/reports/summaryReports/_SummaryReport/summary.json'.format(testrun)
    if not os.path.exists(SummaryJFile):
        print("ERROR: summary.json file does not exists")
    else:
        with open (SummaryJFile,  'r') as JF:
            #JS = json.loads(JF.read())["TestInformation"]["AppliedStartEndDateTime"][10:48]
            JS = json.loads(JF.read())["TestInformation"]["TestRunStartEndDateTime"]
            StartTime,  EndTime = JS.split(" to ")
            SDate,  Stime = StartTime.split("  ")
            SMM, SDD, SYY = SDate.split("/")
            SDate = '{}/{}/20{}'.format(SMM, SDD, SYY)
            EDate,  Etime = EndTime.split(" ")
            EMM, EDD, EYY = EDate.split("/")
            EDate = '{}/{}/20{}'.format(EMM, EDD, EYY)
            URL = 'http://10.10.30.72:8002/DashboardServer/web/dev/checkGraphData?testRun={0}&startTime={1}%20{2}&endTime={3}%20{4}&groupId={5}&graphId={6}&vectorName={7}&mode=2'.format(testrun, SDate, Stime, EDate, Etime, groupID, graphID, vectorName)
            print(URL)
        rep = requests.get(URL,  verify = False)
        #samplelist = rep.json()["Samples"]
        #listsam = [i['graphValue'] for i in samplelist]
        #avg = mean(listsam)
        avg = mean([i['graphValue'] for i in rep.json()['Samples']])
    return str(round(avg,  2))

def Send_Mail(Subject,to,cc):
    import string
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    msg = MIMEMultipart('alternative')
    with open('StatsBt.html', 'r') as HT:
        html = HT.read()
	 
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    rcpt = cc.split(",") + [to]
    msg['Subject'] = Subject
    msg['From'] = "shubham.rajvanshi@cavisson.com"
    msg['To'] = to
    msg['cc'] = cc
    server = smtplib.SMTP('websrv.cavisson.com',587)
    server.starttls()
    server.login("shubham.rajvanshi@cavisson.com", "Cavisson!")
    #server.sendmail("shubham.rajvanshi@cavisson.com", "shubham.rajvanshi@cavisson.com", msg.as_string())
    server.sendmail("shubham.rajvanshi@cavisson.com", rcpt, msg.as_string())
    server.quit()
    return


def Gen_Html_Top():
    html='''<!DOCTYPE html>
<html>
<head>
<style>
table#t01 {
border: 1px solid gray;
margin: 5px;
}
table#t01 tr:nth-child(even) {
background-color: #eee;
}
table#t01 tr:nth-child(odd) {
        background-color:#fff;
}
table#t01 th {
background-color: LightSkyBlue;
color: black;
text-align: left;
}

table#t02 {
border: 1px solid gray;
margin: 5px;
}

table#t02 tr:nth-child(even) {
background-color: #eee;
}
table#t02 tr:nth-child(odd) {
        background-color:#fff;
}
table#t02 th {
background-color: LightSkyBlue;
color: black;
text-align: left;
}

table#t03 {
border: 1px solid gray;
margin: 5px;
}

table#t03 tr:nth-child(even) {
background-color: #eee;
}
table#t03 tr:nth-child(odd) {
        background-color:#fff;
}
table#t03 th {
background-color: LightSkyBlue;
color: black;
text-align: left;
}
</style>
</head>
<body>
<p><b>NetDiagnostics DotNetAgent Performance Stats</b></p>
'''
    with open('PerfStats.html',  'w+') as HT:
        HT.write(html + "\n")
    return

def Gen_Html_End():
    with open('PerfStats.html',  'a') as HT:
        HT.write("<p>Thanks and Regards</p>" + "\n" + "<p>Shubham Rajvanshi</p>" + "\n" + "</body>" + "\n" + "</html>")
    return

def Gen_Html_Data(TestStats):
        with open('PerfStats.html' ,  'a') as HT:
                HT.write("\n" + "<tr>" + "\n")
                for value in TestStats:
                        HT.write(" " + "<td>" + value + "</td>" + "\n")
                HT.write("</tr>" + "\n")
        return

def Gen_Headers(Headers):
    with open("PerfStats.html",  "a") as HT:
        HT.write("<tr>" + "\n")
        for header in Headers:
            HT.write(" " + "<th>" + header + "</th>" + "\n")
        HT.write("</tr>" + "\n")
    return

def Gen_DescTable(TestRuns, TestDesc):
        DescHeaders = ["TestRun",  "Description"]
        with open("PerfStats.html",  "a") as HT:
                HT.write('<table id="t03" style="width:100%">' + "\n")
        Gen_Headers(DescHeaders)
        with open("PerfStats.html",  "a") as HT:
                for i in range(len(TestRuns)):
                        HT.write("<tr>" + "\n")
                        HT.write(" " + "<td>" + TestRuns[i] + "</td>" + "\n" + " " + "<td>" + TestDesc[i] + "</td>" + "\n")
                        HT.write("</tr>" + "\n")
                HT.write("</table>" + "\n")
        return


def Gen_Response_Metrics(TestRuns,  Resp_Headers):
    with open("PerfStats.html",  "a") as HT:
                HT.write('<table id="t01" style="width:100%">' + "\n")
    Gen_Headers(Resp_Headers)
    for TR in TestRuns:
                globals()['TestStats_{}'.format(TR)] = [TR,  "NA",  "NA",  "NA",  "NA",  "NA",  "NA",  "NA",  "NA"]
                TestNumber = eval('TestStats_' + TR)
                TestRun_path = os.path.join('/home/netstorm/DotNet/logs/TR' + TR)
                Summery_File = os.path.join(TestRun_path + '/summary_gdf.data')
                with open(Summery_File,  'r') as SF:
                        for SFlines in SF:
                                if "HTTP Requests" in SFlines:
                                        if "Requests Sent/Sec" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[1]=avg
                                        if "Requests Successful/Sec" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[2]=avg
                                        if "Average Response Time" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[3]=avg
                                if "Page Download" in SFlines:
                                        if "Page Download Started/Second" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[4]=avg
                                        if "Average Page Response Time" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[5]=avg
                                if "Business Transactions(DotNet>Overall>Overall>AllTransactions)" in SFlines:
                                        if "Requests per sec(NA)" in SFlines:
                                                #one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[6]=getavg(TR, 10245, 1, "DotNet>Overall>Overall>AllTransactions")
                                        if "20|Average Response Time (ms)(NA)" in SFlines:
                                                one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                TestNumber[7]=avg
                                if "FlowPath Stats(DotNet>windows-server61>Trade)" in SFlines:
                                        if "Flowpaths per sec" in SFlines:
                                                #one, two, three, four, five, avg, seven, eight = SFlines.split("|")
                                                FstAvg=getavg(TR, 10150, 2, "DotNet>windows-server61>Trade")
                                                SndAvg=getavg(TR, 10150, 2, "DotNet>windows-server61>Manymethod_Ora_iis")
                                                TestNumber[8]=str(float(FstAvg)+float(SndAvg))
                print(TestNumber)
                Gen_Html_Data(TestNumber)
    with open("PerfStats.html",  "a") as HT:
        HT.write("</table>" + "\n")
    return

def Gen_System_Metrics(TestRuns, System_Headers, Sys_Value):
    with open("PerfStats.html",  "a") as HT:
        HT.write('<table id="t02" style="width:100%">' + "\n")
    Gen_Headers(System_Headers)
    for TR in TestRuns:
        #globals()['TestStats_{}'.format(TR)] = [TR,  "NA",  "NA",  "NA",  "NA",  "NA",  "NA",  "NA"]
        globals()['TestStats_{}'.format(TR)] = [TR]
        TestNumber = eval('TestStats_' + TR)
        TestRun_path = os.path.join('/home/netstorm/DotNet/logs/TR' + TR)
        Summery_File = os.path.join(TestRun_path + '/summary_gdf.data')
        i=1
        for val in System_Headers[1:]:
            print(Sys_Value[i])
            GroupID, GraphID, VectorName = Sys_Value[i].split(",")
            TestNumber.append(getavg(TR, GroupID, GraphID, VectorName))
            i = i+1
        
        print(TestNumber)
        Gen_Html_Data(TestNumber)
    with open("PerfStats.html",  "a") as HT:
        HT.write("</table>" + "\n")    
    return



def main():
    TestRuns = []
    TestDesc = []
    Resp_Headers = ["TestRun",  "Requests Sent/Sec",  "Requests Successful/Sec",  "Average Response Time (Secs)",  "Page Download Started/Second",  "Average Page Response Time (Secs)",  "BT(Overall) Requests/Sec",  "BT(Overall) Avg Response Time(ms)",  "Flowpaths/Sec"]
    #System_Headers = ["TestRun", "Available Memory (MB)",  "Context Switches/Sec",  "CPU Load (PCT)",  "Interrupts/Sec",  "Disk Read Bytes/Sec",  "Disk Write Bytes/Sec",  "System Call/Sec",  "Total Thread Contention"]
    System_Headers = ["TestRun"]
    Sys_Value = ["NA"]
    Parser = ConfigParser()
    Parser.read('config.ini')
    for section in Parser.sections():
        if (section == "email"):
            Subject = Parser.get('email', 'Subject')
            to = Parser.get('email', 'to')
            cc = Parser.get('email', 'cc')
        if (section == "SysGraphs"):
            for name, value in Parser.items(section):
                System_Headers.append(name)
                Sys_Value.append(value)
        if (section == "TRDetails"):
            for TRname, TRvalue in Parser.items(section):
                if not os.path.exists(os.path.join('/home/netstorm/DotNet/logs/TR' + TRname)):
                    print(">>>>>>>>ERROR :- TestRun's path is not valid for {} <<<<<<<<<<".format(TRname))
                else:
                    TestRuns.append(TRname)
                    TestDesc.append(TRvalue)
    print(TestRuns)
    print(TestDesc)
    print(Sys_Value)
    print(System_Headers)
    '''keep_going = True
    while keep_going:
        TestRun = input("Enter the testrun numbers:TestDescription ")
        print(TestRun)
        Number, Desc=TestRun.split(":")
        TestRuns.append(Number)
        TestDesc.append(Desc)
        if not os.path.exists(os.path.join('/home/netstorm/DotNet/logs/TR' + Number)):
            print(">>>>>>>>ERROR :- TestRun's path is not valid<<<<<<<<<<")
            ui_keep_going = input("continue? (y/N): ")
            if ui_keep_going != "y":
                keep_going = False
        else:
            ui_keep_going = input("continue? (y/N): ")
            if ui_keep_going != "y":
                keep_going = False'''
    if len(TestRuns) == 0:
        print("ERROR:- There is no test run to work on")
    else:
        Gen_Html_Top()
        Gen_DescTable(TestRuns, TestDesc)
        Gen_Response_Metrics(TestRuns, Resp_Headers)
        Gen_System_Metrics(TestRuns, System_Headers, Sys_Value)
        Gen_Html_End()
        #send_mail(Subject,to,cc)

main()

