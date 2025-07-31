
def accesstoken_user_id(func):
    """验证并注入令牌中的UserID"""
    func._accesstoken_user_id = True
    return func