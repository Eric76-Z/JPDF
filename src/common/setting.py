from os.path import dirname, abspath

# 获取项目根目录  E:\python\JPDF\src
base_dir = dirname(dirname(abspath(__file__)))
# print(base_dir)

conf_json = base_dir + '/configure/project_conf.json'
main_ui_path = base_dir + '/ui/main.ui'
print(conf_json)
# tableWidget_selected 设置
header_field = ['全选', '页数', '删除']

origin_conf = {
    'path_conf': {
        'last_work_path': '/',
        'export_path': '/',
    },
    'selected_files_list': [

    ],
    'recommended_constant': {
        'export_file_name': ''
    }
}
