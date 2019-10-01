# Shania Ie and Pooja Pathak
# CIS 41B
# Lab 3

"""
Description:
Lab3front.py handles all the GUI. It is responsible for the interaction between the user and the application.
There are 2 main windows, a main window and a dialog window.
"""
import tkinter as tk
import sqlite3
import tkinter.messagebox as tkmb

class MainWin(tk.Tk):
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        Creates a main Window with a label for the user to enter the first letter of the country name in an Entry box. 
        Once the user enters a letter, it displays the matching country names in a list box. The list box only allows one selection
        from the list. 
        '''
        super().__init__(*args, **kwargs)
        
        self.title("Country")
        tk.Label(self, text = "Enter first letter of the country name").grid()
        self.choice = tk.StringVar()
        E = tk.Entry(self, textvariable = self.choice)
        E.grid(row = 0, column = 1)
        E.bind("<Return>",self.selectCountry)  #bind the Entry box to callback function selectCountry
        tk.Label(self, text = "Click to choose one country").grid(row = 1, column = 0, sticky = 'w')
        
        self.LB = tk.Listbox(self, height = 10, width = 40)
        self.LB.grid(row = 2, columnspan = 2)
        
        self.conn = sqlite3.connect('Country.db') #Connect to 'Country.db' database
        self.cur = self.conn.cursor()
        #create a set of first letters of all the countries in the database
        self.countrySet = {country[0][:1] for country in self.cur.execute("SELECT country FROM CountryDB")}
        
    def selectCountry(self, letter):
        '''
        selectCountry : checks whether the user input is valid, by matching it against a list of countries that start with that letter. 
                        If the user input is valid, insert a sorted list of those countries into the listbox. 
        Arguments : letter(the user input)
        Returns: None
        '''
        self.LB.delete(0,tk.END)
        letter = self.choice.get().upper().strip()
        
        if letter in self.countrySet:
            self.countryList = sorted([country[0] for country in self.cur.execute("SELECT country FROM CountryDB") if letter == country[0][:1]])
            self.LB.insert(tk.END, *self.countryList)
            self.LB.bind('<<ListboxSelect>>', self.callbackFct)
        
        #Display error message if user enters invalid input letter such as "abc"
        elif len(letter) > 1:
            tkmb.showerror("Error","Enter a letter only", parent=self)
        #Display error message if user enters a letter that has no corresponding country name.
        else:
            tkmb.showerror("Error","No country in database with starting letter " + str(letter), parent=self)
    
    
    def callbackFct(self, event):
        '''
        callbackFct:
        If the user clicks user clicks to select a country name from the listbox,
        open a display window with the popular names for that country.
        '''
        userChoice = self.LB.curselection()
        selection = self.countryList[userChoice[0]]
        dwin = DisplayWin(selection, self.cur)   #Create a display window
    
    def endfct(self):
        ''' 
        endfct:
            If the user clicks X on the main window, open a confirmation messagebox, "Are you sure you wnat to quit?"
            If the user clicks Ok, (return value : True), the database is closed and the main window is destroyed.
        '''
        state = tkmb.askokcancel("Confirmation", "Are you sure you want to quit?", parent=self)
        if state == True:
            self.conn.close()
            self.destroy()
    
class DisplayWin(tk.Toplevel):
    def __init__(self, userChoice, cur, *args, **kwargs):
        '''
        Constructor 
        The display Window has an explanation with thse chosen country name. (Most popular names for ______")
        It also has a list box (with 10 lines of text) that displays a list of the most popular names for the country selected.
        A vertical scrollbar, since most countries have more than 10 names. 
        The popular names are displayed in  alphabetical order. 
        '''
        super().__init__(*args, **kwargs)
        self.focus_set() 
        self.title("List of Popular Names")
        tk.Label(self,text = "Most popular names for " + userChoice).grid()
        
        S = tk.Scrollbar(self)
        S.grid(column = 3, sticky = 'ns')
        LB = tk.Listbox(self, height = 10, width = 40, yscrollcommand = S.set, selectmode= "none")
        S.config(command = LB.yview)
        
        LB.grid(row = 1, columnspan = 2)
        cur.execute("SELECT * FROM CountryDB WHERE country = ?", (userChoice,))
        nameList = {names.strip() for names in cur.fetchone()[1:] if names != None}
        LB.insert(tk.END, *sorted(nameList))
        
def main():
    mw = MainWin()
    mw.protocol("WM_DELETE_WINDOW", mw.endfct)
    mw.mainloop()

main()