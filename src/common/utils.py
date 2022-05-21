def sync_dict(dict1, dict2):
    '''比较dict1与dict2：
    1, dict1中有的key, dict2中必须要有
    2, dict1中没有的key, dict2中需删除
    '''
    if len(dict1.keys()) > len(dict2.keys()):
        d = dict1
    else:
        d = dict2
    for key in d:
        if isinstance(dict1[key], dict):
            sync_dict(dict1[key], dict2[key])
        else:
            # key在dict1中存在，在dict2中不存在，需赋初始值
            if key in dict1.keys() and key not in dict2.keys():
                dict2[key] = dict1[key]
            # key在dict1中不存在，在dict2中存在，需pop
            elif key not in dict1.keys() and key in dict2.keys():
                dict2.pop(key)
    # setting.project_conf 中存在，CONF_JSON中不存在的元素，需要新增并赋值初始设定值
    # for o in origin_conf:
    #     if o not in CONF_JSON:
    #         CONF_JSON[o] = origin_conf[o]
    # # setting.path_conf 中不存在，CONF_JSON中存的元素，需要删除
    # for p in list(CONF_JSON.keys()):
    #     if p not in origin_conf:
    #         CONF_JSON.pop(p)
