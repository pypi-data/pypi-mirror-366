import mxupy as mu
from mxupy import IM, EntityXControl

class TreeDataPath:
    
    def __init__(self, nameFieldName='', namePathFieldName='', isAllowRepeat=False, isAllowRepeatOfAll=True):
        
        # 名称字段名、名称路径字段名
        self.nameFieldName = nameFieldName
        self.namePathFieldName = namePathFieldName
        
        # 同父亲下是否允许重复、是否允许所有重复
        self.isAllowRepeat = isAllowRepeat
        self.isAllowRepeatOfAll = isAllowRepeatOfAll
        
class TreeData:
    
    def __init__(self, idFieldName='id', parentIdFieldName='parentId', nameFieldName='name', paths=[]):
        
        # ID字段名、父ID字段名、名称字段名
        self.idFieldName = idFieldName
        self.parentIdFieldName = parentIdFieldName
        self.nameFieldName = nameFieldName
        
        # 路径数据列表
        self.paths = paths

class TreeEntityXControl(EntityXControl):
    
    def __init__(self, td=None):
        # 调用父类 mu.EntityXControl 的 __init__ 函数
        super().__init__()
        
        if td is None:
            td = TreeData()
        self.td = td
        
        # 树形结构必要字段
        self.treePatternFields = ["depth", "path", "hasChildren"]
        
        if not td.paths:
            td.paths = []
        else:
            for path in td.paths:
                # 添加名称字段名、添加名称路径字段名
                self.treePatternFields.append(path.nameFieldName)
                self.treePatternFields.append(path.namePathFieldName)

    def has_pattern_fields(self, fields=None):
        """ 校验树形结构必要字段

        参数:
            fields (list[str]): 字段集

        返回:
            bool: 是否匹配
        """
        if not fields:
            return True
        
        return any(field in fields for field in self.treePatternFields)
        
        # if fields == "*":
        #     return True
        # flst = fields.split(",")
        # return any(field in flst for field in self.treePatternFields)

    def has_same_name(self, model):
        """ 是否存在同样的名字

        Args:
            model (obj): 实体对象

        Returns:
            bool: 存在否
        """
        if not self.td.paths:
            return False
        
        im = self.dbe.to_dict(model)
        if not im.success:
            return im
        model = im.data
        
        for path in self.td.paths:
            
            # 无限制
            if path.isAllowRepeat and path.isAllowRepeatOfAll:
                continue
            
            # 唯一
            if not path.isAllowRepeatOfAll:
                
                im = self.exists([
                    {path.nameFieldName:mu.get_attr(model, path.nameFieldName, '')}, 
                    {self.td.idFieldName:('!=', mu.get_attr(model, self.td.idFieldName, -1))}
                ])
                
                if im.data:
                    return True
                
            # 同级唯一
            if not path.isAllowRepeat and path.isAllowRepeatOfAll:
                
                im = self.exists([
                    { self.td.parentIdFieldName:mu.get_attr(model, self.td.parentIdFieldName, None) }, 
                    { path.nameFieldName:mu.get_attr(model, path.nameFieldName, '') }, 
                    { self.td.idFieldName:('!=',mu.get_attr(model, self.td.idFieldName, -1)) }
                ])
                if im.data:
                    return True
                
        return False

    def validate_name(self, model, is_add=True, fields=None):
        """ 

        Args:
            model (obj): 实体
            is_add (bool): 添加否
            fields (list[str]): 字段集

        Returns:
            IM: 验证成功否
        """
        im = mu.IM()
        
        im = self.dbe.to_dict(model)
        if not im.success:
            return im
        model = im.data
        
        for path in self.td.paths:
            if is_add or fields == None or path.nameFieldName in fields:
                name = mu.get_attr(model, self.td.nameFieldName, '')
                if not name:
                    im.success = False
                    im.msg = f"{'添加' if is_add else '修改'}失败，{path.nameFieldName}不能为空。"
                    return im
                if '/' in name:
                    im.success = False
                    im.msg = f"{'添加' if is_add else '修改'}失败，{path.nameFieldName}不能包含'/'。"
                    return im
                
        return im

    def fix_pattern(self, model):
        im = mu.IM()
        
        im = self.dbe.to_dict(model, fields=self.fields)
        if not im.success:
            return im
        model = im.data
        
        # 更新自身
        # 如果自身是最顶级分类
        if mu.to_int(mu.get_attr(model, self.td.parentIdFieldName)) < 1:
            model[self.td.parentIdFieldName] = None
            model['depth'] = 1
            model['path'] = mu.get_attr(model, self.td.idFieldName, -1)
            for path in self.td.paths:
                model[path.namePathFieldName] = mu.get_attr(model, path.nameFieldName)
        else:
            im = self.get_one_by_id(mu.get_attr(model, self.td.parentIdFieldName))
            if not im.success:
                return im
            parent = im.data
            mu.set_attr(model, "depth", int(mu.get_attr(parent, "depth")) + 1)
            mu.set_attr(model, "path",
                str(mu.get_attr(parent, "path")) +
                "," +
                str(mu.get_attr(model, self.td.idFieldName, -1))
            )
            for path in self.td.paths:
                mu.set_attr(model, path.namePathFieldName,
                    str(mu.get_attr(parent, path.namePathFieldName)) +
                    "/" +
                    str(mu.get_attr(model, path.nameFieldName))
                )
            # 他的父亲HasChildren必须是True
            mu.set_attr(parent, "hasChildren", True)
            im = super().update_by_id(mu.get_attr(parent, self.td.idFieldName), parent, "hasChildren")
            if not im.success:
                return im
            
        # 更新自身HasChildren属性
        im = self.exists({self.td.parentIdFieldName:mu.get_attr(model, self.td.idFieldName, -1)})
        if not im.success:
            return im
        model['hasChildren'] = im.data
        # has_children = self.exists(self.td.parentIdFieldName == mu.get_attr(model, self.td.idFieldName, -1))
        # setattr(model, "hasChildren", has_children)

        im = super().update({self.td.idFieldName:mu.get_attr(model, self.td.idFieldName, -1)}, model, self.treePatternFields)
        if not im.success:
            return im

        # 更新子节点
        im = self.get_list(where={self.td.parentIdFieldName:mu.get_attr(model, self.td.idFieldName, -1)})
        if im.error:
            return im
        children = im.data
        for child in children:
            im = self.fix_pattern(child)
            if not im.success:
                return im

        return im

    def add(self, model):
        im = mu.IM()
        if self.has_same_name(model):
            im.msg = '添加失败，已包含相同名称的节点。'
            return im

        im = self.validate_name(model)
        if not im.success:
            return im

        # 设置Path和NamePath为任意字符串，以避免在字段不可为空时添加或更新失败
        mu.set_attr(model, "path", "")
        for path in self.td.paths:
            mu.set_attr(model, path.namePathFieldName, "")

        im = super().add(model)
        if not im.success:
            return im
        model = im.data

        im = self.fix_pattern(model)
        if not im.success:
            return im

        # 确保在反馈的im中结果是实体
        im.data = model
        # im.id = mu.get_attr(model, self.td.idFieldName, -1)
        return im

    def update(self, where, model, fields=None, to_dict=False):
        """
            按 id 更新一条记录
        Args:
            where (list[dict]|dict): 包含查询条件的字典集
            model (model|dict): 新值
            fields (list[str]): 字段集
            to_dict: 结果转为字典
            
        Returns:
            im:  一条记录
        """
        im = mu.IM()
        if fields == "hasChildren":
            mu.set_attr(model, "hasChildren", self.has_children(mu.get_attr(model, self.td.idFieldName, -1)))
            return super().update(where, model, "hasChildren")
        elif not self.has_pattern_fields(fields):
            return super().update(where, model, fields)
        else:
            if self.has_same_name(model):
                return im.Error("更新失败，已包含相同名称的节点。")

            im = self.validate_name(model, False, fields)
            if not im.success:
                return im

            # 设置Path和NamePath为任意字符串，以避免在字段不可为空时添加或更新失败
            mu.set_attr(model, "path", "")
            for path in self.td.paths:
                mu.set_attr(model, path.namePathFieldName, "")
            im = super().update(where, model, fields, to_dict)
            if not im.success:
                return im

            # 修复自身和子路径
            im = self.fix_pattern(model)
            if not im.success:
                return im

            # 确保在反馈的im中结果是实体
            im.data = model
            # im.id = mu.get_attr(model, self.td.idFieldName, -1)
            return im

    def has_children(self, model):
        return self.exists(self.td.parentIdFieldName == mu.get_attr(model, self.td.idFieldName, -1))

    def has_children(self, id):
        return self.exists(self.td.parentIdFieldName == id)

    def get_children_ids(self, id, recursive=False, include_me=False):
        """
        获取子节点ID列表
        Args:
            id (int): 父节点ID
            recursive (bool, optional): 是否递归获取所有子节点. Defaults to False.
            include_me (bool, optional): 是否包含当前节点. Defaults to False.
        Returns:
            str: 子节点ID列表，逗号分隔
        """
        if id <= 0:
            id = None
        im = self.get_children(id, recursive, include_me, self.td.idFieldName)
        if im.error:
            return im
        return IM(True, '', ','.join([str(getattr(item, self.td.idFieldName)) for item in im.data]))

    def get_children(self, id, recursive=False, include_me=False, select=None):
        """
        获取指定节点的子节点列表
        
        Args:
            id (int): 节点ID
            recursive (bool, optional): 是否递归获取子节点。默认为False
            include_me (bool, optional): 是否包含当前节点。默认为False
            select (str, optional): 指定返回的字段。默认为 None
        
        Returns:
            IM: 结果
        """
        parent = None
        
        cs = None
        os = [{'path': 'asc'}, {'sort': 'asc'}]

        # 说明是获取根级节点
        if id is None or id <= 0:
            id = None
        else:
            im = self.get_one(where={self.td.idFieldName: id})
            if im.error:
                return im
            parent = im.data
        
        if recursive:
            # 父类不存在，说明是获取所有的节点
            if parent:
                cs = { 'path': ('startswith', parent.path + ',') }
        else:
            cs = { self.td.parentIdFieldName: id }
        
        
        im = self.get_list(select=select, where=cs, order_by=os)
        if im.error:
            return im
        chs = im.data
        
        # 拼合自己
        if include_me and parent:
            chs.insert(0, parent)
        
        im.data = chs
        return im
        
        
        
        # rlst = []
        # im = self.get_list(select=fields_and_extends, where={self.td.parentIdFieldName: id}, order_by={'sort': 'asc'})
        # if im.error or not im.data:
        #     return im
        
        # lst = im.data
        
        # if not lst:
        #     if include_me:
        #         e = self.get_one(id, fields_and_extends)
        #         return [e] if e else rlst
        #     return rlst

        # lst = sorted(lst, key=lambda x: getattr(x, "sort"))
        # for item in lst:
        #     rlst.append(item)
        #     if recursive:
        #         rlst.extend(self.get_children(getattr(item, self.td.idFieldName), recursive, False, fields_and_extends))
        # return rlst

    def get_parents_ids(self, id, include_me=False):
        e = self.get_one(id, "depth,path")
        if not e:
            return ""

        my_depth = getattr(e, "depth")
        my_path = getattr(e, "path")
        if my_depth == 1:
            return str(id) if include_me else ""
        return str(id) if include_me else my_path.replace(f",{str(id)}", "")

    def get_parents(self, id, include_me=False, fields_and_extends="*"):
        fs = f"depth,path,{self.td.parentIdFieldName},{fields_and_extends}"
        e = self.get_one(id, fs)
        if not e:
            return []

        my_depth = int(getattr(e, "depth"))
        my_path = getattr(e, "path")
        if my_depth == 1:
            return [e] if include_me else []

        if not include_me:
            my_path = my_path.replace(f",{str(id)}", "")

        return self.get_list(self.td.idFieldName + " IN " + my_path, order_by="depth DESC", fields=fs)

    def get_parent(self, id, depth=-1, include_me=True, fields_and_extends="*"):
        fs = f"depth,path,{self.td.parentIdFieldName},{fields_and_extends}"
        e = self.get_one(id, fs)
        if not e:
            return None

        # 获取当前节点的深度
        my_depth = int(getattr(e, "depth"))
        # 如果当前节点深度为1，则表示是根节点
        if my_depth == 1:
            return e if include_me else None

        # 如果未指定深度，则默认为当前节点深度减1
        if depth == -1:
            depth = my_depth - 1

        # 获取当前节点的父ID
        pid = int(getattr(e, self.td.parentIdFieldName))
        e2 = None
        # 循环查找直到找到指定深度的父节点
        while e2 is None or int(getattr(e2, "depth")) != depth:
            e2 = self.get_one(self.td.idFieldName == pid, fs)
            if e2 is not None:
                pid = int(getattr(e2, self.td.parentIdFieldName))

        # 返回找到的父节点，如果未找到指定深度的父节点则返回当前节点（如果include_me为True）
        return e2 if e2 and int(getattr(e2, "depth")) == depth else (e if include_me else None)

    def get_siblings(self, id, include_me=True, fields_and_extends="*"):
        c = self.get_one(id, self.td.parentIdFieldName)
        if not c:
            return []

        # 获取兄弟节点列表
        lst = self.get_children(getattr(c, self.td.parentIdFieldName), False, False, fields_and_extends)
        if include_me:
            return lst
        else:
            # 如果不包括当前节点，则从列表中移除
            lst2 = [item for item in lst if getattr(item, self.td.idFieldName) != str(id)]
            return sorted(lst2, key=lambda x: getattr(x, "sort"))

    def get_siblings_ids(self, id, include_me=True):
        c = self.get_one(id, self.td.parentIdFieldName)
        if not c:
            return ""

        # 获取兄弟节点的ID列表
        ids = self.get_children_ids(getattr(c, self.td.parentIdFieldName), False, False)
        if include_me:
            return ids
        else:
            # 如果不包括当前节点，则从列表中移除当前节点的ID
            ids_list = ids.split(",")
            ids_list.pop(ids_list.index(str(id)))
            return ",".join(ids_list)

    def delete(self, id, is_exists_verify=True):
        im = mu.IM()
        # 获取要删除节点的父节点
        c = self.get_parent(id, -1, False)
        if not c:
            return super().delete(id, is_exists_verify)

        im = super().delete(id, is_exists_verify)
        if not im.success:
            return im

        # 如果父节点没有其他子节点，则更新父节点的HasChildren属性为False
        if self.has_children(getattr(c, self.td.idFieldName)):
            return im

        c.set_value_ex("hasChildren", False)
        return super().update(c, "hasChildren")

    def set_new_parent(self, id, parent_id):
        im = mu.IM("指定父元素失败。")

        if id == parent_id:
            return im.error("原元素不能成为原元素的父亲")

        e = self.get_one(id)
        if not e:
            return im.error("原元素不存在。")

        former_parent_id = int(getattr(e, self.td.parentIdFieldName))
        if former_parent_id == parent_id:
            return im.error("新父元素就是原元素的父亲。")

        if parent_id != 0:
            p = self.get_one(parent_id)
            if not p:
                return im.error("父元素不存在。")

            if str(id) in getattr(p, "path").split(","):
                return im.error("新的父元素不能是原元素的子级元素。")

        e.set_value_ex(self.td.parentIdFieldName, parent_id)
        
        im = super().update(e)
        if not im.success:
            return im

        # 修复原父节点的HasChildren属性
        if former_parent_id != 0 and not self.has_children(former_parent_id):
            im = super().update(former_parent_id, "hasChildren", False)
            if not im.success:
                return im

        # 设置新父节点的HasChildren属性为True
        if parent_id != 0:
            im = super().update(parent_id, "hasChildren", True)
            if not im.success:
                return im

        # 修复节点的路径（Path, Depth等）
        es = self.get_list("path".IFLike(f"{getattr(e, 'path')},"))
        es.append(e)
        for et in es:
            im = self.fix_pattern(et)
            if not im.success:
                return im

        return im
    
if __name__ == '__main__':
    
    tc = TreeEntityXControl()
    
    has = tc.has_pattern_fields('*')
    print(has)
    
    # im = countyControl.add_county(11111, 1034, "安道尔1", "Andorra1")
    # print(im.data)
    
    # mc = countyControl.model_class
    # mc.delete().where(County.countyId == 11111).execute()
    
    # im = countyControl.init_data()
    # print(im.data)