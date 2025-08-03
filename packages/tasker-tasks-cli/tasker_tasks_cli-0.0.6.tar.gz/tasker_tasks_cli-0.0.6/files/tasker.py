#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
import argparse
import configparser
import os
import sys
import tempfile
from subprocess import call
import datetime
from dateutil import parser
from iterfzf import iterfzf
import webbrowser
from collections import defaultdict

configfile = "./tasker.conf"

# parameters
parser = argparse.ArgumentParser(description='tasker - task manager for cli')
parser.add_argument('-n','--newtask', nargs="+", required=False)
parser.add_argument('-lc','--listcategories', action='store_true', required=False)
parser.add_argument('-c','--category', nargs='+', required=False)
args = parser.parse_args()

# configs
home = os.path.expanduser("~")
tasker_base = ( home + '/tasker')
taskerdir = ( tasker_base + '/tasks')
configdir = ( tasker_base + '/conf')
taskerfile = ( taskerdir + '/tasker.json')
configfile = ( configdir + '/tasker.conf')

if not os.path.isfile(taskerfile):
  if not os.path.exists(taskerdir):
    os.makedirs(taskerdir)
  jsondbobject = open(taskerfile, 'a+')
  jsondbobject.write("{}")
  jsondbobject.close()

if not os.path.isfile(configfile):
  if not os.path.exists(configdir):
    os.makedirs(configdir)
  configfileobject = open(configfile, 'a+')
  configfileobject.write("[Main]\n")
  configfileobject.write('default_category = NONE\n')
  configfileobject.write('default_highlight = | \n')
  configfileobject.write('# When commented out, will use OS default:\n')
  configfileobject.write('#browser = /snap/bin/firefox\n')
  configfileobject.write("\n")
  configfileobject.close()

config = configparser.ConfigParser()
config.read(configfile)
default_category = config.get('Main', 'default_category')
default_hl = config.get('Main', 'default_highlight')
try:
  browser = config.get('Main', 'browser')
except:
  browser = False

jsondb=taskerfile

menulabel = {
    "new":"/newtask",
    "today":"/today",
    "todayplusall":"/upcoming",
    "tomorrow":"/tomorrow",
    "all":"*",
    "exit":"/exit",
    "back":"/back",
    "p1":"/p1",
    "empty_completed":"/empty-completed",
    "exit_tasks":"/categories",
    "sep":"   ",
    "noteflag":"[n]",
    "linkflag":"[l]",
    "pointer":"=>",
    "completed":"/completed",
    "priority_down":"/priority_down",
    "priority_up":"/priority_up",
    "refresh":"/refresh",
    "schedule":"/schedule",
}

def dbfio(jsonfile,iotype,vtable={}):
    if iotype == "write":
        with open(jsonfile,"w",encoding='utf-8') as outputfile:
            json.dump(vtable, outputfile)
    elif iotype == "read":
        with open(jsonfile,"r") as inputfile:
            try:
                vtable=json.load(inputfile)
            except ValueError:
                vtable={}
    return vtable

def showtasks(taskerdb,show="task",sortby="task",category=False,subcategory=False,returnarray=False,p1only=False,todayonly=True,tomorrowonly=False):
  blankarray=[]
  for key,record in taskerdb.items():
    blankarray.append(record)
  try:
    sortedlist = sorted(blankarray, key=lambda k: k[sortby])
  except:
    sortedlist = sorted(blankarray, key=lambda k: k["task"])
  results=[]
  if show == "category":
    for record in sortedlist:
      if record[show] != "completed":
        results.append(record[show])
    if returnarray:
      return set(results)
    else:
      for arec in set(results):
        print (arec)
  elif show == "subcategory":
    for record in sortedlist:
      results.append(record[show])
    if returnarray:
      return set(results)
    else:
      for arec in set(results):
        print (arec)
  else:
    today = datetime.datetime.today().date()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    for record in sortedlist:
      thetaskdate = datetime.datetime.strptime(record["duedate"], "%Y-%m-%d %H:%M:%S.%f").date()
      if not category:
        if not p1only:
          if tomorrowonly:
            if thetaskdate == tomorrow:
              try:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
              except:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
          elif todayonly:
            if thetaskdate <= today:
              try:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
              except:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])

          elif thetaskdate > today:
            try:
              results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
            except:
              results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
        elif record["priority"] == "1":
          try:
            results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
          except:
            results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
      elif record["category"] == category:
        if not p1only:
          if tomorrowonly:
            if thetaskdate == tomorrow:
              try:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
              except:
                results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
          elif todayonly:
            if thetaskdate <= today:
              if subcategory:
                if record["subcategory"] == subcategory:
                  try:
                    results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
                  except:
                    results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
              else:
                try:
                  results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
                except:
                  results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
          elif thetaskdate > today:
            try:
              results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
            except:
              results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
        elif record["priority"] == "1":
          try:
            results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"],record["link"]])
          except:
            results.append([record[show],record["priority"],record["note"],record["category"],record["subcategory"]])
    if returnarray:
      return results
    else:
      for showrec in results:
        print (showrec)

