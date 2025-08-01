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

def ShiZer(decimal_num):
    """
    功能: 将十进制数转换为二进制字符串
    示例:
        10 -> '1010'
    """
    return bin(int(decimal_num))[2:]
    
def ShiZba(decimal_num):
    """
    功能: 将十进制数转换为八进制字符串
    示例:
        10 -> '12'
    """
    return oct(int(decimal_num))[2:]
    
def ShiZsl(decimal_num):
    """
    功能: 将十进制数转换为十六进制字符串
    示例:
        10 -> 'a'
        255 -> 'ff'
    """
    return hex(int(decimal_num))[2:]

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
        
def CHch(num):
    """
    将数字转换为中文金额大写（纯函数实现）
    
    参数:
        num (float/int): 金额数字，支持两位小数（如 1234.56）
    
    返回:
        str: 中文金额大写字符串
    
    示例:
        >>> number_to_chinese_currency(1234.56)
        '壹仟贰佰叁拾肆元伍角陆分'
    """
    if not isinstance(num, (int, float)):
        raise ValueError("输入必须是数字")
    
    # 中文数字映射
    digits = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
    units = ["", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿", "拾", "佰", "仟"]

    # 分离整数和小数部分
    integer_part = int(abs(num))
    decimal_part = round(abs(num) - integer_part, 2)
    
    # 处理负数
    sign = "负" if num < 0 else ""
    
    # 转换整数部分
    def convert_integer(n):
        if n == 0:
            return digits[0]
        res = []
        zero_flag = False
        for i, c in enumerate(str(n)[::-1]):
            c = int(c)
            if c == 0:
                if not zero_flag and i % 4 != 0:
                    res.append(digits[0])
                    zero_flag = True
            else:
                res.append(units[i] + digits[c])
                zero_flag = False
        return "".join(reversed(res))
    
    # 转换小数部分
    def convert_decimal(d):
        jiao = int(d * 10) % 10
        fen = int(d * 100) % 10
        parts = []
        if jiao > 0:
            parts.append(digits[jiao] + "角")
        if fen > 0:
            parts.append(digits[fen] + "分")
        return "".join(parts)
    
    # 组合结果
    result = sign
    if integer_part > 0:
        result += convert_integer(integer_part) + "元"
    if decimal_part > 0:
        result += convert_decimal(decimal_part)
    else:
        result += "整"
    
    return result        
