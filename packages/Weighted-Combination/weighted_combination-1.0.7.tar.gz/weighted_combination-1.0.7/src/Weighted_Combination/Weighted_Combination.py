import numpy as np
import os
from scipy.optimize import curve_fit
import math
import re
import tempfile
import shutil
from pathlib import Path

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

##############################################################################
# --- Functions for GUI
##############################################################################

##################################################
# --- Functions for graphing
##################################################

def plot_crys():
    counter = counter_crys.get()
    counter_crys.set(counter + 1)
    if counter % 2 == 0:
        global crys_plot
        crys_plot, = ax.plot(crys_data[:,0],crys_data[:,1], c='tab:red', label = 'Crystalline')
    elif counter % 2 == 1:
        crys_plot.remove()
    ax.legend()
    fig.canvas.draw()

def plot_amorph():
    counter = counter_amorph.get()
    counter_amorph.set(counter+1)
    if counter % 2 == 0:
        global amorph_plot
        amorph_plot, = ax.plot(amorph_data[:,0], amorph_data[:,1], c='purple', label='Amorphous')
    elif counter % 2 ==1:
        amorph_plot.remove()
    ax.legend()
    fig.canvas.draw()

def on_dropdown_selection(event):
    global selected_value
    print('1')
    selected_value = dropdown.get()
    translation_table = str.maketrans('', '', '[]')
    selected_value = selected_value.translate(translation_table)
    selected_value = selected_value[1:-1]
    
    for i in range(len(file_path_base_data)):
        if selected_value == file_path_base_data[i]:
            ax.clear()
            ax.plot(data[:,2*i], data[:,(2*i)+1], c='g', label='Data')
            ax.plot(X_PDF_Total[:,i], PDF_Plot_Total[:,i],c='#1f77b4', label='Weighted Fit')
            ax.plot(X_PDF_Total[:,i], Diff_Curve_Total[:,i], c='tab:red', label = 'Difference Curve')
            ax.hlines(offset_total[:,i],X_PDF[0],X_PDF[-1], colors='k')
            ax.legend()
            ax.set_title(selected_value)
            fig.canvas.draw()

def update():
    x=X_PDF
    ax.clear()
    ax.plot(x,Diff_Curve_Total[:,0],c='tab:red', label = 'Difference Curve')
    ax.plot(file_data[:,0],file_data[:,1],c='g', label = 'Data')
    ax.plot(X_PDF_Total[:,0],PDF_Plot_Total[:,0],c='#1f77b4', label = 'Weighted Fit')
    ax.set_title(file_path_base_data[0])
    ax.hlines(offset_total[:,0],x[0],x[-1], colors='k')
    ax.legend()
    fig.canvas.draw()
    
    if len(Amorphous_Fraction) > 1:
        fig2 = Figure(figsize=(6, 4), dpi=100)
        ax2 = fig2.add_subplot(111)
        canvas2 = FigureCanvasTkAgg(fig2, master=graph_frame)
        canvas2.get_tk_widget().grid(row=2, column=0)
        
        ax2.scatter(range(len(Amorphous_Fraction)),Amorphous_Fraction)
        for j in range(len(Amorphous_Fraction)):
            ax2.annotate(file_path_base_data[j][0:8],((j/len(Amorphous_Fraction)),Amorphous_Fraction[j]/Amorphous_Fraction[-1]), xycoords='axes fraction')
        ax2.grid()
        ax2.set_xticks([])
        fig2.canvas.draw()
    global dropdown
    dropdown = ttk.Combobox(graph_frame,values=file_path_base_data, width=50)
    dropdown.place(relx=1,rely=0, anchor='ne')
    dropdown.bind("<<ComboboxSelected>>", on_dropdown_selection)
    
##################################################
# --- Functions for reading files
##################################################        

def remove_blank_lines(file):
    file = Path(file)
    lines = file.read_text().splitlines()
    filtered = [
        line
        for line in lines
        if line.strip()
    ]
    file.write_text('\n'.join(filtered))

