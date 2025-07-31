class ApiControl():

    @classmethod
    def inst(cls):
        """ 单例模式，通过此函数返回对象的实例

        Returns:
            mu.ApiControl: 控制器实例
        """
        if not hasattr(cls, '_inst'):
            cls._inst = cls()
        return cls._inst