def showschedule(category_filter):
  import os, json, datetime, sys
  from collections import defaultdict
  os.system("clear")
  sys.stdout.write("\033[?25l")  # Hide cursor
  sys.stdout.flush()
  try:
    with open(taskerfile, "r") as f:
      data = json.load(f)
    today = datetime.datetime.today().date()
    tasks_by_key = defaultdict(list)

    # Prepare each task
    for task in data.values():
      if (
        task.get("category") == category_filter
        and not task.get("subcategory")
      ):
        try:
          due_dt = datetime.datetime.fromisoformat(task["duedate"])
          due_date = due_dt.date()
          if due_date <= today:
            continue  # Exclude tasks due today or earlier
          delta_days = (due_date - today).days
          if delta_days == 1:
            day_part = "(tomorrow)"
          else:
            day_part = f"({delta_days} days)"
          key = (str(due_date), due_date.strftime("%A"), day_part)
          tasks_by_key[key].append(task["task"])
        except Exception as e:
          print(f"Skipping task with invalid date: {task.get('task')} ({e})")

    if not tasks_by_key:
      print("No tasks found.\n")
      input("\n\n<enter> to return")
      return

    # Calculate alignment
    max_day_len = max(len(day) for _, day, _ in tasks_by_key)
    max_label_len = max(len(label) for _, _, label in tasks_by_key)

    # Prepare lines and max width
    output_lines = []
    for (datestr, day, label) in sorted(tasks_by_key):
      group_lines = []
      for idx, task in enumerate(tasks_by_key[(datestr, day, label)]):
        if idx == 0:
          line = f"{datestr} - {day:<{max_day_len}} {label:<{max_label_len}} - {task}"
        else:
          line = f"{' ' * len(datestr)}   {' ' * max_day_len} {' ' * max_label_len} - {task}"
        group_lines.append(line)
      output_lines.append(group_lines)

    max_line_len = max(len(line) for group in output_lines for line in group)
    rule = "─" * max_line_len

    # Print output
    print(rule)
    for idx, group in enumerate(output_lines):
      for line in group:
        print(line)
      print(rule)
    input()
  finally:
    sys.stdout.write("\033[?25h")  # Show cursor again
    sys.stdout.flush()

def hashstring(somestring):
  hash_object = hashlib.sha256(somestring.encode('utf-8'))
  return hash_object.hexdigest()

def addtask(taskerdb,defaultcat=False,defaultsubcat=False,thetask=False,priority="NONE"):
  os.system("clear")
  print ("\n%s/input\n" % menulabel["new"])
  if thetask:
    task=thetask
  else:
    task = input("\nTask: ")
  if task == "":
    return
  category = defaultcat
  note = ""
  link = ""
  adictrecord = {
      "task": task,
      "category": category,
      "subcategory": "",
      "priority": priority,
      "note": note,
      "link": link,
      "duedate": str(datetime.datetime.today())
  }
  task_key=hashstring(adictrecord["task"])
  taskerdb[task_key]=adictrecord
  if args.newtask:
    taskerdb=priorityupdate(taskerdb,task_key,priority)
  else:
    taskerdb=priorityupdate(taskerdb,task_key)
  if args.newtask:
    taskerdb=catupdate(taskerdb,task_key,category,defaultcat)
  else:
    taskerdb=catupdate(taskerdb,task_key,False,defaultcat)
  if args.newtask:
    taskerdb=subcatupdate(taskerdb,task_key,"NONE",defaultsubcat)
  else:
    taskerdb=subcatupdate(taskerdb,task_key,False,defaultsubcat)
  if args.newtask:
    taskerdb=duedateupdate(taskerdb,task_key,str(datetime.datetime.today()))
  else:
    taskerdb=duedateupdate(taskerdb,task_key)
  taskerdb=dbfio(jsondb,"write", taskerdb) 

def primove(taskerdb,thecat,down=True):
  for somerec in taskerdb:
      if taskerdb[somerec]["category"] == thecat:
          thepriority = taskerdb[somerec]["priority"]
          if thepriority != "NONE":
              if down:
                  thepriority = str(int(thepriority) + 1)
              else:
                  thepriority = str(int(thepriority) - 1)
                  if thepriority == "0":
                      thepriority = "1"
          taskerdb[somerec]["priority"]=thepriority
  taskerdb=dbfio(jsondb,"write", taskerdb) 

def saveit(taskerdb):
  taskerdb = dbfio(jsondb,"write", taskerdb)
  taskerdb = dbfio(jsondb,"read") 
  return taskerdb

