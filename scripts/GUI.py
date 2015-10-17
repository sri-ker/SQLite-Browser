from Tkinter import *
import ttk
import tkFileDialog

import sqlite3

app_name = "SQLite View"
version_num = "0.1"

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


#######################################
############# View interface #############
#######################################


def view_interface():
	view = Tk()
	view.title("View Table" + " " + variable_table_choosing.get())
	tree = ttk.Treeview(view)

	temp_result = con.execute("select * from "+variable_table_choosing.get())
	temp_column_name = con.execute("pragma table_info(" + variable_table_choosing.get() + ");").fetchall()
	
	column_name_and_type=[]
	for i in range(len(temp_column_name)):
		column_name_and_type.append(" (".join(temp_column_name[i][1:3]) + ")")

	print column_name_and_type


	query_result = temp_result.fetchall()
	# if(view_all_flag != 1):
	# 	query_result=query_result[0:30]
	#query_result=query_result[0:30]

	n_row = len(query_result)
	n_col = len(query_result[0])

	for i in range(n_row):
		for j in range(n_col):
			print query_result[i][j]
		print "\n"

	tree["columns"]=column_name_and_type
	for i in column_name_and_type:
		tree.column(i, width=100)
		tree.heading(i, text=i)

	if(n_row>=30):
		for i in range(30):
			tree.insert("", "end", text=str(i+1), values=query_result[i])
	else:
		for i in range(n_row):
			tree.insert("", "end", text=str(i+1), values=query_result[i])

	def view_all():
		view = Tk()
		view.title("View all")
		tree = ttk.Treeview(view)

		tree["columns"]=column_name_and_type
		for i in column_name_and_type:
			tree.column(i, width=100)
			tree.heading(i, text=i)
		for i in range(n_row):
			tree.insert("", "end", text=str(i+1), values=query_result[i])
		tree.pack()
	Button(view, text="View all", command=view_all).pack()

	def export_to_csv():
		save_path = tkFileDialog.asksaveasfilename(title="Where to export?", defaultextension="*.csv")
		
		
		csv_content=[",".join(column_name_and_type)]
		for i in range(n_row):
			for j in range(n_col):
				query_result[i]=list(query_result[i])
				query_result[i][j] = str(query_result[i][j])
			csv_content.append(",".join(query_result[i]))
		
		to_write = "\n".join(csv_content)

		f=open(save_path, "w")
		f.write(to_write)
		f.close()

	Button(view, text="Export to .CSV", command=export_to_csv).pack()

	tree.pack()
 	# tree view:
 	# http://www.tkdocs.com/tutorial/tree.html

#######################################
############# choosing interface #############
#######################################

def main_interface():
	main = Tk()
	main.title(app_name + " " +version_num)
	main.geometry('600x300')

	print db_type
	if(db_type == "existing"):
		db_path = db_path_entry.get()
	else:
		db_path = new_db_entry.get()

	print db_path

	global con
	con = sqlite3.connect(db_path)
	table_list_cursor = con.execute("select name from sqlite_master where type = 'table';")
	table_list=[]
	for row in table_list_cursor:
		table_list.append(row[0])

	print table_list

	if len(table_list)==0:
		table_list.append("!EMPTY!")

	Label(main, text="Table List:").place(x=50, y=30)

	# http://knowpapa.com/ttk-treeview/
	tree = ttk.Treeview(main)
	tree["columns"]=("one")
	tree.column("one", width=100 )
	tree.heading("one", text="Table")

	for i in range(len(table_list)):
		tree.insert("" , "end",  text=str(i+1), values=(table_list[i]))
 
	tree.place(x=50, y=50)

	Label(main, text="Choose table to manipulate:").place(x=380, y=100)

	global variable_table_choosing
	variable_table_choosing = StringVar(main)
	variable_table_choosing.set(table_list[0]) # default value

	table_choosing = apply(OptionMenu, (main, variable_table_choosing) + tuple(table_list))
	table_choosing.place(x=380, y=120)


	Button(main, text="Ok", comman=view_interface).place(x=385, y=150)





#######################################
############# Begin GUI #############
#######################################

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


Button(root, text = 'open', command = main_interface).place(x = 50, y=100 )



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