from Tkinter import *
import ttk
import tkFileDialog
import tkMessageBox
import ScrolledText
import subprocess, string, os, uuid, time, sys, datetime, logging, math, socket

main = Tk()
main.resizable(width=False, height=False)
cwd = os.getcwd()

logging.basicConfig(filename=cwd + "\\Log.txt", level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%y %H:%M:%S')
############################################################################
########################### GUI Structure
############################################################################
tabFrame = Frame(main)
tabFrame.grid(row=0)

tabLocation = ttk.Notebook(tabFrame)
tabLocation.grid(row=0, column=0, columnspan=50, rowspan=49, sticky='NESW')

tab_deploy = ttk.Frame(tabLocation)
tabLocation.add(tab_deploy, text="FIO Menu")

tab_advanced = ttk.Frame(tabLocation)
tabLocation.add(tab_advanced, text="Advanced")


def frame_gui():
    titleLabel = main
    titleLabel.title("EasyFIO")


# tab1 variables
wim_location = StringVar()
check_desktopfiles = IntVar()
check_desktopfiles.set(1)
destination_drive = ""
volume_list = []
selected_volume = StringVar()
wim_size = ""

runTime = StringVar()

def frame_deploy():
    global destination_drive

    tab1_lbl_destintation = Label(tab_deploy, text=" Logical Drives:", anchor=NW, width=70)
    tab1_lbl_destintation.grid(row=0)
    tab1_lstbx_destinationdrives = Listbox(tab_deploy, width=80, selectmode=SINGLE)
    tab1_lstbx_destinationdrives.bind('<<ListboxSelect>>', tab1_lstbx_select)
    tab1_lstbx_destinationdrives.grid(row=1, rowspan=2)
    generate_volume_list()
    for item in volume_list:
        tab1_lstbx_destinationdrives.insert(END, item)

    timeCompartment = Frame(tab_deploy)

    timeCompartment.grid(row=1, column=1)
    tab1_btn_setTimeText = Label(timeCompartment, text="Set Time in (s)Seconds", width=20)
    tab1_btn_setTimeText.grid(row=0)
    tab1_btn_setTimeInput = Entry(timeCompartment, textvariable=runTime, width=25, justify=RIGHT)
    tab1_btn_setTimeInput.grid(row=1, pady=(0,80))

    tab1_chbx_CheckAll = Checkbutton(timeCompartment, text="Run FIO on all drives", variable=check_desktopfiles)
    tab1_chbx_CheckAll.deselect()
    tab1_chbx_CheckAll.grid(row=2, sticky=W)

    tab1_deploy_exit = Frame(timeCompartment)
    tab1_deploy_exit.grid(row=3)
    tab1_btn_deploy = Button(tab1_deploy_exit, width=10, text="Start", command=tab1_trig_start)
    tab1_btn_deploy.grid(row=0, column=0)
    tab1_btn_exit = Button(tab1_deploy_exit, width=10, text="Exit", command=exit_script)
    tab1_btn_exit.grid(row=0, column=1)


    destination_drive = tab1_lstbx_destinationdrives.get(ACTIVE)


# tab 2 variables
trafficType = StringVar()
trafficSize = StringVar()


def frame_advanced():
    advanced_size_lbl = Label(tab_advanced, text="Select traffic size:", anchor=NW)
    advanced_size_lbl.grid(row=0)

    GbOne = Radiobutton(tab_advanced, text="1Gb", variable=trafficSize, value=1)
    GbOne.select()
    GbOne.grid(row=1, column=0)
    Radiobutton(tab_advanced, text="2Gb", variable=trafficSize, value="2").grid(row=1, column=1)
    Radiobutton(tab_advanced, text="4Gb", variable=trafficSize, value="4").grid(row=1, column=2)
    Radiobutton(tab_advanced, text="8Gb", variable=trafficSize, value="8").grid(row=1, column=3)

    advanced_type_lbl = Label(tab_advanced, text="Select traffic type:", anchor=NW)
    advanced_type_lbl.grid(row=2)

    typeOne = Radiobutton(tab_advanced, text="Random R/W", variable=trafficType, value=1)
    typeOne.select()
    typeOne.grid(row=3, column=0, padx=(50,0))
    Radiobutton(tab_advanced, text="Queue Depth 1 R/W", variable=trafficType, value=2).grid(row=3, column=1)
    Radiobutton(tab_advanced, text="Queue Depth 2 R/W", variable=trafficType, value=4).grid(row=3, column=2)
    Radiobutton(tab_advanced, text="8", variable=trafficType, value=8).grid(row=3, column=3)



def tab1_lstbx_select(event):
    global destination_drive
    widget = event.widget
    selection = widget.curselection()
    destination_drive = widget.get(selection)


############################################################################
########################### GUI Triggers
############################################################################
# tab1
def tab1_trig_start():
    selected_volume = destination_drive.split()[0][0]
    f = open("fioConfig.txt", "w+")
    f.write("[global]\nbs=512k\n")
    f.write("size=%sG\n" %(trafficSize.get()))
    f.write("time_based\n")
    f.write("runtime=%s\n" %(runTime.get()))
    f.write(";;rw=rw\n")
    f.write("direct=1\n")
    f.write("iodepth=32\n;;group_reporting\n\n")

    f.write("[job1]\nrw=read\nfilename=%s\:fiofile1\n\n" %(selected_volume))
    f.write("[job2]\nrw=randread\nfilename=%s\:fiofile2\n\n" % (selected_volume))
    f.write("[job3]\nrw=write\nfilename=%s\:fiofile1\n\n" % (selected_volume))
    f.write("[job4]\nrw=randwrite\nfilename=%s\:fiofile2\n\n" % (selected_volume))

    f.close()

    fio_program = 'fio.exe'
    arg_file = 'fioConfig.txt'

    subprocess.call([fio_program, arg_file])
    exit()

def tab1_lstbx_select(event):
    global source_volume
    widget = event.widget
    selection = widget.curselection()
    source_volume = widget.get(selection)

def tab2_radio_one_select(event):
    global trafficSize
    widget = event.widget
    selection = widget.curselection()
    trafficSize = widget.get(selection)

def tab2_radio_two_select(event):
    global trafficType
    widget = event.widget
    selection = widget.curselection()
    trafficType = widget.get(selection)

############################################################################
########################### Functions
############################################################################


def generate_volume_list():
    os.system("color")
    global volume_list
    while len(volume_list) > 0:
        volume_list.pop()
    poll_logic_drives = subprocess.Popen("wmic logicaldisk get name,volumename", stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
    for line in poll_logic_drives.stdout.readlines():
        if "VolumeName" in line:
            continue
        volume_list.append(line.rstrip())
        volume_list = filter(None, volume_list)
    return volume_list


def error_stop(errorname):
    os.system("color c0")
    raise ValueError(str(errorname))


def exit_script():
    exit()


############################################################################
########################### Execution
############################################################################
os.system("cls")
os.system("color")
# tech_check()
frame_gui()
frame_deploy()
frame_advanced()
main.mainloop()