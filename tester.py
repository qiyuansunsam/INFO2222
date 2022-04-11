import sql 
database_args = "samnchad.db" # Currently runs in RAM, might want to change this to a file if you use it
sql_db = sql.SQLDatabase(database_args)
sql_db.database_setup("admin")
sql_db.add_user("jeff","dunham",0)
sql_db.add_user("Alice","aliceword",0)
sql_db.add_user("Bob","bobword",0)
sql_db.add_user("")