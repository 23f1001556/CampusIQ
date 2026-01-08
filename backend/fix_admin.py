import sqlite3

conn = sqlite3.connect('instance/local.db')
cursor = conn.cursor()

# Update the admin user
cursor.execute("UPDATE users SET role=?, isadmin=? WHERE email=?", ('admin', 1, 'sidhantsksk@gmail.com'))
conn.commit()

# Verify
cursor.execute("SELECT id, email, role, isadmin FROM users WHERE email=?", ('sidhantsksk@gmail.com',))
result = cursor.fetchone()
print(f"Updated user: {result}")

conn.close()
