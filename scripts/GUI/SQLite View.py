from Tkinter import *
import ttk
import tkFileDialog   #http://tkinter.unpythonic.net/wiki/tkFileDialog
import os

import sqlite3


app_name = "SQLite View"
version_num = "0.14"


#######################################
############# View interface #############
#######################################

# we define here SQL_command here for a feature later in "SQL Execution" and "submit" module
SQL_command="" # this is a meaningful & useful definiton

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
		table_list.append("-EMPTY-")


	# a modeule to deal with the situation in which the .db file is empty.
	# will give a reminding and close the window.
	if table_list[0]=='-EMPTY-':
		empty_warning=Tk()
		empty_warning.title("Empty Database File")
		empty_warning.geometry('250x100')

		view.destroy()

		w = Message(empty_warning, text="This database file is empty.", width=300, font='Helvetica 15')
		w.place(x=35, y=20)

		def close():
			empty_warning.destroy()
		Button(empty_warning, text="Okay", command=close).place(x=100, y=60)



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

	Button(view, text="Export to .CSV", command=export_to_csv).place(x=30, y=150)


	def import_from_csv():
		global import_interface
		import_interface = Tk()
		import_interface.geometry('330x250')
		import_interface.title("Import Table From .CSV File")

		# entry for the path and name of the CSV file
		Label(import_interface, text="Target CSV Path:").place(x=30, y=30)
		csv_name=StringVar()
		csv_entry = Entry(import_interface, textvariable = csv_name)
		csv_entry.place(x=30, y=50)


		def browse_csv_path():
			types = [('.CSV files', '*.csv')]
			csv_path = tkFileDialog.askopenfilename(title = 'Importing Table From CSV File', filetypes = types)
			csv_entry.delete(0, END)
			csv_entry.insert(0, csv_path)
		Button(import_interface, text="Browse", command=browse_csv_path).place(x=230, y=50)


		# specify the name of the new table (which will be built from the CSV file)
		Label(import_interface, text="Import into Table:").place(x=30, y=100)
		table_name=StringVar()
		table_name_entry = Entry(import_interface, textvariable = table_name)
		table_name_entry.place(x=30, y=120)


		def import_act():
			
			f=open(csv_entry.get())
			content = f.readlines()

			# this function split each row from CSV file into format ready for SQL inserting
			def split_row(x_row):
				splitted_row = x_row.split(',')
				splitted_row[len(splitted_row)-1] = splitted_row[len(splitted_row)-1].split('\n')[0]
				return splitted_row
			csv_column_name = split_row(content[0])


			# check if the new table name is empty
			if table_name_entry.get()=="":
				temp = Tk()
				temp.title("Empty Table Name")
				temp.geometry('250x100')
				Message(temp, text="Empty Table Name", width=300, font='Helvetica 14').place(x=35, y=20)

				def close():
					temp.destroy()
				Button(temp, text="Okay", command=close).place(x=100, y=60)
				return 0

			# check if the new table name already exist
			if table_name_entry.get() in table_list:
				temp = Tk()
				temp.title("Table Name exists")
				temp.geometry('250x100')
				Message(temp, text="Table Name exists", width=300, font='Helvetica 14').place(x=35, y=20)

				def close():
					temp.destroy()
				Button(temp, text="Okay", command=close).place(x=100, y=60)
				return 0


			# build the table by SQL
			for i in range(len(csv_column_name)):
				csv_column_name[i] = csv_column_name[i]+" text"
			temp=','.join(csv_column_name)
			build_command = "create table " + table_name_entry.get()+ "("+ temp +");"
			
			con.execute(build_command)
			con.commit()

			# insert the content of the CSV into the table whcih was built above
			for i in range(1, len(content)):
				
				content[i]=split_row(content[i])
				for j in range(len(content[i])):
					content[i][j] = "'" + content[i][j] + "'"

				temp = ",".join(content[i])
				insert_command="insert into " + table_name_entry.get()+ " values("+temp+");"
				
				con.execute(insert_command)
				con.commit()

			# the block below is to remind the user once the importing is finished
			importing_finished_interface = Tk()
			importing_finished_interface.title("Importing Finished")
			importing_finished_interface.geometry('250x100')
			Message(importing_finished_interface, text="Importing finished", width=300, font='Helvetica 14').place(x=35, y=20)

			import_interface.destroy()

			def close():
				importing_finished_interface.destroy()
			Button(importing_finished_interface, text="Okay", command=close).place(x=100, y=60)

			view.destroy()
			view_interface()

		Button(import_interface, text="import", command=import_act).place(x=80, y=180)


	Button(view, text="Import from .CSV", command=import_from_csv).place(x=30, y=180)






	tree.place(x=200, y=50)
 	# tree view:
 	# http://www.tkdocs.com/tutorial/tree.html


 	# SQL Execution Module
 	Label(view, text="Query:", font='Helvetica 15 bold').place(x = 200, y= 300)
	sentence=StringVar()
	query=Text(view, width=40, height=5, background="lightblue")
	query.place(x = 200, y = 320)
	query.insert(END, SQL_command)

	def submit():

		# according to current workflow, once the execution succecced, the "view" window will be closed and built again.
		# then the SQL command entered last time will be gone.
		# but in most situations, we want the SQL command we entered to keep there.
		global SQL_command
		SQL_command = query.get('1.0', END)

		temp = con.execute(SQL_command)
		con.commit()
		selected_column_names = temp.description
		temp = temp.fetchall()

		# if the execution will lead to any content returned, then a separate window will be built to show these contents
		# This feature is mainly for 'select' execution
		if len(temp)>0:
			
			n_row=len(temp)
			n_col=len(temp[0])
			

			# to obtain the column names of the selected result
			selected_column_names = list(selected_column_names)
			for i in range(len(selected_column_names)):
				selected_column_names[i] = selected_column_names[i][0]

			execution_show = Tk()
			execution_show.title('Execution Result')
			execution_show.geometry('1000x320')
			Label(execution_show, text="SQL Command Executed:").place(x=20, y=20)
			Label(execution_show, text = query.get('1.0', END)).place(x=20, y=40)

			
			tree = ttk.Treeview(execution_show)
			tree['show'] = 'headings'

			tree["columns"]=selected_column_names
			for i in selected_column_names:
				tree.column(i, width=100)
				tree.heading(i, text=i)
			for i in range(n_row):
				tree.insert("", "end", text=str(i+1), values=temp[i])
			tree.place(x=20, y=60)

			Label(execution_show, text="Size: " + str(n_row) + " rows, " + str(n_col) + " columns.", font='Helvetica 12').place(x=20, y=260)
			

			def export_to_csv():
				save_path = tkFileDialog.asksaveasfilename(title="Where to export?", defaultextension="*.csv")
		
		
				csv_content=[",".join(selected_column_names)]
				for i in range(n_row):
					for j in range(n_col):
						temp[i]=list(temp[i])
						temp[i][j] = str(temp[i][j])
					csv_content.append(",".join(temp[i]))
		
				to_write = "\n".join(csv_content)
				
				f=open(save_path, "w")
				f.write(to_write)
				f.close()

			Button(execution_show, text="Export to .CSV", command=export_to_csv).place(x=20, y=280)

		view.destroy()
		view_interface()


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
root.geometry('500x300')

