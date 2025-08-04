

class BFLError(Exception):
    """BFL API 错误基类"""
    def __init__(self, code: int, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

# 预定义错误类型
ERROR_MESSAGES = {
    401: "API key 无效",
    402: "积分不足",
    429: "超出并发限制",
    400: "请求参数错误",
    500: "服务器内部错误"
}

def get_error_message(status_code: int, default_message: str | None = None) -> str:
    """获取错误信息"""
    return ERROR_MESSAGES.get(status_code, default_message or f"未知错误: {status_code}")
