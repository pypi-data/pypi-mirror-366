import json
import random
import string
from datetime import datetime
class GeneralToolkit:
    def __init__(self) -> None:
        # 限制最大 JSON 长度为 1MB，防止过大的恶意输入
        self.MAX_JSON_LENGTH = 1024 * 1024

    def check_common_substrings(self, input_string, substr_list):
        """
        检查字符串是否包含列表中的任何完整子字符串

        参数:
        input_string (str): 需要检查的字符串
        substr_list (list): 用于比较的子字符串列表

        返回:
        bool: 如果存在匹配的子字符串返回 True，否则返回 False
        """
        for substr in substr_list:
            if substr in input_string:
                return True
        return False

    def filter_sensitive_words(self, sensitive_words: list[str], text: str, replacement: str = '*') -> str:
        """
        将文本中的敏感词替换为指定字符串，每个敏感词仅替换一次

        参数:
            sensitive_words: 敏感词列表
            text: 需要过滤的文本
            replacement: 用于替换敏感词的字符串，默认为星号(*)

        返回:
            过滤后的文本
        """
        # 按长度降序排列敏感词，确保长词优先被替换
        sensitive_words = sorted(sensitive_words, key=len, reverse=True)

        filtered_text = text
        for word in sensitive_words:
            filtered_text = filtered_text.replace(word, replacement, 1)  # 仅替换一次

        return filtered_text

    def is_safe_json_structure(self, obj) -> bool:
        """
        验证 JSON 对象结构是否安全（只允许 object 或 array 作为根节点）

        参数:
            obj: 解析后的 JSON 对象

        返回:
            bool: 结构安全返回 True，否则返回 False
        """
        return isinstance(obj, (dict, list))

    def json_format(self, content: str, is_json: bool = True, should_dump: bool = True) -> str | dict | list:
        """
        格式化 JSON 字符串，增加安全性处理

        参数:
            content: 待格式化的字符串
            is_json: 是否强制作为 JSON 处理
            should_dump: 是否对解析后的对象执行 json.dumps，默认为 True

        返回:
            格式化后的 JSON 字符串或解析后的 Python 对象（dict/list）或原始内容

        异常:
            ValueError: 输入不符合 JSON 格式或结构不安全
            TypeError: 输入类型错误
        """
        # 检查输入类型
        if not isinstance(content, str):
            raise TypeError(f"Expected string, got {type(content).__name__}")

        # 检查输入长度
        if len(content) > self.MAX_JSON_LENGTH:
            raise ValueError(f"Input exceeds maximum length of {self.MAX_JSON_LENGTH} characters")

        # 如果明确不是 JSON 且不需要强制处理，直接返回
        if not is_json:
            return content

        try:
            # 解析 JSON
            parsed = json.loads(content)

            # 验证 JSON 结构安全性
            if not self.is_safe_json_structure(parsed):
                raise ValueError("Unsafe JSON structure: root must be object or array")

            # 根据 should_dump 参数决定是否执行 json.dumps
            if should_dump:
                return json.dumps(parsed, indent=4, ensure_ascii=False)
            else:
                return parsed

        except json.JSONDecodeError as e:
            # 处理 JSON 解析错误
            if is_json:
                # 如果强制要求是 JSON，抛出错误
                raise ValueError(f"Invalid JSON format: {str(e)}") from e
            else:
                # 否则返回原始内容
                return content
        except ValueError as e:
            # 重新抛出安全验证错误
            raise ValueError(f"Unsafe JSON structure: {str(e)}") from e
        except Exception as e:
            # 处理其他异常
            raise ValueError(f"Unexpected error processing JSON: {str(e)}") from e


    def get_ua(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
            'Opera/8.0 (Windows NT 5.1; U; en)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
        ]
        user_agent = random.choice(user_agents)  # random.choice(),从列表中随机抽取一个对象
        return user_agent
    
    def get_headers(self) -> dict:
        """返回一个包含随机 User-Agent 的 HTTP 头字典"""
        user_agent = self.get_ua()
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent
        }
        return headers

    def get_formatted_time(self) -> str:
        """返回格式为 'YYYY-MM-DD HH:MM:SS' 的当前时间字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_device_id(self, length: int = 22, segments: int = 3, separator: str = '_') -> str:
        """
        生成随机设备ID，格式类似 "WiRsasjclDTQ2eVSz6_SY"

        Args:
            length: 每个段的字符长度（默认22）
            segments: 段的数量（默认3）
            separator: 段之间的分隔符（默认下划线）

        Returns:
            生成的随机设备ID字符串
        """
        # 允许的字符集合（大小写字母和数字）
        allowed_chars = string.ascii_letters + string.digits

        # 生成每个段的随机字符串
        parts = [
            ''.join(random.choice(allowed_chars) for _ in range(length))
            for _ in range(segments)
        ]

        # 使用分隔符连接各段
        return separator.join(parts)
