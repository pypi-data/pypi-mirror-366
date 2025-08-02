#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import os
import subprocess

class GuiMp3ToolsApp:
    def __init__(self, master=None):
        # build ui
        self.notebook = ttk.Notebook(master)
        self.notebook.configure(height=600, width=800)
        self.frame_merge = ttk.Frame(self.notebook)
        self.frame_merge.configure(height=200, width=200)
        label3 = ttk.Label(self.frame_merge)
        label3.configure(state="normal", text='Working Directory:')
        label3.grid(column=0, row=0)
        entry1 = ttk.Entry(self.frame_merge)
        self.workingdir = tk.StringVar()
        self.workingdir.set(os.getcwd())
        entry1.configure(textvariable=self.workingdir)
        entry1.grid(column=1, padx=10, row=0, sticky="ew")
        frame12 = ttk.Frame(self.frame_merge)
        frame12.configure(height=200, padding=5, relief="sunken", width=200)
        label9 = ttk.Label(frame12)
        label9.configure(text='Command parameters:')
        label9.grid(column=0, columnspan=2, row=0, sticky="ew")
        label10 = ttk.Label(frame12)
        label10.configure(text='Directory:')
        label10.grid(column=0, row=1, sticky="e")
        label12 = ttk.Label(frame12)
        label12.configure(text='FooBar2000 Path:')
        label12.grid(column=0, row=3, sticky="e")
        label13 = ttk.Label(frame12)
        label13.configure(state="normal", text='Waiting Time [s]:')
        label13.grid(column=0, row=4, sticky="e")
        entry3 = ttk.Entry(frame12)
        self.mergedir = tk.StringVar(value='.')
        entry3.configure(textvariable=self.mergedir)
        _text_ = '.'
        entry3.delete("0", "end")
        entry3.insert("0", _text_)
        entry3.grid(column=1, row=1, sticky="ew")
        entry5 = ttk.Entry(frame12)
        self.mergefoobarpath = tk.StringVar(
            value='.')
        entry5.configure(textvariable=self.mergefoobarpath)
        entry5.grid(column=1, row=3, sticky="ew")
        entry6 = ttk.Entry(frame12)
        self.mergewaittime = tk.IntVar(value=5)
        entry6.configure(textvariable=self.mergewaittime)
        _text_ = '5'
        entry6.delete("0", "end")
        entry6.insert("0", _text_)
        entry6.grid(column=1, row=4, sticky="ew")
        button1 = ttk.Button(frame12)
        button1.configure(text='Start Script')
        button1.grid(
            column=0,
            columnspan=3,
            padx=10,
            pady=10,
            row=5,
            sticky="nsew")
        button1.configure(command=self.startscript)
        buttonfoo = ttk.Button(frame12)
        buttonfoo.configure(text='Start foobar2000')
        buttonfoo.grid(
            column=2,
            padx=10,
            pady=10,
            row=3,
            sticky="nsew")
        buttonfoo.configure(command=self.startfoo)
        label1 = ttk.Label(frame12)
        self.cmdtext = tk.StringVar()
        label1.configure(font="TkFixedFont", textvariable=self.cmdtext)
        label1.grid(column=0, columnspan=2, row=8, sticky="ew")
        separator1 = ttk.Separator(frame12)
        separator1.configure(orient="horizontal")
        separator1.grid(column=0, columnspan=2, row=7, sticky="ew")
        checkbutton1 = ttk.Checkbutton(frame12)
        self.mergesubfoldermode = tk.BooleanVar()
        self.mergesubfoldermode.set(True)
        checkbutton1.configure(
            state="normal",
            text='Subfolder Mode',
            variable=self.mergesubfoldermode)
        checkbutton1.grid(column=1, row=2, sticky="w")
        frame12.grid(column=0, columnspan=2, row=1, sticky="nsew")
        frame12.rowconfigure(0, pad=10)
        frame12.rowconfigure(6, weight=1)
        frame12.rowconfigure("all", pad=10)
        frame12.columnconfigure(0, pad=10)
        frame12.columnconfigure(1, weight=1)
        self.frame_merge.grid(column=0, row=0, sticky="nsew")
        self.frame_merge.rowconfigure(0, pad=10)
        self.frame_merge.rowconfigure(1, weight=1)
        self.frame_merge.columnconfigure(0, pad=10)
        self.frame_merge.columnconfigure(1, weight=1)
        self.notebook.add(
            self.frame_merge,
            state="normal",
            sticky="nsew",
            text='merge')
        self.frame_createsubdirs = ttk.Frame(self.notebook)
        self.frame_createsubdirs.configure(height=200, width=200)
        label15 = ttk.Label(self.frame_createsubdirs)
        label15.configure(state="normal", text='Working Directory:')
        label15.grid(column=0, row=0)
        entry7 = ttk.Entry(self.frame_createsubdirs)
        entry7.configure(textvariable=self.workingdir)
        entry7.grid(column=1, row=0, sticky="ew")
        frame14 = ttk.Frame(self.frame_createsubdirs)
        frame14.configure(height=200, padding=5, relief="sunken", width=200)
        label16 = ttk.Label(frame14)
        label16.configure(text='Command parameters:')
        label16.grid(column=0, columnspan=2, row=0, sticky="ew")
        label17 = ttk.Label(frame14)
        label17.configure(text='Directory:')
        label17.grid(column=0, row=1, sticky="e")
        label18 = ttk.Label(frame14)
        label18.configure(state="normal", takefocus=False, text='Group Size:')
        label18.grid(column=0, row=2, sticky="e")
        label19 = ttk.Label(frame14)
        label19.configure(text='File Filter:')
        label19.grid(column=0, row=3, sticky="e")
        entry9 = ttk.Entry(frame14)
        self.createdir = tk.StringVar(value='.')
        entry9.configure(textvariable=self.createdir)
        _text_ = '.'
        entry9.delete("0", "end")
        entry9.insert("0", _text_)
        entry9.grid(column=1, row=1, sticky="ew")
        entry10 = ttk.Entry(frame14)
        self.creategroupsize = tk.StringVar(value='15')
        entry10.configure(textvariable=self.creategroupsize)
        _text_ = '15'
        entry10.delete("0", "end")
        entry10.insert("0", _text_)
        entry10.grid(column=1, row=2, sticky="ew")
        entry11 = ttk.Entry(frame14)
        self.createfilefilter = tk.StringVar(value='.mp3')
        entry11.configure(textvariable=self.createfilefilter)
        _text_ = '.mp3'
        entry11.delete("0", "end")
        entry11.insert("0", _text_)
        entry11.grid(column=1, row=3, sticky="ew")
        button2 = ttk.Button(frame14)
        button2.configure(text='Start Script')
        button2.grid(
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            row=5,
            sticky="nsew")
        button2.configure(command=self.startscript)
        label2 = ttk.Label(frame14)
        label2.configure(font="TkFixedFont", textvariable=self.cmdtext)
        label2.grid(column=0, columnspan=2, row=8, sticky="ew")
        separator2 = ttk.Separator(frame14)
        separator2.configure(orient="horizontal")
        separator2.grid(column=0, columnspan=2, row=7, sticky="ew")
        checkbutton2 = ttk.Checkbutton(frame14)
        self.createcopymode = tk.BooleanVar()
        checkbutton2.configure(
            state="normal",
            text='Copy Mode',
            variable=self.createcopymode)
        checkbutton2.grid(column=1, row=4, sticky="w")
        frame14.grid(column=0, columnspan=2, row=1, sticky="nsew")
        frame14.rowconfigure(0, pad=10)
        frame14.rowconfigure(6, weight=1)
        frame14.rowconfigure("all", pad=10)
        frame14.columnconfigure(0, pad=10)
        frame14.columnconfigure(1, weight=1)
        self.frame_createsubdirs.grid(column=0, row=0, sticky="nsew")
        self.frame_createsubdirs.rowconfigure(0, pad=10)
        self.frame_createsubdirs.rowconfigure(1, weight=1)
        self.frame_createsubdirs.columnconfigure(0, pad=10)
        self.frame_createsubdirs.columnconfigure(1, pad=10, weight=1)
        self.notebook.add(
            self.frame_createsubdirs,
            sticky="nsew",
            text='create subdirs')
        self.frame_removesubdirs = ttk.Frame(self.notebook)
        self.frame_removesubdirs.configure(height=200, width=200)
        label22 = ttk.Label(self.frame_removesubdirs)
        label22.configure(state="normal", text='Working Directory:')
        label22.grid(column=0, row=0)
        entry13 = ttk.Entry(self.frame_removesubdirs)
        entry13.configure(textvariable=self.workingdir)
        entry13.grid(column=1, row=0, sticky="ew")
        frame16 = ttk.Frame(self.frame_removesubdirs)
        frame16.configure(height=200, padding=5, relief="sunken", width=200)
        label23 = ttk.Label(frame16)
        label23.configure(text='Command parameters:')
        label23.grid(column=0, columnspan=2, row=0, sticky="ew")
        label24 = ttk.Label(frame16)
        label24.configure(text='Directory:')
        label24.grid(column=0, row=1, sticky="e")
        label25 = ttk.Label(frame16)
        label25.configure(justify="left", text='Subfolder Filter:')
        label25.grid(column=0, row=2, sticky="e")
        label26 = ttk.Label(frame16)
        label26.configure(text='File Filter:')
        label26.grid(column=0, row=3, sticky="e")
        entry15 = ttk.Entry(frame16)
        self.removedir = tk.StringVar(value='.')
        entry15.configure(textvariable=self.removedir)
        _text_ = '.'
        entry15.delete("0", "end")
        entry15.insert("0", _text_)
        entry15.grid(column=1, row=1, sticky="ew")
        entry16 = ttk.Entry(frame16)
        self.removesubfolderfilter = tk.StringVar(value='*')
        entry16.configure(textvariable=self.removesubfolderfilter)
        _text_ = '*'
        entry16.delete("0", "end")
        entry16.insert("0", _text_)
        entry16.grid(column=1, row=2, sticky="ew")
        entry17 = ttk.Entry(frame16)
        self.removefilefilter = tk.StringVar(value='.mp3')
        entry17.configure(textvariable=self.removefilefilter)
        _text_ = '.mp3'
        entry17.delete("0", "end")
        entry17.insert("0", _text_)
        entry17.grid(column=1, row=3, sticky="ew")
        button3 = ttk.Button(frame16)
        button3.configure(text='Start Script')
        button3.grid(
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            row=6,
            sticky="nsew")
        button3.configure(command=self.startscript)
        label4 = ttk.Label(frame16)
        label4.configure(font="TkFixedFont", textvariable=self.cmdtext)
        label4.grid(column=0, columnspan=2, row=9, sticky="ew")
        separator3 = ttk.Separator(frame16)
        separator3.configure(orient="horizontal")
        separator3.grid(column=0, columnspan=2, row=8, sticky="ew")
        checkbutton3 = ttk.Checkbutton(frame16)
        self.removecopymode = tk.BooleanVar()
        checkbutton3.configure(text='Copy Mode', variable=self.removecopymode)
        checkbutton3.grid(column=1, row=4, sticky="w")
        checkbutton4 = ttk.Checkbutton(frame16)
        self.removeemptySubfolder = tk.BooleanVar()
        self.removeemptySubfolder.set(True)
        checkbutton4.configure(
            text='Remove Empty Subfolders',
            variable=self.removeemptySubfolder)
        checkbutton4.grid(column=1, row=5, sticky="w")
        frame16.grid(column=0, columnspan=2, row=1, sticky="nsew")
        frame16.rowconfigure(0, pad=10)
        frame16.rowconfigure(7, weight=1)
        frame16.rowconfigure("all", pad=10)
        frame16.columnconfigure(0, pad=10)
        frame16.columnconfigure(1, weight=1)
        self.frame_removesubdirs.grid(column=0, row=0, sticky="nsew")
        self.frame_removesubdirs.rowconfigure(0, pad=10)
        self.frame_removesubdirs.rowconfigure(1, weight=1)
        self.frame_removesubdirs.columnconfigure(0, pad=10)
        self.frame_removesubdirs.columnconfigure(1, pad=10, weight=1)
        self.notebook.add(
            self.frame_removesubdirs,
            sticky="nsew",
            text='remove subdirs')
        self.notebook.grid(column=0, row=0)
        self.notebook.bind(
            "<<NotebookTabChanged>>",
            self.updateCommand,
            add="")

        # Main widget
        self.mainwindow = self.notebook

    def run(self):
        self.mainwindow.mainloop()

    def startscript(self):
        self.updateCommand()
        os.chdir(self.workingdir.get())
        subprocess.Popen(self.cmdtext.get())
        
    def startfoo(self):
        foobarpath = self.mergefoobarpath.get()
        if self.mergefoobarpath.get() == ".":
            foobarpath = "C:/Program Files (x86)/foobar2000/foobar2000.exe"
        subprocess.Popen(foobarpath)
                   
    def updateCommand(self, event=None):
        tabtext = self.notebook.tab(self.notebook.select(), "text")
        if tabtext == "merge":
            self.cmdtext.set("mp3tools merge-mp3"
                             + " " + self.mergedir.get()
                             + " " + str(self.mergesubfoldermode.get())
                             + " " + self.mergefoobarpath.get()
                             + " " + str(self.mergewaittime.get())
                             )
        if tabtext == "create subdirs":
            self.cmdtext.set("mp3tools pack-subdirs"
                             + " " + str(self.creategroupsize.get())
                             + " " + self.createdir.get()
                             + " " + self.createfilefilter.get()
                             + " " + str(self.createcopymode.get())
                             )
        if tabtext == "remove subdirs":
            self.cmdtext.set("mp3tools unpack-subdirs"
                             + " " + self.removedir.get()
                             + " " + self.removesubfolderfilter.get()
                             + " " + self.removefilefilter.get()
                             + " " + str(self.removecopymode.get())
                             + " " + str(self.removeemptySubfolder.get())
                             )

if __name__ == "__main__":
    root = tk.Tk()
    app = GuiMp3ToolsApp(root)
    root.title("mp3tool")
    app.run()
