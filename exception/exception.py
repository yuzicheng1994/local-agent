class ServiceException(Exception):
    """服务异常基类"""

    def __init__(self, status_code: int = 500, message: str = "服务异常"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)


class AgentNotInitializedException(ServiceException):
    """Agent未初始化异常"""

    def __init__(self):
        super().__init__(500, "Agent服务未初始化")


class VectorStoreNotInitializedException(ServiceException):
    """向量存储未初始化异常"""

    def __init__(self):
        super().__init__(500, "向量存储未初始化")