def duedateupdate(taskerdb,task_key,newduedate=False):
  thetask=taskerdb[task_key]
  if newduedate:
    thetask["duedate"]=newduedate
  else:
    os.system("clear")
    weekdays=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    taskdate = datetime.datetime.strptime(thetask["duedate"], "%Y-%m-%d %H:%M:%S.%f")
    today = datetime.datetime.today()
    tomorrow = datetime.datetime.today() + datetime.timedelta(1)
    p2days = datetime.datetime.today() + datetime.timedelta(2)
    p3days = datetime.datetime.today() + datetime.timedelta(3)
    p4days = datetime.datetime.today() + datetime.timedelta(4)
    p5days = datetime.datetime.today() + datetime.timedelta(5)
    p6days = datetime.datetime.today() + datetime.timedelta(6)
    p1week = datetime.datetime.today() + datetime.timedelta(7)
    thedatelist=[today,tomorrow,p2days,p3days,p4days,p5days,p6days,p1week]
    taskoptionsmenu=[]
    taskoptionsmenu.append("today")
    taskoptionsmenu.append("tomorrow")
    taskoptionsmenu.append(weekdays[p2days.weekday()])
    taskoptionsmenu.append(weekdays[p3days.weekday()])
    taskoptionsmenu.append(weekdays[p4days.weekday()])
    taskoptionsmenu.append(weekdays[p5days.weekday()])
    taskoptionsmenu.append(weekdays[p6days.weekday()])
    taskoptionsmenu.append("1 week")
    taskoptionsmenu.append("specify date")
    task_selection_indexed = [f"{index} {value}" for index, value in enumerate(taskoptionsmenu)]
    try:
      task_selection_full = iterfzf(task_selection_indexed, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--with-nth=2..','--border=rounded',"--border-label= DUE DATE: %s " % thetask["task"]])
    except:
      task_selection = "today"
      task_index = 0 
    try:
      task_index_str, task_selection = task_selection_full.split(' ', 1)
      task_index = int(task_index_str)
      task_selection = task_selection.lstrip()
    except:
      task_selection = "today"
      task_index = 0 

    if task_selection == "specify date":
      while True:
        spectoday = datetime.date.today()
        specstart_date = datetime.date(spectoday.year, 1, 1)
        specend_date = datetime.date(spectoday.year + 1, 12, 31)
        specdelta = datetime.timedelta(days=1)
        specdates = []
        while specstart_date <= specend_date:
            specdates.append(str(specstart_date.strftime("%Y-%m-%d")))
            specstart_date += specdelta
        manual_date = iterfzf(specdates, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= SPECIFY DATE"])
        try:
          parsed_date = datetime.datetime.strptime(manual_date, "%Y-%m-%d")
          break
        except ValueError:
          print("\nInvalid date. Please try again.")
      newdate=manual_date+" 00:00:00.000000"
      thetask["duedate"]=str(newdate)
    else:
      thetask["duedate"]=str(thedatelist[task_index])
  taskerdb[task_key]=thetask
  return taskerdb

def delcompleted(taskerdb):
  completedlist=showtasks(taskerdb,show="task",sortby="task",category="completed",returnarray=True)
  if len(completedlist) > 0:
    os.system("clear")
    confirm=input("\n\nPermanently delete %s completed tasks? (y/n): " % len(completedlist))
    if confirm == "y":
      for rec in completedlist:
        somekey=hashstring(rec[0])
        del taskerdb[somekey]
      taskerdb=saveit(taskerdb)
  return taskerdb

def noteupdate(taskerdb,task_key,newnote=False):
  thetask=taskerdb[task_key]
  if newnote:
    thetask["note"]=newnote
  else:
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
      tf.write(thetask["note"].encode('utf-8'))
      tf.flush()
      call(["vim", '+set backupcopy=yes', tf.name])
      tf.seek(0)
      task_selection = tf.read().rstrip()
    thetask["note"]=task_selection.decode('utf-8')
  taskerdb[task_key]=thetask
  taskerdb=saveit(taskerdb)
  return taskerdb

def taskupdate(taskerdb,task_key,newtask=False,defaultcat=False):
  thetask=taskerdb[task_key]
  new_key=task_key
  if newtask:
    thetask["task"]=newtask
  else:
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
      tf.write(thetask["task"].encode('utf-8'))
      tf.flush()
      call(["vim", '+set backupcopy=yes', tf.name])
      tf.seek(0)
      task_selection = tf.readline().rstrip()
    thetask["task"]=task_selection.decode('utf-8')
    new_key=hashstring(task_selection.decode('utf-8'))
  taskerdb[new_key]=thetask
  if new_key != task_key:
    del taskerdb[task_key]
  return [taskerdb,new_key]

def catupdate(taskerdb,task_key,newcat=False,defaultcat=False):
  thetask=taskerdb[task_key]
  if newcat:
    thetask["category"]=newcat
  else:    
    os.system("clear")
    task_selection="start"
    tmparray=showtasks(taskerdb,show="category",sortby="category",category=False,returnarray=True)
    taskoptionsmenu=[]
    if defaultcat:
      taskoptionsmenu.append(defaultcat)
    for rec in tmparray:
      if rec != defaultcat:
        taskoptionsmenu.append(rec)
    taskoptionsmenu.append("OTHER")
    try:
      task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= SET CATEGORY: %s " % thetask["task"]])
    except:
      task_selection = "NONE"
    if task_selection is None:
      task_selection = "NONE"
    if task_selection == "OTHER":
      newcat=input("\nCategory: ").lower()
      taskerdb=catupdate(taskerdb,task_key,newcat)
    else:
      thetask["category"]=task_selection
  taskerdb[task_key]=thetask
  return taskerdb

def priorityupdate(taskerdb,task_key,newpriority=False):
  thetask=taskerdb[task_key]
  if newpriority:
    thetask["priority"]=newpriority
  else:
    os.system("clear")
    taskoptionsmenu=["NONE","1","2","3","4","5","6","7","8","9"]
    try:
      task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= SET PRIORITY: %s " % thetask["task"]])
    except:
      task_selection = "NONE"
    if task_selection is None:
      task_selection = "NONE"
    thetask["priority"]=task_selection
  taskerdb[task_key]=thetask
  return taskerdb

def linkupdate(taskerdb,task_key):
  thetask=taskerdb[task_key]
  os.system("clear")
  taskoptionsmenu=["launch","edit", "delete", "back"]
  try:
    thelink=thetask["link"]
    if thelink == "":
      thelink="No link set"
  except:
    thelink="No link set"
  try:
    task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=["--header=\n%s\n\n\n" % thelink,'--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= LINK "])
  except:
    task_selection = "NONE"
  if task_selection == "edit":
    newlink=input("\nURL: ")
    if newlink != "":
      thetask["link"]=newlink
      taskerdb[task_key]=thetask
      taskerdb=saveit(taskerdb)
      garbage=input("\n\nLink updated. Hit [enter] to continue.")
    else:
      garbage=input("\n\nLink NOT updated. Hit [enter] to continue.")
  elif task_selection == "delete":
    userinput=input("\n\nDelete link? Are you sure? (y|N): ")
    if userinput == "y":
      thetask["link"]=""
      taskerdb[task_key]=thetask
      taskerdb=saveit(taskerdb)
      garbage=input("\n\nLink removed. Hit [enter] to continue.")
    else:
      garbage=input("\n\nDelete link aborted. Hit [enter] to continue.")
  elif task_selection == "launch":
    if thelink != "No link set":
      if not browser:
        webbrowser.open(thelink)
      else:
        urlfmt="\"%s\"" % thelink 
        torun = "%s %s" % (browser, urlfmt)
        os.system(torun)
  return taskerdb

def subcatupdate(taskerdb,task_key,newsubcat=False,defaultsubcat=False):
  thetask=taskerdb[task_key]
  if newsubcat:
    if newsubcat == "NONE":
      thetask["subcategory"]=""
    else:
      thetask["subcategory"]=newsubcat
  else:    
    os.system("clear")
    task_selection="start"
    tmparray=showtasks(taskerdb,show="subcategory",sortby="subcategory",subcategory=False,returnarray=True) 
    taskoptionsmenu=[]
    if defaultsubcat: #needs code update to make use of.
      taskoptionsmenu.append(defaultsubcat)
    taskoptionsmenu.append("NONE")
    for rec in tmparray:
      if rec != defaultsubcat and rec != "":
        taskoptionsmenu.append(rec)
    taskoptionsmenu.append("OTHER")
    try:
      task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= SET SUB CATEGORY: %s " % thetask["task"]])
    except:
      task_selection = "NONE"
    if task_selection is None:
      task_selection = "NONE"
    if task_selection == "OTHER":
      newsubcat=input("\nSub-Category: ").lower()
      taskerdb=subcatupdate(taskerdb,task_key,newsubcat)
    elif task_selection == "NONE":
      taskerdb=subcatupdate(taskerdb,task_key,"NONE")
    else:
      thetask["subcategory"]=task_selection
  taskerdb[task_key]=thetask
  return taskerdb

def taskoptions(taskerdb,task_key):
  os.system("clear")
  task_selection="start"
  thetask=taskerdb[task_key]
  taskoptionsmenu=[]

  taskoptionsmenu.append("/priority")
  taskoptionsmenu.append("/due")
  taskoptionsmenu.append("/category")
  taskoptionsmenu.append("/subcategory")
  taskoptionsmenu.append("/edit")
  taskoptionsmenu.append("/note")
  taskoptionsmenu.append("/link")
  taskoptionsmenu.append("/delete")
  taskoptionsmenu.append("/completed")
  taskoptionsmenu.append(menulabel["sep"])
  taskoptionsmenu.append(menulabel["exit"])
  taskoptionsmenu.append(menulabel["back"])

  weekdays=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
  taskdate = datetime.datetime.strptime(thetask["duedate"], "%Y-%m-%d %H:%M:%S.%f")
  today = datetime.datetime.today()
  if taskdate <= today:
    taskdatestring="today"
  else:
    taskdatestring=weekdays[taskdate.weekday()]
  if thetask["note"] == "":
    hasnote=False
  else:
    hasnote=True
  while task_selection != menulabel["back"]:
    aline="=" * 30
    if hasnote:
      tasktitle="*** "+thetask["task"]+" ***\n\ncategory: "+thetask["category"]+"\npriority: "+thetask["priority"]+"\ndue: "+taskdatestring+"\n\nnote:\n"+aline+"\n"+thetask["note"]+"\n"+aline
    else:
      tasktitle="*** "+thetask["task"]+" ***\n\ncategory: "+thetask["category"]+"\npriority: "+thetask["priority"]+"\ndue: "+taskdatestring
    try:
      taskheader = '\n'.join(tasktitle.splitlines()[1:])
      task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=['--no-info',"--header=%s\n\n" % taskheader,'--height=100%','--layout=reverse','--border=rounded',"--border-label= %s " % thetask["task"]])
    except:
      task_selection = "/back"
    if task_selection is None:
      task_selection = "/back"
    if task_selection == "/priority":
      task_selection = menulabel["back"]
      taskerdb=priorityupdate(taskerdb,task_key)
      taskerdb=saveit(taskerdb)
    elif task_selection == "/exit":
      taskerdb=saveit(taskerdb)
      os._exit(0)
    elif task_selection == "/category":
      task_selection = menulabel["back"]
      taskerdb=catupdate(taskerdb,task_key)
      taskerdb=saveit(taskerdb)
    elif task_selection == "/subcategory":
      task_selection = menulabel["back"]
      taskerdb=subcatupdate(taskerdb,task_key)
      taskerdb=saveit(taskerdb)
    elif task_selection == "/due":
      task_selection = menulabel["back"]
      taskerdb=duedateupdate(taskerdb,task_key)
      taskerdb=saveit(taskerdb)
    elif task_selection == "/note":
      print (thetask["note"])
      taskerdb=noteupdate(taskerdb,task_key)
      taskerdb=saveit(taskerdb)
      thetask=taskerdb[task_key]
      if thetask["note"] == "":
        hasnote=False
      else:
        hasnote=True
    elif task_selection == "/link":
      taskerdb=linkupdate(taskerdb,task_key)
    elif task_selection == "/edit":
      task_selection = menulabel["back"]
      returnresult=taskupdate(taskerdb,task_key)
      taskerdb=returnresult[0]
      task_key=returnresult[1]
      taskerdb=saveit(taskerdb)
      thetask=taskerdb[task_key]
    elif task_selection == "/delete":
      confirm=input("\n\nDelete this task. Are you sure? (y/n): ")
      if confirm == "y":
        task_selection = menulabel["back"]
        del taskerdb[task_key]
        taskerdb=saveit(taskerdb)
    elif task_selection == "/completed":
      task_selection = menulabel["back"]
      taskerdb=priorityupdate(taskerdb,task_key,"NONE")
      taskerdb=catupdate(taskerdb,task_key,"completed")
      taskerdb=duedateupdate(taskerdb,task_key,str(datetime.datetime.today()))
      taskerdb=saveit(taskerdb)
  return taskerdb

def taskerwrapper(usercategory=False):
  if not usercategory:
    if default_category:
      usercategory = default_category
  showsubcat=False
  while True:
    taskerdb=dbfio(jsondb,"read") 
    catmenu=[]
    completedlist=showtasks(taskerdb,show="task",sortby="priority",category="completed",returnarray=True,p1only=False,todayonly=True)
    catlist=showtasks(taskerdb,show="category",sortby="category",category=False,returnarray=True)
    for somerec in catlist:
      catmenu.append(somerec)
    catmenu.append(menulabel["all"])
    catmenu.append(menulabel["sep"])
    catmenu.append(menulabel["p1"])
    if len(completedlist) > 0:
      catmenu.append(menulabel["completed"])
    catmenu.append(menulabel["new"])
    catmenu.append(menulabel["exit"])
    if not usercategory:
      try:
        chosen_category = iterfzf(catmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label=%s" % " categories "])
      except:
        chosen_category = menulabel["sep"]
      if chosen_category == None:
        chosen_category = menulabel["sep"]
    else:
      chosen_category = usercategory
      usercategory=False
    if chosen_category == menulabel["exit"]:
      sys.exit()
    elif chosen_category == menulabel["new"]:
      addtask(taskerdb)
    elif chosen_category == menulabel["sep"]:
      pass
    else:
      if chosen_category == menulabel["completed"]:
        chosen_category="completed"
        chosen_category_string="completed"
      else:
        chosen_category_string=chosen_category
      chosen_task="start"
      p1=False
      if chosen_category == menulabel["all"]:
        chosen_category=False
        chosen_category_string=menulabel["all"]
      elif chosen_category == menulabel["p1"]:
        chosen_category=False
        chosen_category_string="bin/p1"
        p1=True
      todaytasks=True
      tomorrowtasks=False
      while chosen_task != menulabel["back"]:
        if todaytasks:
          todaytasksflip=False
        else:
          todaytasksflip=True
        taskmenu=[]
        tasklist=showtasks(taskerdb,show="task",sortby="priority",category=chosen_category,returnarray=True,p1only=p1,todayonly=todaytasks,tomorrowonly=tomorrowtasks)
        tasklistother=showtasks(taskerdb,show="task",sortby="priority",category=chosen_category,returnarray=True,p1only=p1,todayonly=todaytasksflip,tomorrowonly=tomorrowtasks)
        tasklisttomorrow=showtasks(taskerdb,show="task",sortby="priority",category=chosen_category,returnarray=True,p1only=p1,todayonly=todaytasksflip,tomorrowonly=True)
        tasklisttoday=showtasks(taskerdb,show="task",sortby="priority",category=chosen_category,subcategory=showsubcat,returnarray=True,p1only=p1,todayonly=True,tomorrowonly=False)
        tasklistlen=len(tasklist)
        otherlength=len(tasklistother)
        tomorrowlength=len(tasklisttomorrow)
        todaylength=len(tasklisttoday)
        if tasklistlen == 0 and otherlength == 0:
          break
        filteredtasklist=[]
        if not showsubcat:
          for tofilt in tasklist:
            if not tofilt[4]:
              filteredtasklist.append(tofilt)
            elif ["subcatcheck419",tofilt[4],""] not in filteredtasklist:
              filteredtasklist.append(["subcatcheck419",tofilt[4],""])
        else:
          for tofilt in tasklist:
            if tofilt[4] == showsubcat:
              filteredtasklist.append(tofilt)

        for sometask in filteredtasklist:
          if sometask[1] == "NONE":
            somepriority=" "
          else:
            somepriority=sometask[1]
          linkcheck=""
          try:
            if sometask[5] == "":
              linkcheck=""
            else:
              linkcheck=menulabel["linkflag"]
          except:
            linkcheck=""
          if sometask[2] == "":
            notecheck=""
          else:
            notecheck=menulabel["noteflag"]
          if sometask[0] == "subcatcheck419":
            taskmenu.append(sometask[1])
          else:
            if somepriority == "1":
              if default_hl == "":
                aredresult = somepriority+" - "+sometask[0]+" "+notecheck+" "+linkcheck
              else:
                aredresult = default_hl+" "+sometask[0]+" "+notecheck+" "+linkcheck+" "+default_hl
              taskmenu.append(aredresult)
            else:
              taskmenu.append(somepriority+" - "+sometask[0]+" "+notecheck+" "+linkcheck)
        taskmenu.append(menulabel["sep"])
        if todaytasks:
          if otherlength > 0:
            if not p1:
              taskmenu.append(menulabel["todayplusall"]+"/"+str(otherlength))
              taskmenu.append(menulabel["tomorrow"]+"/"+str(tomorrowlength))
        elif otherlength > 0:
          if not p1:
            taskmenu.append(menulabel["today"]+"/"+str(todaylength))
        if chosen_category == "completed":
          taskmenu.append(menulabel["empty_completed"])
        else:
          taskmenu.append(menulabel["new"])
        taskmenu.append(menulabel["priority_down"])
        taskmenu.append(menulabel["priority_up"])
        taskmenu.append(menulabel["refresh"])
        taskmenu.append(menulabel["schedule"])
        taskmenu.append(menulabel["exit"])
        taskmenu.append(menulabel["back"])
        taskmenuindexed = [f"{index} {value}" for index, value in enumerate(taskmenu)]
        try:
          chosen_taskfull = iterfzf(taskmenuindexed, cycle=True, multi=True, __extra__=['--no-info','--height=100%','--layout=reverse','--with-nth=2..','--border=rounded',"--border-label= /%s (%s tasks) " % (chosen_category_string,str(len(tasklist)))])
        except:
          chosen_task = menulabel["sep"]
          chosen_task_index = 0 
        try:
          if len(chosen_taskfull) == 1:
            chosen_task_index_str, chosen_task = chosen_taskfull[0].split(' ', 1)
            chosen_task_index = int(chosen_task_index_str)
          else:
            taskerdb=multiselectoptions(taskerdb, chosen_taskfull,filteredtasklist)
            taskerdb=saveit(taskerdb)
            chosen_task = menulabel["sep"]
            chosen_task_index = 0 
        except:
          chosen_task = menulabel["back"]
          chosen_task_index = 0 
        if chosen_task == menulabel["new"]: 
          addtask(taskerdb,chosen_category)
          taskerdb=dbfio(jsondb,"read") 
        elif chosen_task == menulabel["refresh"]:
          taskerdb=dbfio(jsondb,"read") 
          pass
        elif chosen_task == menulabel["schedule"]:
          showschedule(chosen_category) 
          pass
        elif chosen_task == menulabel["sep"]:
          pass
        elif chosen_task == menulabel["back"]:
          if showsubcat:
            showsubcat=False
            chosen_task = menulabel["sep"]
          pass
        elif chosen_task == menulabel["exit"]:
          sys.exit()
        elif chosen_task == menulabel["empty_completed"]:
          taskerdb=delcompleted(taskerdb)
        elif chosen_task == menulabel["todayplusall"]+"/"+str(otherlength):
          todaytasks=False
          tomorrowtasks=False
        elif chosen_task == menulabel["tomorrow"]+"/"+str(tomorrowlength):
          todaytasks=False
          tomorrowtasks=True
        elif chosen_task == menulabel["today"]+"/"+str(todaylength):
          todaytasks=True
          tomorrowtasks=False
        elif chosen_task == menulabel["priority_down"]:
          primove(taskerdb,chosen_category)
        elif chosen_task == menulabel["priority_up"]:
          primove(taskerdb,chosen_category,down=False)
        else:
          try:
            if filteredtasklist[chosen_task_index][0] == "subcatcheck419":
              showsubcat=filteredtasklist[chosen_task_index][1] # user picked a subcat
            else:
              showsubcat=False
              taskid=hashstring(filteredtasklist[chosen_task_index][0])
              taskerdb=taskoptions(taskerdb,taskid)
          except:
            pass

def multiselectoptions(taskerdb, multitasks, filteredtasklist):
  os.system("clear")
  theheader=""
  taskoptionsmenu=["BACK","priority","due","completed","category","subcategory","delete"]
  for atask in multitasks:
    task_index_str, task = atask.split(' ', 1)
    task_index = int(task_index_str)
    theheader = theheader + " " + task + "\n"
  task_selection = iterfzf(taskoptionsmenu, cycle=True, multi=False, __extra__=["--header=\n%s\n" % theheader,'--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= MULTI-SELECT "])
  if task_selection == "priority":
    priorityoptionsmenu=["NONE","1","2","3","4","5","6","7","8","9"]
    try:
      priority_selection = iterfzf(priorityoptionsmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= MULTI-SELECT: Set Priority "])
    except:
      priority_selection = "CANCEL"
    if priority_selection is None:
      priority_selection = "CANCEL"
    if priority_selection != "CANCEL":
      for atask in multitasks:
        task_index_str, task = atask.split(' ', 1)
        task_index = int(task_index_str)
        tasktext = filteredtasklist[task_index][0]
        if tasktext != "subcatcheck419":
          task_key=hashstring(tasktext)
          thetask=taskerdb[task_key]
          thetask["priority"]=priority_selection
  elif task_selection == "completed":
    for atask in multitasks:
      task_index_str, task = atask.split(' ', 1)
      task_index = int(task_index_str)
      tasktext = filteredtasklist[task_index][0]
      if tasktext != "subcatcheck419":
        task_key=hashstring(tasktext)
        thetask=taskerdb[task_key]
        thetask["category"]="completed"
        thetask["priority"]="NONE"
  elif task_selection == "category":
    tmparray=showtasks(taskerdb,show="category",sortby="category",category=False,returnarray=True)
    catmenu=[]
    for rec in tmparray:
      catmenu.append(rec)
    catmenu.append("OTHER")
    try:
      cat_selection = iterfzf(catmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= MULTI-SELECT: Set Category"])
    except:
      cat_selection = "CANCEL"
    if cat_selection is None:
      cat_selection="CANCEL"
    if cat_selection == "OTHER":
      try:
        cat_selection=input("\nCategory: ").lower()
      except:
        cat_selection="CANCEL"
      if cat_selection is None:
        cat_selection="CANCEL"
    if cat_selection != "CANCEL":
      for atask in multitasks:
        task_index_str, task = atask.split(' ', 1)
        task_index = int(task_index_str)
        tasktext = filteredtasklist[task_index][0]
        if tasktext != "subcatcheck419":
          task_key=hashstring(tasktext)
          thetask=taskerdb[task_key]
          thetask["category"]=cat_selection
  elif task_selection == "subcategory":
    tmparray=showtasks(taskerdb,show="subcategory",sortby="subcategory",category=False,returnarray=True)
    subcatmenu=[]
    subcatmenu.append("NONE")
    for rec in tmparray:
      if rec != "":
        subcatmenu.append(rec)
    subcatmenu.append("OTHER")
    try:
      subcat_selection = iterfzf(subcatmenu, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--border=rounded',"--border-label= MULTI-SELECT: Set Subcategory"])
    except:
      subcat_selection = "CANCEL"
    if subcat_selection is None:
      subcat_selection="CANCEL"
    if subcat_selection == "OTHER":
      try:
        subcat_selection=input("\nSubcategory: ").lower()
      except:
        subcat_selection="CANCEL"
      if subcat_selection is None:
        subcat_selection="CANCEL"
    if subcat_selection != "CANCEL":
      for atask in multitasks:
        task_index_str, task = atask.split(' ', 1)
        task_index = int(task_index_str)
        tasktext = filteredtasklist[task_index][0]
        if tasktext != "subcatcheck419":
          task_key=hashstring(tasktext)
          thetask=taskerdb[task_key]
          if subcat_selection == "NONE":
            thetask["subcategory"]= ""
          else:
            thetask["subcategory"]=subcat_selection
  elif task_selection == "delete":
    task_selection = menulabel["back"]
    confirm=input("\n\nDelete these tasks. Are you sure? (y/n): ")
    if confirm == "y":
      for atask in multitasks:
        task_index_str, task = atask.split(' ', 1)
        task_index = int(task_index_str)
        tasktext = filteredtasklist[task_index][0]
        if tasktext != "subcatcheck419":
          task_key=hashstring(tasktext)
          del taskerdb[task_key]
  elif task_selection == "due":
    weekdays=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    today = datetime.datetime.today()
    tomorrow = datetime.datetime.today() + datetime.timedelta(1)
    p2days = datetime.datetime.today() + datetime.timedelta(2)
    p3days = datetime.datetime.today() + datetime.timedelta(3)
    p4days = datetime.datetime.today() + datetime.timedelta(4)
    p5days = datetime.datetime.today() + datetime.timedelta(5)
    p6days = datetime.datetime.today() + datetime.timedelta(6)
    p1week = datetime.datetime.today() + datetime.timedelta(7)
    thedatelist=[today,tomorrow,p2days,p3days,p4days,p5days,p6days,p1week]
    duetaskoptionsmenu=[]
    duetaskoptionsmenu.append("today")
    duetaskoptionsmenu.append("tomorrow")
    duetaskoptionsmenu.append(weekdays[p2days.weekday()])
    duetaskoptionsmenu.append(weekdays[p3days.weekday()])
    duetaskoptionsmenu.append(weekdays[p4days.weekday()])
    duetaskoptionsmenu.append(weekdays[p5days.weekday()])
    duetaskoptionsmenu.append(weekdays[p6days.weekday()])
    duetaskoptionsmenu.append("1 week")
    task_selection_indexed = [f"{index} {value}" for index, value in enumerate(duetaskoptionsmenu)]
    try:
      duetask_selection_full = iterfzf(task_selection_indexed, cycle=True, multi=False, __extra__=['--no-info','--height=100%','--layout=reverse','--with-nth=2..','--border=rounded',"--border-label= MULTI-SELECT: Due Date "])
    except:
      duetask_selection_full = "CANCEL"
    if duetask_selection_full is None:
      duetask_selection_full = "CANCEL"
    if duetask_selection_full != "CANCEL":
      try:
        duetask_index_str, duetask_selection = duetask_selection_full.split(' ', 1)
        duetask_index = int(duetask_index_str)
        duetask_selection = duetask_selection.lstrip()
      except:
        duetask_selection = "today"
        duetask_index = 0 
      for atask in multitasks:
        task_index_str, task = atask.split(' ', 1)
        task_index = int(task_index_str)
        tasktext = filteredtasklist[task_index][0]
        if tasktext != "subcatcheck419":
          task_key=hashstring(tasktext)
          thetask=taskerdb[task_key]
          thetask["duedate"]=str(thedatelist[duetask_index])
  return taskerdb

#
# MAIN
#

if args.category:
  taskerwrapper(args.category[0])
elif args.listcategories:
  taskerdb=dbfio(jsondb,"read") 
  showtasks(taskerdb,show="category",sortby="category",category=False,returnarray=False)
elif args.newtask:
  taskerdb=dbfio(jsondb,"read") 
  inputstring=""
  for aword in args.newtask:
    inputstring=inputstring+" "+aword
  inputstring=inputstring.strip()
  datain = inputstring.rsplit(' ', 2)[0]
  catin = inputstring.rsplit()[-2]
  priority = inputstring.rsplit()[-1]
  if not priority.isdigit():
    datain = datain + " " + catin
    catin = priority
    priority = "NONE"
  addtask(taskerdb,catin,"NONE",datain,priority)
else:
  taskerwrapper()
sys.exit()
