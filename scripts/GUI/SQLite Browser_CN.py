#-*-coding:utf-8-*-
from Tkinter import *
import ttk
import tkFileDialog   #http://tkinter.unpythonic.net/wiki/tkFileDialog
import os
import re  # for regular expression filter module

import sqlite3


app_name = "SQLite 浏览器"
version_num = "0.15"

############################################################################################################################################################
############################################################################################################################################################


#######################################
#######################################
###       View interface            ###
#######################################
#######################################

# we define here SQL_command here for a feature later in "SQL Execution" and "submit" module
SQL_command="" # this is a meaningful & useful definiton

def view_interface():

	global view
	view = Tk()
	view.title("查看表格")
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
		table_list.append("空")


	# a modeule to deal with the situation in which the .db file is empty.
	# will give a reminding and close the window.
	if table_list[0]=='空':
		empty_warning=Tk()
		empty_warning.title("数据库文件为空")
		empty_warning.geometry('250x100')

		view.destroy()

		w = Message(empty_warning, text="该数据库文件为空.", width=300, font='Helvetica 15')
		w.place(x=35, y=20)

		def close():
			empty_warning.destroy()
		Button(empty_warning, text="确认", command=close).place(x=100, y=60)



	variable_table_choosing = StringVar(view)
	variable_table_choosing.set(table_list[0]) # default value

	Label(view, text="表格:", font='Helvetica 14 bold').place(x=30,y=30)
	table_choosing = apply(OptionMenu, (view, variable_table_choosing) + tuple(table_list))
	table_choosing.configure(width=12) # set the width of the OptionMenu widget
	table_choosing.place(x=30, y=50)

	
	def choose_table():
		view_work()

	Button(view, text="选择", comman=choose_table).place(x=30, y=75)


	# this two lines are added to help show the current table in viewer.
	# the specific table name will be assigned within function view_work below
	current_table_to_show = Label(view, text=" ", font='Helvetica 15 bold')
	current_table_to_show.place(x=200, y=20)

	# these two lines are added to hlep show the table size in viewer
	# the specific size will be assined within  the function view_work below
	table_size=Label(view, text=" ", font='Helvetica 12')
	table_size.place(x=200, y=260)
	
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
			tree.column(i, width=100)
			tree.heading(i, text=i)

		if(n_row>=30):
			for i in range(30):
				tree.insert("", "end", text=str(i+1), values=query_result[i])
		else:
			for i in range(n_row):
				tree.insert("", "end", text=str(i+1), values=query_result[i])

		
		current_table_to_show.configure(text="当前表格: "+str(variable_table_choosing.get()))
		table_size.configure(text = "维度: " + str(n_row) + " 行, " + str(n_col) + " 列.")

	view_work()



	Label(view, text="操作:", font='Helvetica 14 bold').place(x=30,y=130)

	#----------------------------------------------------------------------------------------------------------------------------------------
	
	#######################################
	# View full table
	#######################################
	def view_all():
		view = Tk()
		view.title("查看完整表格")
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

		Label(view, text="维度: " + str(n_row) + " 行, " + str(n_col) + " 列.", font='Helvetica 12').place(x=20, y=230)

		def close():
			view.destroy()
		Button(view, text="关闭", command = close).place(x=20, y=250)

	Button(view, text="查看完整表格", command=view_all).place(x=30, y=150)

	#----------------------------------------------------------------------------------------------------------------------------------------

	#######################################
	# "export to CSV" module
	#######################################

	def export_to_csv():
		save_path = tkFileDialog.asksaveasfilename(title="导出至?", defaultextension="*.csv")
		
		
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

	Button(view, text="导出至.CSV文件", command=export_to_csv).place(x=30, y=180)

	#----------------------------------------------------------------------------------------------------------------------------------------

	#######################################
	# "Import from CSV" module
	#######################################

	def import_from_csv():
		global import_interface
		import_interface = Tk()
		import_interface.geometry('330x250')
		import_interface.title("从.CSV文件导入表格")

		# entry for the path and name of the CSV file
		Label(import_interface, text="CSV文件路径:").place(x=30, y=30)
		csv_name=StringVar()
		csv_entry = Entry(import_interface, textvariable = csv_name)
		csv_entry.place(x=30, y=50)


		def browse_csv_path():
			types = [('.CSV files', '*.csv')]
			csv_path = tkFileDialog.askopenfilename(title = '从CSV文件导入表格', filetypes = types)
			csv_entry.delete(0, END)
			csv_entry.insert(0, csv_path)
		Button(import_interface, text="浏览", command=browse_csv_path).place(x=230, y=50)


		# specify the name of the new table (which will be built from the CSV file)
		Label(import_interface, text="导入至表格:").place(x=30, y=100)
		table_name=StringVar()
		table_name_entry = Entry(import_interface, textvariable = table_name)
		table_name_entry.place(x=30, y=120)


		def import_act():
			
			f=open(csv_entry.get(), "r")
			content = f.readlines() # if the csv file contains n rows, then "content" should be a list with length n

			# this function split each row from CSV file into format ready for SQL inserting
			def split_row(x_row):
				splitted_row = x_row.split(',')
				splitted_row[len(splitted_row)-1] = splitted_row[len(splitted_row)-1].split('\n')[0]
				return splitted_row
			csv_column_name = split_row(content[0])


			# check if the new table name is empty
			if table_name_entry.get()=="":
				temp = Tk()
				temp.title("表格名为空")
				temp.geometry('250x100')
				Message(temp, text="表格名为空", width=300, font='Helvetica 14').place(x=35, y=20)

				def close():
					temp.destroy()
				Button(temp, text="确认", command=close).place(x=100, y=60)
				return 0

			# check if the new table name already exist
			if table_name_entry.get() in table_list:
				temp = Tk()
				temp.title("该表格名已存在")
				temp.geometry('250x100')
				Message(temp, text="该表格名已存在", width=300, font='Helvetica 14').place(x=35, y=20)

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
			importing_finished_interface.title("导入完成")
			importing_finished_interface.geometry('250x100')
			Message(importing_finished_interface, text="导入完成", width=300, font='Helvetica 14').place(x=35, y=20)

			import_interface.destroy()

			def close():
				importing_finished_interface.destroy()
			Button(importing_finished_interface, text="确认", command=close).place(x=100, y=60)

			view.destroy()
			view_interface()

		Button(import_interface, text="导入", command=import_act).place(x=50, y=180)

		def close_outer():
			import_interface.destroy()
		Button(import_interface, text="关闭", command=close_outer).place(x=140, y=180)


	Button(view, text="从CSV文件导入", command=import_from_csv).place(x=30, y=210)




	tree.place(x=200, y=50)
 	# tree view:
 	# http://www.tkdocs.com/tutorial/tree.html

 	#----------------------------------------------------------------------------------------------------------------------------------------

 	#######################################
 	# "SQL command execution" module
 	#######################################

 	# SQL Execution Module
 	Label(view, text="SQL查询:", font='Helvetica 15 bold').place(x = 200, y= 300)
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
			execution_show.title('执行结果')
			execution_show.geometry('1000x350')
			Label(execution_show, text="已执行的SQL语句:", font="Helvetica 14 bold").place(x=20, y=20)
			Label(execution_show, text = query.get('1.0', END),fg="blue").place(x=20, y=40)

			
			tree = ttk.Treeview(execution_show)
			tree['show'] = 'headings'

			tree["columns"]=selected_column_names
			for i in selected_column_names:
				tree.column(i, width=100)
				tree.heading(i, text=i)
			for i in range(n_row):
				tree.insert("", "end", text=str(i+1), values=temp[i])
			tree.place(x=20, y=80)

			Label(execution_show, text="维度: " + str(n_row) + " 行, " + str(n_col) + " 列.", font='Helvetica 12').place(x=20, y=280)
			

			def export_to_csv():
				save_path = tkFileDialog.asksaveasfilename(title="导出至？", defaultextension="*.csv")
		
		
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

			Button(execution_show, text="导出为CSV文件", command=export_to_csv).place(x=18, y=310)

		view.destroy()
		view_interface()


	Button(view, text="提交", comman=submit).place(x=510, y=350)


	#----------------------------------------------------------------------------------------------------------------------------------------

	#######################################
	# STATUS module
	#######################################

	Label(view, text="状态:", font='Helvetica 15 bold').place(x = 200, y= 430)
	Label(view, text="数据库文件路径: "+db_path).place(x = 200, y = 450)
	# BUG:  for now, if I create a table with SQL execution, the number here will not change correspondingly.
	status_num_of_table = Label(view, text="表格数量: " + str(len(table_list)))
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

	Label(view, text="数据库文件大小: "+str(db_file_size)+" "+db_file_size_unit).place(x = 200, y = 490)

	#----------------------------------------------------------------------------------------------------------------------------------------

	#######################################
	# "Regular Expression Filter" Module
	#######################################

	# this is a new feature with which user can filter the records in database with Regular Expression
	def RE():
		RE_filter = Tk()
		RE_filter.title("以正则表达式进行筛选")
		RE_filter.geometry('350x230')

		variable_table_choosing = StringVar(RE_filter)
		variable_table_choosing.set(table_list[0]) # default value
		Label(RE_filter, text="选择表格以及列:", font='Helvetica 14 bold').place(x=30, y= 20)
		table_choosing = apply(OptionMenu, (RE_filter, variable_table_choosing) + tuple(table_list))
		table_choosing.configure(width=15) # set the width of the OptionMenu widget
		table_choosing.place(x=30, y=40)

		def choose_table_RE():
			column_select_RE['menu'].delete(0, 'end')
			table_choosed=variable_table_choosing.get()
			temp = con.execute("pragma table_info(" + table_choosed + ");").fetchall()

			temp_column_name=[]
			for i in range(len(temp)):
				temp_column_name.append(temp[i][1])

			# add the column names of the selected table into the optionMedu widget
			#http://www.prasannatech.net/2009/06/tkinter-optionmenu-changing-choices.html
			column_name_RE.set(temp_column_name[0])
			for i in temp_column_name:
				column_select_RE["menu"].add_command(label=i, command=lambda temp = i: column_select_RE.setvar(column_select_RE.cget("textvariable"), value = temp))

		Button(RE_filter, text="选择", command=choose_table_RE).place(x=180, y=40)

		column_name_RE = StringVar(RE_filter)
		column_name_RE.set(" ")
		column_select_RE = OptionMenu(RE_filter, column_name_RE, " ")
		column_select_RE.configure(width=15)
		column_select_RE.place(x=30, y=80)


		Label(RE_filter, text="Pattern:", font='Helvetica 14 bold').place(x=30, y=120)
		RE_query=Text(RE_filter, width=40, height=1, background="lightblue")
		RE_query.place(x=30, y=140)

		def RE_submit():
			column_to_run_RE = column_name_RE.get()
			RE_pattern = RE_query.get('1.0', END)
			RE_pattern = RE_pattern[0:len(RE_pattern)-1]  # the get method in the last line will add a "\n" at the end of the text automatically. So we use this line to remove the "\n"
			

			## Execute the Regular Expression and return the rows with this pattern
			def RE_execution(table, column, pattern):
				
				# obtain all the data in the column selected
				RE_command = 'select '+column+' from ' + table
				data_to_run_RE = con.execute(RE_command)
				data_to_run_RE = data_to_run_RE.fetchall()

				for i in range(len(data_to_run_RE)):
					data_to_run_RE[i] = data_to_run_RE[i][0]


				# Run Regular Expression and generate a vector which will label if each record meet the requirement of RE
				match_result_index=[]
				for i in range(len(data_to_run_RE)):
					temp_match = re.search(str(pattern), str(data_to_run_RE[i]))
					if temp_match:
						match_result_index.append(1)
					else:
						match_result_index.append(0)

				return match_result_index

			RE_match_result = RE_execution(variable_table_choosing.get(), column_to_run_RE, RE_pattern)
			

			RE_result_view = Tk()
			RE_result_view.title("正则表达式筛选结果")
			RE_result_view.geometry('1000x300')
			tree = ttk.Treeview(RE_result_view)
			tree['show'] = 'headings'

			table_choosed=variable_table_choosing.get()
			temp_result = con.execute("select * from "+table_choosed)
			temp_column_name = con.execute("pragma table_info(" + table_choosed + ");").fetchall()
			
			column_name=[]
			for i in range(len(temp_column_name)):
				column_name.append(temp_column_name[i][1])

			query_result = temp_result.fetchall()
			n_row = len(query_result)

			# Based on the vector obtained above, select the correspding rows and return them
			exact_result=[]
			for i in range(n_row):
				if RE_match_result[i]==1:
					exact_result.append(query_result[i])
			n_row = len(exact_result)
			n_col = len(exact_result[0])

			tree["columns"]=column_name
			for i in column_name:
				tree.column(i, width=100)
				tree.heading(i, text=i)
			for i in range(n_row):
				tree.insert("", "end", text=str(i+1), values=exact_result[i])
			tree.grid(row=0, column=0)
			Label(RE_result_view, text=str(n_row) + " 行被提取.", font='Helvetica 12').grid(row=1, column=0)

			def export_to_csv():
				save_path = tkFileDialog.asksaveasfilename(title="导出至？", defaultextension="*.csv")
		
		
				csv_content=[",".join(column_name)]
				for i in range(n_row):
					for j in range(n_col):
						exact_result[i]=list(exact_result[i])
						exact_result[i][j] = str(exact_result[i][j])
					csv_content.append(",".join(exact_result[i]))
		
				to_write = "\n".join(csv_content)
				
				f=open(save_path, "w")
				f.write(to_write)
				f.close()

			Button(RE_result_view, text="导出为CSV文件", command=export_to_csv).grid(row=2, column=0)
			def close():
				RE_result_view.destroy()
			Button(RE_result_view, text="关闭", command=close).grid(row=3, column=0)

		Button(RE_filter, text="运行", command=RE_submit).place(x=30, y=170)

		def close():
			RE_filter.destroy()
		Button(RE_filter, text="关闭", command=close).place(x=100, y=170)



	Button(view, text="正则表达式", command=RE).place(x=30, y=240)

	def close():
		view.destroy()
	Button(view, text="关闭", height=2, command=close, font='Helvetica 15').place(x=30, y=400)

