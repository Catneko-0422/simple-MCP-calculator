import json
import re
import ollama

# 定義可執行的函數
def multiply(a, b):
    return a * b

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def division(a, b):
    return a / b if b != 0 else "錯誤: 除數不能為零"

def print_message(message):
    print(message)

# 可用的函數對應表
FUNCTIONS = {
    "multiply": multiply,
    "add": add,
    "sub": sub,
    "division": division,
    "print_message": print_message
}

# 可用的函數描述，提供給 AI 參考
available_functions = [
    {"name": "multiply", "description": "計算兩數相乘", "parameters": {"a": "int", "b": "int"}},
    {"name": "division", "description": "計算兩數相除", "parameters": {"a": "int", "b": "int"}},
    {"name": "add", "description": "計算兩數相加", "parameters": {"a": "int", "b": "int"}},
    {"name": "sub", "description": "計算兩數相減", "parameters": {"a": "int", "b": "int"}},
    {"name": "print_message", "description": "回應user印出訊息", "parameters": {"message": "string"}},
]

user_input = input('請輸入訊息: ')

# 發送請求給 Ollama
response = ollama.chat(
    model='gemma3:4b',
    messages=[
        {
            'role': 'system',
            'content': f"你可以調用以下函式: {json.dumps(available_functions)}。請確保你的回應是純 JSON，"
                       "且不包含多餘的文字。例如：{\"function_name\": \"multiply\", \"parameters\": {\"a\": 4, \"b\": 7}} 當用戶回應非計算問題時請用print_message函式回應當用戶的計算問題需要多函數的調用時可以將parameters寫成調用函數。例如要計算1+2/3：{\"function_name\": \"add\", \"parameters\": {\"a\": 1, \"b\":  {\"function_name\": \"division\", \"parameters\": {\"a\": 2, \"b\": 3}}}} 此用法可以無限套用 請確保每一個運算元都有使用到。"
        },
        {'role': 'user', 'content': user_input}
    ]
)

# 取得回應內容
content = response['message']['content']
print("原始回應:", content)

# 移除可能的 ```json ... ``` 包裹
cleaned_content = re.sub(r"^```json\s*|\s*```$", "", content, flags=re.DOTALL).strip()

def evaluate_value(v):  
    if isinstance(v, dict) and 'function_name' in v:  
        return evaluate_function_call(v)  
    else:  
        return v  

def evaluate_function_call(data):  
    function_name = data['function_name']  
    params = {}  
    for k, v in data.get('parameters', {}).items():  
        params[k] = evaluate_value(v)  
    return FUNCTIONS[function_name](**params)  

# 在主逻辑中：  
try:  
    data = json.loads(cleaned_content)  
    result = evaluate_function_call(data)  
    print(f"计算结果: {result}")  
except json.JSONDecodeError as e:  
    print("JSON解析失败:", e)  
    print("清理后的内容:", cleaned_content)  
