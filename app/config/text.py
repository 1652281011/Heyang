# root_test.py
import pymysql

def test_root_connection():
    print("Testing Root Connection")
    print("=" * 30)
    
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="123456",  # 替换为实际root密码
            charset='utf8mb4'
        )
        print("SUCCESS: Root connection works!")
        
        # 查看用户列表
        with connection.cursor() as cursor:
            cursor.execute("SELECT user, host FROM mysql.user")
            users = cursor.fetchall()
            print("\nCurrent users:")
            for user, host in users:
                print(f"  {user}@{host}")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"FAILED: Root connection failed - {e}")
        return False

if __name__ == "__main__":
    test_root_connection()
    input("\nPress Enter to exit...")