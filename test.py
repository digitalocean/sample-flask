from tkinter import *

dato= Tk()
dato.title("calculadora")
 
e=Entry(dato, width=35, borderwidth=5)
e.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

def button_click(number):
    current=e.get()
    e.delete(0, END)
    e.insert(0, str(current)+ str(number))
    
def button_clear():
    e.delete(0, END)
    
def button_add():
    first_number= e.get()
    global f_num
    global math
    math="adicion"
    f_num=int(first_number)
    e.delete(0, END)

def button_equal():
    second_number = e.get()
    e.delete(0, END)
    if math == "addition":
        e.insert(0, f_num + int(second_number))
    if math == "resta":
        e.insert(0, f_num - int(second_number))
    if math == "multiplicacion":
        e.insert(0, f_num * int(second_number))
    if math == "division":
        e.insert(0, f_num / int(second_number))
    
def button_resta():
    first_number= e.get()
    global f_num
    global math
    math="resta"
    f_num= int(first_number)
    e.delete(0, END)

def button_multiplicacion():
    first_number= e.get()
    global f_num
    global math
    math="multiplicacion"
    f_num= int(first_number)
    e.delete(0, END)    
    
    
def button_division():
    first_number= e.get()
    global f_num
    global math
    math="division"
    f_num= int(first_number)
    e.delete(0, END)

    
# se definen los botones aqui
button_1= Button(dato, text="1", padx="40", pady=20, command=lambda: button_click(1))
button_2= Button(dato, text="2", padx="40", pady=20, command=lambda: button_click(2)) 
button_3= Button(dato, text="3", padx="40", pady=20, command=lambda: button_click(3))
button_4= Button(dato, text="4", padx="40", pady=20, command=lambda: button_click(4))
button_5= Button(dato, text="5", padx="40", pady=20, command=lambda: button_click(5))
button_6= Button(dato, text="6", padx="40", pady=20, command=lambda: button_click(6))
button_7= Button(dato, text="7", padx="40", pady=20, command=lambda: button_click(7))
button_8= Button(dato, text="8", padx="40", pady=20, command=lambda: button_click(8))
button_9= Button(dato, text="9", padx="40", pady=20, command=lambda: button_click(9))
button_0= Button(dato, text="0", padx="40", pady=20, command=lambda: button_click(0))
button_add= Button(dato,text="+", padx="39", pady=20, command=button_add)
button_equal= Button(dato,text="=", padx="91", pady=20, command=button_equal)
button_clear= Button(dato,text="C", padx="79", pady=20, command= button_clear)

button_resta= Button(dato,text="-", padx="39", pady=20, command=button_resta)
button_multiplicacion= Button(dato,text="*", padx="39", pady=20, command=button_multiplicacion)
button_division= Button(dato,text="/", padx="39", pady=20, command=button_division)
#aqui se aplicara para que aprete los boton
button_1.grid(row=3, column=0)
button_2.grid(row=3, column=1)
button_3.grid(row=3, column=2)

button_4.grid(row=2, column=0)
button_5.grid(row=2, column=1)
button_6.grid(row=2, column=2)

button_7.grid(row=1, column=0)
button_8.grid(row=1, column=1)
button_9.grid(row=1, column=2)

button_0.grid(row=4, column=0)
button_clear.grid(row=4, column=1, columnspan=2)
button_add.grid(row=5, column=0)
button_equal.grid(row=5, column=1, columnspan=2)

button_resta.grid(row=6, column=0)
button_multiplicacion.grid(row=6, column=1)
button_division.grid(row=6, column=2)
dato.mainloop()