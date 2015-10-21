from Tkinter import *
import ttk
import tkFileDialog   #http://tkinter.unpythonic.net/wiki/tkFileDialog
import os

import sqlite3


app_name = "SQLite View"
version_num = "0.11"




#######################################
############# View interface #############
#######################################


def view_interface():

	global view
	view = Tk()
	view.title("View Tables")
	view.geometry('900x550')
	

	tree = ttk.Treeview(view)
	tree['show'] = "headings"


	if(db_type == "existing"):
		db_path = db_path_entry.get()
	else:
		db_path = new_db_entry.get()


	# build the connection with the .db file
	global con
	con = sqlite3.connect(db_path)
	table_list_cursor = con.execute("select name from sqlite_master where type = 'table';")
	table_list=[]
	for row in table_list_cursor:
		table_list.append(row[0])

	if len(table_list)==0:
		table_list.append("!EMPTY!")


	# global variable_table_choosing
	variable_table_choosing = StringVar(view)
	variable_table_choosing.set(table_list[0]) # default value

	Label(view, text="Table:", font='Helvetica 14 bold').place(x=30,y=30)
	table_choosing = apply(OptionMenu, (view, variable_table_choosing) + tuple(table_list))
	table_choosing.place(x=30, y=50)

	
	def choose_table():
		view_work()

	Button(view, text="Choose", comman=choose_table).place(x=30, y=75)


	# this two lines are added to help show the current table in viewer.
	# the specific table name will be assigned within function view_work below
	current_table_to_show = Label(view, text=" ", font='Helvetica 15 bold')
	current_table_to_show.place(x=200, y=20)

	# these two lines are added to hlep show the table size in viewer
	# the specific size will be assined within  the function view_work below
	table_size=Label(view, text=" ", font='Helvetica 12')
	table_size.place(x=200, y=260)
	
	# global view_work
	def view_work():

		# delete all the entries in the tree currently
		for i in tree.get_children():
			tree.delete(i)

		table_choosed=variable_table_choosing.get()
		temp_result = con.execute("select * from "+table_choosed)
		temp_column_name = con.execute("pragma table_info(" + table_choosed + ");").fetchall()
		
		global column_name
		column_name=[]
		for i in range(len(temp_column_name)):
			column_name.append(temp_column_name[i][1])

		global query_result
		query_result = temp_result.fetchall()
		# if(view_all_flag != 1):
		# 	query_result=query_result[0:30]
		#query_result=query_result[0:30]
		global n_row
		global n_col
		n_row = len(query_result)
		n_col = len(query_result[0])


		tree["columns"]=column_name
		for i in column_name:
			tree.column(i, width=80)
			tree.heading(i, text=i)

		if(n_row>=30):
			for i in range(30):
				tree.insert("", "end", text=str(i+1), values=query_result[i])
		else:
			for i in range(n_row):
				tree.insert("", "end", text=str(i+1), values=query_result[i])
		
		# current_table_to_show = StringVar()
		# current_table_to_show_label = Label(view, textvariable=current_table_to_show)
		# current_table_to_show_label.place(x=200, y=20)
		# current_table_to_show.set("Current Table: "+variable_table_choosing.get())

		
		current_table_to_show.configure(text="Current Table: "+str(variable_table_choosing.get()))
		table_size.configure(text = "Size: " + str(n_row) + " rows, " + str(n_col) + " columns.")

	view_work()




	def view_all():
		view = Tk()
		view.title("View all")
		view.geometry('1000x300')
		tree = ttk.Treeview(view)
		tree['show'] = 'headings'

		tree["columns"]=column_name
		for i in column_name:
			tree.column(i, width=100)
			tree.heading(i, text=i)
		for i in range(n_row):
			tree.insert("", "end", text=str(i+1), values=query_result[i])
		tree.place(x=20, y=20)

		Label(view, text="Size: " + str(n_row) + " rows, " + str(n_col) + " columns.", font='Helvetica 12').place(x=20, y=230)

	Button(view, text="View all", command=view_all).place(x=30, y=120)





	def export_to_csv():
		save_path = tkFileDialog.asksaveasfilename(title="Where to export?", defaultextension="*.csv")
		
		
		csv_content=[",".join(column_name)]
		for i in range(n_row):
			for j in range(n_col):
				query_result[i]=list(query_result[i])
				query_result[i][j] = str(query_result[i][j])
			csv_content.append(",".join(query_result[i]))
		
		to_write = "\n".join(csv_content)

		f=open(save_path, "w")
		f.write(to_write)
		f.close()

	Button(view, text="Export all to .CSV", command=export_to_csv).place(x=30, y=150)

	tree.place(x=200, y=50)
 	# tree view:
 	# http://www.tkdocs.com/tutorial/tree.html



 	Label(view, text="Query:", font='Helvetica 15 bold').place(x = 200, y= 300)
	sentence=StringVar()
	query=Text(view, width=40, height=5, background="lightblue")
	query.place(x = 200, y = 320)

	def submit():
		con.execute(query.get('1.0', END))
		con.commit()
		view_work()


	Button(view, text="Submit", comman=submit).place(x=510, y=350)


	# STATUS module

	Label(view, text="Status:", font='Helvetica 15 bold').place(x = 200, y= 430)
	Label(view, text="Database File Location: "+db_path).place(x = 200, y = 450)
	# BUG:  for now, if I create a table with SQL execution, the number here will not change correspondingly.
	status_num_of_table = Label(view, text="Number of Tables: " + str(len(table_list)))
	status_num_of_table.place(x = 200, y = 470)

	# the lines below are used to modify the unit of file size automatically. 
	# The dafault unit is "bytes".
	# if the file size is too big, it would be better to use 'Kb' or 'Mb' correspondingly.
	db_file_size = os.path.getsize(db_path)
	if db_file_size > 10485760:
		db_file_size = round(db_file_size/1048576.0, 3)
		db_file_size_unit = "Mb"
	elif db_file_size > 102400:
		db_file_size = round(db_file_size/1024.0, 3)
		db_file_size_unit = "Kb"
	else:
		db_file_size_unit = "Bytes"

	Label(view, text="Database File Size: "+str(db_file_size)+" "+db_file_size_unit).place(x = 200, y = 490)



