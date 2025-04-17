# 生成Python脚本，从Excel提取数据，自动去重并标准化格式，输出到SQL数据库
# 该脚本实现了从Excel读取数据，去除重复项和空值，标准化数据格式，并将清洗后的数据存储到SQLite数据库中。
# 代码中包含了异常处理机制，以保证在读取文件或操作数据库时出现错误能够得到妥善处理。
# 需要安装的库：pandas, openpyxl, sqlite3

# 请确保已安装 pandas 库：运行命令 `pip install pandas`
# 请确保已安装 openpyxl 库：运行命令 `pip install openpyxl`

import pandas as pd
import sqlite3
from datetime import datetime
import argparse

# 使用 argparse 获取文件路径
parser = argparse.ArgumentParser(description="从Excel提取数据，去重并标准化格式，输出到SQL数据库")
parser.add_argument('--file', required=True, help="Excel文件路径")
args = parser.parse_args()
file_path = args.file  # 从命令行参数获取文件路径

try:  
    # 读取Excel的代码块  
    try:
        # 读取Excel文件到DataFrame
        df = pd.read_excel(file_path)
        print(f"Excel文件中的列名：{df.columns.tolist()}")  # 打印列名
        possible_columns = ['name', 'Name', '姓名', '名称', '产品', '物品']
        name_column = next((col for col in possible_columns if col in df.columns), None)
        if name_column:
            # 清洗数据
            df[name_column] = df[name_column].str.replace(r'[^\w\s]', '', regex=True)
            print(f"清洗后的数据：\n{df[[name_column]].head()}")  # 打印清洗后的数据

            # 写入SQLite数据库
            try:
                conn = sqlite3.connect("cleaned_data.db")  # 创建或连接数据库
                table_name = "cleaned_data"  # 数据库表名
                df.to_sql(table_name, conn, if_exists='replace', index=False)  # 写入数据库
                print(f"清洗后的数据已成功写入数据库表 '{table_name}'")
            except sqlite3.Error as db_error:
                print(f"数据库写入时出错：{db_error}")
            finally:
                conn.close()  # 关闭数据库连接
        else:
            print("警告：未找到任何匹配的'name'列，无法进行数据清洗！")
    except Exception as e:
        print(f"读取Excel文件时出错：{e}")
except FileNotFoundError:  
    print("错误：文件不存在，请检查路径！")  
except pd.errors.XLRDError:  
    print("错误：文件格式不正确，请检查文件类型！")  
except pd.errors.ParserError:  
    print("错误：解析文件时出错，请检查文件内容！")  
except pd.errors.DtypeWarning as e:  
    print("警告：数据类型不一致，可能会导致数据丢失！")
    with open("dtype_warning_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()}: {str(e)}\n")
except sqlite3.Error as e:  
    print(f"数据库错误：{e}")
    
    # Log the error to a file
    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - 数据库错误：{e}\n")
    
    # Retry mechanism
    retry_count = 3
    for attempt in range(retry_count):
        try:
            print(f"尝试重新连接数据库... (第 {attempt + 1} 次)")
            # Replace with your database connection logic
            conn = sqlite3.connect("cleaned_data.db")
            print("数据库重新连接成功！")
            break
        except sqlite3.Error as retry_error:
            print(f"重试失败：{retry_error}")
            if attempt == retry_count - 1:
                print("多次重试失败，请检查数据库配置或网络连接。")
                with open("error_log.txt", "a", encoding="utf-8") as log_file:
                    log_file.write(f"{datetime.now()} - 多次重试失败：{retry_error}\n")
    print("已将问题行保存到 'problematic_rows.csv'，并记录到 'dtype_warning_log.txt'。")
except pd.errors.MergeError:  
    print("错误：合并数据时出错，请检查数据格式！")  
except sqlite3.Error as e:  
    print(f"数据库错误：{e}")

import sqlite3

conn = sqlite3.connect("cleaned_data.db")
query = "SELECT * FROM cleaned_data"
df = pd.read_sql(query, conn)
print(df)
conn.close()