def add_symbol(filepath, symbol):
    temp_filepath = filepath + ".tmp"
    with open(filepath, 'r') as infile, open(temp_filepath, 'w') as outfile:
        for line in infile:
            # Check if the line contains any alphabetical characters
            if re.search(r'[a-df-zA-DF-Z]', line):
                outfile.write(symbol + line)
            else:
                outfile.write(line)

def create_temp(filepath):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    shutil.copy2(filepath, temp_file_path)
    remove_blank_lines(temp_file_path)
    add_symbol(temp_file_path, '#')
    temp_file.close()
    return temp_file_path + '.tmp'

def read_file_data(filepath):  
    try: 
        with open(filepath, 'r') as file: #opens each datafile
            data=np.loadtxt(file)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data

#opens file and returns data inside
def read_file_data_multiple(filepath):  
    global data
    try: 
        for i in range(len(filepath)):
            with open(filepath[i], 'r') as file: #opens each datafile
                if i == 0:
                    # global index
                    # index=skip_header(file)
                    data = np.loadtxt(file)
                    if data.shape[1] > 2:
                        data = data[:,:-1]
                else:
                    data_loaded = np.loadtxt(file)
                    if data_loaded.shape[1] > 2:
                        data_loaded = data_loaded[:,:-1]
                    data = np.concatenate((data, data_loaded), axis=1)
                print("File content:\n", data)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data
    
#used with amorphous button, opens file and puts name of file next to it
def select_file_amorph():
    global file_path_amorph
    file_path_amorph = filedialog.askopenfilename()
    file_path_base_amorph = os.path.basename(file_path_amorph)
    file_path_amorph_temp = create_temp(file_path_amorph)
    if file_path_amorph:
        print(f"Selected file: {file_path_base_amorph}")
        tk.Label(data_frame, text=file_path_base_amorph).grid(row=3,column=0, columnspan=2)
        global amorph_data, amorph_plot
        amorph_data = read_file_data(file_path_amorph_temp)
        
#used with crystalline button, opens file and puts name of file next to it
def select_file_crys():
    global file_path_crys
    file_path_crys = filedialog.askopenfilename()
    file_path_base_crys = os.path.basename(file_path_crys)
    file_path_crys_temp = create_temp(file_path_crys)
    if file_path_crys:
        print(f"Selected file: {file_path_base_crys}")
        tk.Label(data_frame, text=file_path_base_crys).grid(row=1,column=0, columnspan=2)
        global crys_data, crys_plot
        crys_data = read_file_data(file_path_crys_temp)

#used with data files button, opens file and puts name of file next to it
def select_files():
    global file_path_data, file_path_base_data
    file_path_data = filedialog.askopenfilenames()
    file_path_data = root.tk.splitlist(file_path_data)
    file_path_base_data = np.zeros(len(file_path_data), dtype=object)
    file_path_data_temp = np.zeros(len(file_path_data), dtype=object)
    for i in range(len(file_path_data)):
        file_path_base_data[i] = os.path.basename(file_path_data[i])
        file_path_data_temp[i] = create_temp(file_path_data[i])
    if file_path_data:
        print(f"Selected file: {file_path_base_data} \n")
        for j in range(len(file_path_base_data)):
            tk.Label(data_frame, text=file_path_base_data[j]).grid(row=6+j,column=0)
        global file_data
        file_data = read_file_data_multiple(file_path_data_temp)
    
##############################################################################
# Functions for Calculation
##############################################################################

#rounds final values
def round_to_first_nonzero(num):
    abs_num = abs(num)
    if abs_num >= 1:
        precision = 2
        return np.round(num,precision), precision 
    elif abs_num == 1 or abs_num == 0:
        precision = 2
        return np.round(num,precision),precision
    else:
        precision = -int(math.floor(math.log10(abs_num))) + 1 
        return np.round(num, precision), precision

#used for calculating amorphous fraction error
def fitting_func(r, f_a):
    return amorph_data[:, 1] * f_a + crys_data[:, 1] * (1-f_a)