#######################################
############# Begin GUI #############
#######################################

root=Tk()

'''
# this three lines help detect the screen resolution and set the size of the window to be the
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print screen_height
print screen_width
root.geometry(str(screen_width) + "x" + str(screen_height))
'''
root.title(app_name + " " +version_num)
root.geometry('500x200')


db_type="?"

db_path_label = Label(root, text = "Open existing database (.db):")
db_path_label.place(x = 50, y = 50)

name=StringVar()
db_path_entry = Entry(root, textvariable = name)
db_path_entry.place(x = 50, y = 70)

def get_db_path():
	global db_type
	db_type = "existing"
	types = [('.db files', '*.db')]
	temp_path = tkFileDialog.askopenfilename(title = 'Existing .db file', filetypes = types)
	db_path_entry.delete(0, END)
	db_path_entry.insert(0, temp_path)

Button(root, text = 'Browse...', command = get_db_path).place(x = 250, y = 70)


Button(root, text = 'open', command = view_interface).place(x = 50, y=100 )



# new_db_label = Label(root, text = "Build a new database:")
# new_db_label.place(x = 50, y = 140)

# name=StringVar()
# new_db_entry = Entry(root, textvariable = name)
# new_db_entry.place(x = 50, y = 160)

# def get_new_db_name():
# 	global db_type
# 	db_type = "new"
# 	temp_path = tkFileDialog.asksaveasfilename(title = 'Build new database')
# 	new_db_entry.delete(0, END)
# 	new_db_entry.insert(0, temp_path+'.db')

# Button(root, text = 'Browse...', command = get_new_db_name).place(x = 250, y = 160)
# Button(root, text = 'Build', command = main_interface).place(x = 50, y=190 )


mainloop()