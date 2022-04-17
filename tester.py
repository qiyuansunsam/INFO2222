import sql
sql_db = sql.SQLDatabase("samnchad.db")
sql_db.get_chatlog(1,2)
sql_db.add_chatlog(1,"U2FsdGVkX19iQXNdL7RSfUeYXPkwRkZ192yP7M+so50=")
sql_db.get_chatlog(1,2)