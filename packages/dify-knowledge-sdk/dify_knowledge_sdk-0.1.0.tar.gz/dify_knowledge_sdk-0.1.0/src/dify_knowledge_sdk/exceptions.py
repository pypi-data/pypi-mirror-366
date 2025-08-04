class DifyError(Exception):
    """Base exception class for Dify SDK."""

    pass


class DifyAPIError(DifyError):
    """API error from Dify service."""

    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class DifyAuthenticationError(DifyAPIError):
    """Authentication error."""

    pass


class DifyValidationError(DifyAPIError):
    """Validation error."""

    pass


class DifyNotFoundError(DifyAPIError):
    """Resource not found error."""

    pass


class DifyConflictError(DifyAPIError):
    """Conflict error."""

    pass


class DifyServerError(DifyAPIError):
    """Server error."""

    pass


class DifyConnectionError(DifyError):
    """Connection error."""

    pass


class DifyTimeoutError(DifyError):
    """Timeout error."""

    pass


# Error code mappings
ERROR_CODE_MAPPING = {
    "no_file_uploaded": "请上传你的文件",
    "too_many_files": "只允许上传一个文件",
    "file_too_large": "文件大小超出限制",
    "unsupported_file_type": "不支持的文件类型",
    "high_quality_dataset_only": '当前操作仅支持"高质量"知识库',
    "dataset_not_initialized": "知识库仍在初始化或索引中。请稍候",
    "archived_document_immutable": "归档文档不可编辑",
    "dataset_name_duplicate": "知识库名称已存在，请修改你的知识库名称",
    "invalid_action": "无效操作",
    "document_already_finished": "文档已处理完成。请刷新页面或查看文档详情",
    "document_indexing": "文档正在处理中，无法编辑",
    "invalid_metadata": "元数据内容不正确。请检查并验证",
}
