
def third_party_api(func):
    """标记第三方API（跳过Token验证）"""
    func._third_party_api = True
    return func