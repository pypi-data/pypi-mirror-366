
def skip_check_accesstoken(func):
    """标记第三方API（跳过访问令牌检查）"""
    func._skip_check_accesstoken = True
    return func