# does the weighted PDF combination
def pdf():

    #loads raw data
    Amorphous_raw   = amorph_data
    Crystalline_raw = crys_data
    global Amorphous_Fraction
    Amorphous_Fraction = 0
    err=np.zeros(len(file_path_base_data))
    global X_PDF, Y_PDF

    global Crystalline, Amorphous
    Amorphous = np.copy(Amorphous_raw) #creates copy to prevent indexing error (would chop off more data each time it went through loop)
    Crystalline = np.copy(Crystalline_raw) #creates copy to prevent indexing error 
    LoadFile = file_data
    for j in range(len(file_path_base_data)):#loads comparison files
        X_PDF = LoadFile[:,2*j] 
        Y_PDF = LoadFile[:,(2*j)+1]
        popt, pcov = curve_fit(fitting_func, X_PDF, Y_PDF)
        pcov=np.sqrt(np.diag(pcov))

        err=pcov
    
        #Deletes data before nearest neighbor peak
        index = np.argmax(X_PDF>0.5)
        Y_PDF = Y_PDF[index:]
        X_PDF = X_PDF[index:]
        Crystalline = Crystalline[np.argmax(Crystalline[:,0]>0.5):]
        Amorphous = Amorphous[np.argmax(Amorphous[:,0]>0.5):]
    
        # Finds PDF fraction with smallest associated error
        error1 = 1E6
        i_all = 0
        for i in np.linspace(0,1,1001):
            Crystalline_PDF = Crystalline[:,1]*(1-i)
            Amorphous_PDF = Amorphous[:,1]*i
            PDF = Crystalline_PDF + Amorphous_PDF
            error2 = np.sum((PDF[1:]-Y_PDF[1:])**2)
            if error2 < error1:
                error1 = error2
                PDF_Plot = PDF   #make this have multiple columns
                i_all = np.append(i_all,i)
        Amorphous_Fraction = np.append(Amorphous_Fraction, max(i_all))
        
        global PDF_Plot_Total, X_PDF_Total, Diff_Curve_Total, err_total, offset_total
        if j == 0:
            PDF_Plot_Total = PDF_Plot
            PDF_Plot_Total = np.reshape(PDF_Plot_Total, (-1,1))
            X_PDF_Total = X_PDF
            X_PDF_Total = np.reshape(X_PDF_Total, (-1,1))
            err_total = err
            err_total = np.reshape(err_total, (-1,1))
        else:
            PDF_Plot_Total = np.column_stack((PDF_Plot_Total, PDF_Plot))
            X_PDF_Total = np.column_stack((X_PDF_Total, X_PDF))
            err_total = np.column_stack((err_total, err))
            
        #Finds Difference Curve        
        Crys_PDF_Diff = Crystalline[:,1]*(1-max(i_all))
        Amorph_PDF_Diff = Amorphous[:,1]*max(i_all)
        PDF_Diff = Crys_PDF_Diff + Amorph_PDF_Diff
        Difference_Curve = Y_PDF - PDF_Diff
        offset = - abs(min(min(PDF_Plot), min(Y_PDF))) - max(Difference_Curve)
        Difference_Curve = Difference_Curve[:] + offset
        if j == 0:
            Diff_Curve_Total = Difference_Curve
            Diff_Curve_Total = np.reshape(Diff_Curve_Total, (-1,1))
            offset_total = offset
            offset_total = np.reshape(offset,(-1,1))
        else:
            Diff_Curve_Total = np.column_stack((Diff_Curve_Total, Difference_Curve))
            offset_total = np.column_stack((offset_total, offset))
        print(Amorphous_Fraction) 
    Amorphous_Fraction = Amorphous_Fraction[1:]
    # if Amorphous_Fraction[0]:
    for j in range(len(file_path_base_data)):
        err_rounded, precision = round_to_first_nonzero(err_total[:,j])
        text = str(round(Amorphous_Fraction[j],precision)) + ' +/- ' + str(err_rounded)
        tk.Label(data_frame, text = text).grid(row=6+j, column=1)
    
    update()
        
##############################################################################
# --- Root Setup
##############################################################################