############################################################################################################################################################
############################################################################################################################################################


#######################################
#######################################
###             Begin GUI           ###
#######################################
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
root.geometry('540x300')


#######################################
# Open Existing .DB file
#######################################

db_path_label = Label(root, text = "打开已有的数据库文件 (.db):", font='Helvetica 15 bold')
db_path_label.place(x = 100, y = 45)

name=StringVar()
db_path_entry = Entry(root, textvariable = name, width=25)
db_path_entry.place(x = 100, y = 70)

def get_db_path():
	global db_type
	db_type = "existing"
	types = [('.db files', '*.db')]
	temp_path = tkFileDialog.askopenfilename(title = '已有的 .db 文件', filetypes = types)
	db_path_entry.delete(0, END)
	db_path_entry.insert(0, temp_path)
Button(root, text = '浏览...', command = get_db_path).place(x = 350, y = 70)

def open_db():
	view_interface()

Button(root, text = '打开', command = open_db).place(x = 100, y=100 )

#----------------------------------------------------------------------------------------------------------------------------------------

#######################################
# Build a new .DB file
#######################################

new_db_label = Label(root, text = "新建数据库文件:", font='Helvetica 15 bold')
new_db_label.place(x = 100, y = 155)

name=StringVar()
new_db_entry = Entry(root, textvariable = name, width=25)
new_db_entry.place(x = 100, y = 180)

def get_new_db_name():
	global db_type
	db_type = "new"
	temp_path = tkFileDialog.asksaveasfilename(title = '新建数据库')
	new_db_entry.delete(0, END)
	new_db_entry.insert(0, temp_path+'.db')
Button(root, text = '浏览...', command = get_new_db_name).place(x = 350, y = 180)

def build():
	conn_temp = sqlite3.connect(new_db_entry.get())
	conn_temp.execute("create table test(id int, name text);")
	conn_temp.execute("insert into test values (1, 'test');")
	conn_temp.commit()
	conn_temp.close()
	view_interface()
Button(root, text = '新建', command = build).place(x = 100, y=210)

def close():
	root.destroy()
Button(root, text = '关闭', command = close).place(x = 450, y=260)

mainloop()