import pyodbc
import pandas as pd

# 設定 MSSQL 連線參數
server = 'your_server_name'  # 替換為你的伺服器名稱，例如 'localhost' 或 'SERVER\INSTANCE'
database = 'your_database_name'  # 替換為你的資料庫名稱
username = 'your_username'  # 替換為你的使用者名稱（如果使用 SQL Server 驗證）
password = 'your_password'  # 替換為你的密碼（如果使用 SQL Server 驗證）

# 使用 Windows 驗證（如果適用）
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    # 建立連線
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # 查詢 1：執行 sp_tables 取得表格清單
    query1 = "EXEC sp_tables @table_type = '''TABLE''';"
    df_tables = pd.read_sql(query1, conn)
    print("=== 資料庫中的表格清單 ===")
    print(df_tables)
    print("\n")

    # 查詢 2：執行 sp_help 取得指定表格的結構（以 'TableName' 為例）
    table_name = 'TableName'  # 替換為實際的表格名稱
    query2 = f"EXEC sp_help '{table_name}';"
    
    # sp_help 會返回多個結果集，因此需要逐一處理
    cursor.execute(query2)
    
    # 遍歷所有結果集
    result_sets = []
    while True:
        try:
            # 獲取結果集的欄位名稱
            columns = [column[0] for column in cursor.description] if cursor.description else []
            # 獲取結果集的資料
            rows = cursor.fetchall()
            if rows:
                # 將結果集轉為 DataFrame
                df = pd.DataFrame.from_records(rows, columns=columns)
                result_sets.append(df)
            # 檢查是否有下一個結果集
            if not cursor.nextset():
                break
        except pyodbc.ProgrammingError:
            break

    # 打印 sp_help 的結果集（通常第一個結果集是表格資訊，第二個是欄位資訊）
    print(f"=== {table_name} 的結構資訊 ===")
    for i, df in enumerate(result_sets):
        print(f"結果集 {i + 1}:")
        print(df)
        print("\n")

except Exception as e:
    print(f"發生錯誤：{e}")

finally:
    # 關閉連線
    cursor.close()
    conn.close()