db_path_label = Label(root, text = "Open existing database (.db):", font='Helvetica 15 bold')
db_path_label.place(x = 100, y = 45)

name=StringVar()
db_path_entry = Entry(root, textvariable = name)
db_path_entry.place(x = 100, y = 70)

def get_db_path():
	global db_type
	db_type = "existing"
	types = [('.db files', '*.db')]
	temp_path = tkFileDialog.askopenfilename(title = 'Existing .db file', filetypes = types)
	db_path_entry.delete(0, END)
	db_path_entry.insert(0, temp_path)
Button(root, text = 'Browse...', command = get_db_path).place(x = 300, y = 70)

Button(root, text = 'open', command = view_interface).place(x = 100, y=100 )



# build a new .db file

new_db_label = Label(root, text = "Build a new database:", font='Helvetica 15 bold')
new_db_label.place(x = 100, y = 155)

name=StringVar()
new_db_entry = Entry(root, textvariable = name)
new_db_entry.place(x = 100, y = 180)

def get_new_db_name():
	global db_type
	db_type = "new"
	temp_path = tkFileDialog.asksaveasfilename(title = 'Build new database')
	new_db_entry.delete(0, END)
	new_db_entry.insert(0, temp_path+'.db')
Button(root, text = 'Browse...', command = get_new_db_name).place(x = 300, y = 180)

def build():
	conn_temp = sqlite3.connect(new_db_entry.get())
	conn_temp.execute("create table test(id int, name text);")
	conn_temp.execute("insert into test values (1, 'test');")
	conn_temp.commit()
	conn_temp.close()
	view_interface()
Button(root, text = 'Build', command = build).place(x = 100, y=210)


mainloop()