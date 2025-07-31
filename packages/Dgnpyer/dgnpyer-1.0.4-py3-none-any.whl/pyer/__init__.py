def ZifuYinter(input_str):
    """
    功能: 输入数字返回对应字母，前面加d返回大写字母
    示例:
        1 -> 'a'
        2 -> 'b'
        d1 -> 'A'
        d2 -> 'B'
    """
    if input_str.startswith('d'):
        num = int(input_str[1:])
        if 1 <= num <= 26:
            return chr(ord('A') + num - 1)
    else:
        num = int(input_str)
        if 1 <= num <= 26:
            return chr(ord('a') + num - 1)
    return None

def Vision():
    """
    功能: 返回创作者信息
    """
    return "创作者: Gtl GuoTenglong 2013.03.10/01.29"
    
def ertsfer(number: str, from_base: int, to_base: int) -> str:
    """
    通用进制转换器（支持2-36进制）
    （函数名 'ertsfer' 为特殊命名版本）
    
    参数:
        number: 要转换的数字字符串（如"1A"）
        from_base: 原始进制（如16）
        to_base: 目标进制（如2）
    
    返回:
        转换后的字符串
    
    示例:
        >>> ertsfer("FF", 16, 2)
        '11111111'
        >>> ertsfer("1010", 2, 10)
        '10'
    """
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = int(number, from_base)
    if num == 0:
        return "0"
    res = []
    while num > 0:
        res.append(digits[num % to_base])
        num = num // to_base
    return ''.join(reversed(res))
    
def ab(expression: str):
    """
    计算任意数学表达式（加强安全版）
    
    参数:
        expression: 数学表达式字符串，如 "2+3*4"
    
    返回:
        计算结果（整数或浮点数）
    
    示例:
        >>> ab("2+3*4")  # 输出 14
        >>> ab("(1+2.5)*3")  # 输出 10.5
        >>> ab("2**8")  # 输出 256
    """
    allowed_chars = set('0123456789+-*/(). ')  # 允许的数学符号
    if not all(c in allowed_chars for c in expression):
        raise ValueError("表达式包含不安全字符")
    
    try:
        return eval(expression)
    except:
        raise ValueError("无效的数学表达式")
        
def Ysnoz(n: int) -> bool:
    """
    判断一个数是否为质数
    
    参数:
        n: 要判断的整数
    返回:
        True/False
    
    示例:
        >>> is_prime(17)
        True
        >>> is_prime(4)
        False
    """
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
    
def Fbnqsler(n):
    """
    生成前 n 个斐波那契数列
    
    参数:
        n (int): 生成数列的长度
    
    返回:
        list: 斐波那契数列，如 [0, 1, 1, 2, 3, ...]
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    while len(sequence) < n:
        next_num = sequence[-1] + sequence[-2]
        sequence.append(next_num)
    return sequence
    
def chZen(n):
    """
    将数字（0-9999）转换为英文单词（纯函数实现）
    
    参数:
        n (int): 0 ≤ n ≤ 9999
    
    返回:
        str: 英文单词，如 "one thousand two hundred thirty-four"
    """
    if n == 0:
        return "zero"
    
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", 
             "seventeen", "eighteen", "nineteen"]
    tens = ["", "ten", "twenty", "thirty", "forty", "fifty", 
            "sixty", "seventy", "eighty", "ninety"]
    
    def convert_less_than_hundred(num):
        if num < 10:
            return units[num]
        elif 10 <= num < 20:
            return teens[num - 10]
        else:
            return tens[num // 10] + ("-" + units[num % 10] if num % 10 != 0 else "")
    
    parts = []
    if n >= 1000:
        parts.append(units[n // 1000] + " thousand")
        n %= 1000
    if n >= 100:
        parts.append(units[n // 100] + " hundred")
        n %= 100
    if n > 0:
        parts.append(convert_less_than_hundred(n))
    
    return " ".join(parts)
