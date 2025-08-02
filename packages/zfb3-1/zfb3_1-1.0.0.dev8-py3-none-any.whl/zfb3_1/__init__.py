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

def X_x(s1, s2):
    """
    计算两个字符串的相似度（基于编辑距离算法）
    
    参数:
        s1 (str): 第一个字符串
        s2 (str): 第二个字符串
    
    返回:
        float: 相似度分数（0.0~1.0）
    
    示例:
        >>> string_similarity("kitten", "sitting")
        0.571
        >>> string_similarity("apple", "apple")
        1.0
    """
    # 处理空字符串情况
    if not s1 or not s2:
        return 0.0 if s1 != s2 else 1.0
    
    # 转换为小写统一比较
    s1, s2 = s1.lower(), s2.lower()
    
    # 初始化矩阵
    rows = len(s1) + 1
    cols = len(s2) + 1
    distance = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # 矩阵边界初始化
    for i in range(1, rows):
        distance[i][0] = i
    for j in range(1, cols):
        distance[0][j] = j
    
    # 动态规划计算编辑距离
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            distance[i][j] = min(
                distance[i-1][j] + 1,      # 删除
                distance[i][j-1] + 1,      # 插入
                distance[i-1][j-1] + cost  # 替换
            )
    
    # 计算相似度分数
    max_len = max(len(s1), len(s2))
    similarity = 1 - (distance[-1][-1] / max_len)
    
    return round(similarity, 3)
    
def text_txet(text: str, reverse_words: bool = False) -> str:
    """
    强大的文字反转工具（无需导入任何模块）
    
    参数:
        text: 要处理的字符串
        reverse_words: 
            False=整体反转（默认）
            True=按单词反转
    
    返回:
        处理后的字符串
    
    示例:
        >>> text_reverse("hello world")
        'dlrow olleh'
        >>> text_reverse("hello world", True)
        'world hello'
        >>> text_reverse("Python很棒！")
        '！棒nohtyP'
    """
    if reverse_words:
        return ' '.join(text.split()[::-1])
    else:
        return text[::-1]
        
def Abcer(sz: int, pattern_type: str = 'sz') -> str:
    """
    生成数字/字母金字塔模式（sz=行数，pattern_type=模式类型）
    
    参数:
        sz: 行数（1-9）
        pattern_type: 模式类型 ('sz'=数字, 'zm'=字母)
    
    返回:
        多行模式字符串
    
    示例:
        >>> print(Abcer(3))
        1
        22
        333
        
        >>> print(Abcer(4, 'zm'))
        A
        BB
        CCC
        DDDD
    """
    if not 1 <= sz <= 9:
        raise ValueError("行数必须在1-9之间")
    
    result = []
    for i in range(1, sz+1):
        if pattern_type == 'sz':
            line = str(i) * i
        elif pattern_type == 'zm':
            line = chr(64 + i) * i  # A的ASCII码是65
        else:
            raise ValueError("类型必须是'sz'或'zm'")
        result.append(line)
    return '\n'.join(result)
    
def Genhaer(num: float) -> float:
    """
    计算输入数字的平方根（牛顿迭代法实现）
    
    参数:
        num: 要计算平方根的数字（必须≥0）
    
    返回:
        输入数字的平方根
    
    示例:
        >>> Genhaer(16)
        4.0
        >>> Genhaer(2)
        1.4142135623730951
    """
    if num < 0:
        raise ValueError("输入数字不能为负数")
    if num == 0:
        return 0.0
    
    # 牛顿迭代法求平方根
    guess = num / 2  # 初始猜测值
    while True:
        new_guess = (guess + num / guess) / 2
        if abs(new_guess - guess) < 1e-10:  # 设置精度阈值
            return new_guess
        guess = new_guess