import sqlite3
from datetime import datetime
import csv

def setup_database():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expense (
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
setup_database()    
    


#----------------------------------------------------------------------ADDING THE INCOME------------------------------------------------------------------------------------
def add_income():
    try:
        amount = float(input("Enter income amount: "))
        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return
        
        date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
        if date.strip() == "":
            date = datetime.today().strftime('%Y-%m-%d')                                    # strftime () converts a datetime object to a string in the specified format
        
        conn = sqlite3.connect("finance.db")                                                # Connect to the SQLite database , if file does not exist it will be created
        cursor = conn.cursor()                                                              # Create a cursor object to execute SQL queries
        cursor.execute("INSERT INTO income (amount, date) VALUES (?, ?)", (amount, date))
        conn.commit()                                                                       # It will save the changes in database otherwise data will be temporary
        conn.close()                                                                       
        print("✅ Income added successfully!\n")
        print("📈 Budget Advice:")
        budget_advice()        
        
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
   
#----------------------------------------------------------------------ADDING THE EXPENCE------------------------------------------------------------------------------------
        
def add_expense():
    try:
        amount = float(input("Enter expense amount: "))
        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return

        # 🔥 Fetch current balance
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM income")
        income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM expense")
        expense = cursor.fetchone()[0] or 0

        balance = income - expense

        # 🚨 Check before adding expense
        if amount > balance:
            print("❌ Insufficient balance! You cannot spend more than available.")
            print(f"💰 Available Balance: ₹{balance}")
            conn.close()
            return

        category = input("Enter category (e.g., food, travel, bills): ")
        if category.strip() == "":
            print("❌ Category cannot be empty.")
            conn.close()
            return

        category = category.capitalize()

        date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
        if date.strip() == "":
            date = datetime.today().strftime('%Y-%m-%d')

        cursor.execute(
            "INSERT INTO expense (amount, category, date) VALUES (?, ?, ?)",
            (amount, category, date)
        )

        conn.commit()
        conn.close()

        print("✅ Expense added successfully!\n")
        print("📈 Budget Advice:")
        budget_advice()

    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    
#----------------------------------------------------------------------SHOWING THE TOTAL BALANCE------------------------------------------------------------------------------

    
def show_balance():      
    conn = sqlite3.connect("finance.db")                                               
    cursor = conn.cursor()    
    
    #Total of Income
    cursor.execute("SELECT SUM(amount) FROM income")
    income_total=cursor.fetchone()[0]
    if income_total is None:
        income_total=0
    
    #Total of Expence
    cursor.execute("SELECT SUM(amount) FROM expense")
    expense_total=cursor.fetchone()[0]
    if expense_total is None:
        expense_total=0
        
    #Calculating the Total Balance 
    balance = income_total - expense_total
    
    print(f"\n💰 Total Income: ₹{income_total}")
    print(f"💸 Total Expenses: ₹{expense_total}")
    print(f"🧾 Balance: ₹{balance}\n")
    print("📈 Budget Advice:")
    budget_advice() 

    conn.close()  
    
    
#----------------------------------------------------------------------SHOWING THE TOTAL BALANCE------------------------------------------------------------------------------
     
def show_transactions():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    
    print("\n--- 💰 Income Transactions ---")
    cursor.execute("SELECT rowid,amount,date FROM income")
    income_rows=cursor.fetchall()
    if income_rows:
        for row in income_rows:
            print(f"ID: {row[0]} | Amount: ₹{row[1]} | Date: {row[2]}")
    else:
        print("No income transactions found.")        
            
    print("\n--- 💸 Expense Transactions ---")
    cursor.execute("SELECT rowid,amount,category,date FROM expense")
    expense_rows=cursor.fetchall()
    if expense_rows:
        for row in expense_rows:
            print(f"ID: {row[0]} | Amount: ₹{row[1]} | Category: {row[2]} | Date: {row[3]}")
        else:
            print("No expense records found.")
        conn.close()

#----------------------------------------------------------------------DELETE TRANACTION------------------------------------------------------------------------------
def delete_transactions():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()   
    trans_type = input("Delete from (income/expense)? ").strip().lower()
    if trans_type not in ("income", "expense"):
        print("❌ Invalid type.")
        return
    try:
        trans_id = int(input("Enter transaction ID to delete: "))
        cursor.execute(f"DELETE FROM {trans_type} WHERE rowid = ?", (trans_id,))
        conn.commit()    
    except ValueError:
        print("❌ Please enter a valid number.")
    conn.close()        
            
#----------------------------------------------------------------------DELETE THE DATA------------------------------------------------------------------------------            
def delete_all_data():
    confirmation = input("⚠️ Are you sure you want to delete ALL data? (yes/no): ").strip().lower()
    if confirmation == "yes":
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM income")
        cursor.execute("DELETE FROM expense")
        conn.commit()
        conn.close()
        print("🗑️ All data deleted successfully!\n")
    else:
        print("❎ Deletion cancelled.\n")
        
#----------------------------------------------------------------------SEQUENCING BY THE CATEGORY------------------------------------------------------------------------------
        
def expance_by_category():
    conn=sqlite3.connect("finance.db")
    cursor=conn.cursor()
    cursor.execute("SELECT category , SUM(amount) FROM expense GROUP BY category")
    rows=cursor.fetchall()
    print("\n📊 Expense by Category:")
    for row in rows:
        print(f"{row[0]}: ₹{row[1]}")
    conn.close()    

#----------------------------------------------------------------------SHOWING THE TOTAL BALANCE------------------------------------------------------------------------------

def export_to_csv():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    with open("income.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Date"])
        for row in cursor.execute("SELECT amount, date FROM income"):
            writer.writerow(row)

    with open("expense.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Category", "Date"])
        for row in cursor.execute("SELECT amount, category, date FROM expense"):
            writer.writerow(row)

    conn.close()
    print("📂 Data exported to 'income.csv' and 'expense.csv' successfully!\n")
    
    
def budget_advice():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM income")
    income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expense")
    expense = cursor.fetchone()[0] or 0

    conn.close()

    if income == 0:
        print("💡 You haven't added any income yet. Please log your earnings.")
    elif expense > income:
        print("⚠️ You're spending more than you earn. Consider reducing your expenses.")
    elif expense > 0.8 * income:
        print("🟡 You’ve spent over 80% of your income. Monitor your spending closely.")
    else:
        print("✅ You're doing well! Keep tracking to stay on budget.")
    

while True: 
    print('''PRESS ACCORDING WHAT YOU WANT TO DO :->
    1. Add Income
    2. Add Expense
    3. Show Balance
    4. Show Transactions
    5. Delete Transactions
    6. Category wise expance 
    7. Delete All Data
    8. Import In CSV
    9. Exit
    ''')
    try:
        choice = int(input("Enter the nummber of choice:"))
        if choice==1:
            add_income()
        elif choice ==2:
            add_expense()
        elif choice==3:
            show_balance()
        elif choice==4:
           show_transactions()
        elif choice==5:
            delete_transactions()   
        elif choice==6:
            expance_by_category()
        elif choice==7:
            delete_all_data()
        elif choice==8:
            export_to_csv()    
        elif choice==9:
            print("Goodbye👋")
            break    
        else:
            print("Invalid choice😥")
    except ValueError:
        print("❌ Please enter a valid number.")        