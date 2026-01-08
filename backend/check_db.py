import sqlite3

conn = sqlite3.connect('instance/local.db')
cursor = conn.cursor()

# Check all users
cursor.execute("SELECT id, email, role, isadmin FROM users")
users = cursor.fetchall()
print(f"Total users in database: {len(users)}")
for user in users:
    print(f"  {user[0]}: {user[1]} - role={user[2]}, isadmin={user[3]}")

# Check if there are any institutes
cursor.execute("SELECT DISTINCT SUBSTR(email, INSTR(email, '@') + 1) as domain FROM users WHERE email LIKE '%@%'")
domains = cursor.fetchall()
print(f"\nDomains found: {len(domains)}")
for domain in domains:
    print(f"  {domain[0]}")

conn.close()