root = tk.Tk()
root.title("Amorphous Fraction Calculator")
select_files.counter=0

#Window Frame
frame = tk.Frame(root)
frame.pack()
frame.rowconfigure(0, weight=1)
frame.columnconfigure((0,1),weight=1)

#crys and amorph endmember frame
data_frame=tk.LabelFrame(frame, padx=100, pady=20)
data_frame.grid(row=1, column=0)
    
#text frame
text_frame = tk.LabelFrame(frame, padx=80, pady=20)
text_frame.grid(row=0, column=0)

#calculate frame
calc_frame = tk.LabelFrame(frame, padx=20,pady=20)
calc_frame.grid(row=2, column=0)

#Graph frame
graph_frame = tk.LabelFrame(frame, text = 'Graph', padx=20, pady=20)
graph_frame.grid(row=0, column=1, rowspan=4)

##############################################################################
# --- Text
##############################################################################

text = tk.Label(text_frame, text = 'Input a fully amorphous and fully crystalline data file and a \n weighted combination will be used to find the \n amorphous fraction.').grid(row=0, column=0)
text2 = tk.Label(text_frame, text='For best results make sure all data files only contain data \n or non-data lines are commented out using #.', pady=20).grid(row=1, column=0)


##############################################################################
# --- Crystalline Data file config
##############################################################################

crys_label = tk.Label(data_frame, text='Crystalline Data File').grid(row=0, column=0)
crys_button = tk.Button(data_frame, text="Select File", command=select_file_crys)
crys_blank = tk.Label(data_frame, text='', pady=10).grid(row=1, column=0)
crys_button.grid(row=0, column=1, sticky='e')

counter_crys = tk.IntVar()
counter_crys.set(0)
crys_show_button = tk.Button(data_frame, text='Show', command = plot_crys).grid(row=1, column = 2)

##############################################################################
# --- Amorphous Data File config
##############################################################################

amorph_label = tk.Label(data_frame, text='Amorphous Data File').grid(row=2, column=0)
amorph_blank = tk.Label(data_frame, text='').grid(row=3, column=0)
amorph_button = tk.Button(data_frame, text="Select File", command=select_file_amorph)
amorph_button.grid(row=2, column=1, sticky='e')

counter_amorph = tk.IntVar()
counter_amorph.set(0)
amorph_show_button = tk.Button(data_frame, text='Show', command=plot_amorph).grid(row=3, column = 2)
##############################################################################
# --- Data File List
##############################################################################

Data_label = tk.Label(data_frame, text='Calculated Fraction Data Files').grid(row=4, column=0)
Data_button = tk.Button(data_frame, text='Select File(s)',command = select_files).grid(row=4, column=1)
data_blank = tk.Label(data_frame, text='').grid(row=6, column=1)


tk.Label(data_frame, text='Amorphous Fraction').grid(row=5, column=1)
tk.Label(data_frame, text='File').grid(row=5, column=0)


##############################################################################
# --- Calculation
##############################################################################

Calc_button = tk.Button(calc_frame, text='Calculate Amorphous Fraction',command=pdf).grid(row=0,column=0)

##############################################################################
# --- Graph
##############################################################################
dropdown = ttk.Combobox(graph_frame,values='', width=50)
dropdown.place(relx=1,rely=0, anchor='ne')
dropdown.bind("<<ComboboxSelected>>", on_dropdown_selection)

fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
x=0
y=0
pdf=0
graph = ax.plot(x,y, label = 'Data')
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0)#pack(anchor='center', fill=tk.BOTH, expand=True) #toolbar
toolbar = NavigationToolbar2Tk(canvas, graph_frame, pack_toolbar=False)
toolbar.grid(row=1, column=0)
toolbar.update()
canvas.get_tk_widget().grid(row=0, column=0)#pack(side=tk.TOP, expand=True) #data graph

#anim = FuncAnimation(fig, update)


######################################## --- Initializes GUI
for h in data_frame.winfo_children():
    h.grid_configure(padx=10,pady=10)

# creates GUI
root.mainloop()