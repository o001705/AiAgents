from DBConnection import DBAction

db_action = DBAction()
db_action.create_tables()
for i in range(10):
    db_action.store_new_transaction("user_2")
db_action.close_connection()
