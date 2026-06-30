from system.models import Menu, Config
from system.serializer.menu_ser import MenuSerializer

def build_menu_tree(flat_data):
    nodes = {}
    for item in flat_data:
        nodes[item["id"]] = {
            "id": item["id"],
            "label": item["name"],
            "disabled": True if item['status']=="0" else False,
            "children": []
        }

    tree = []
    for item in flat_data:
        parent_id = item["parent_id"]
        if parent_id and parent_id in nodes:
            nodes[parent_id]["children"].append(nodes[item["id"]])
        else:
            tree.append(nodes[item["id"]])


    def clean_children(node):
        if not node["children"]:
            node.pop("children")
        else:
            for child in node["children"]:
                clean_children(child)

    for t in tree:
        clean_children(t)

    return tree

def build_dept_tree(flat_data):
    nodes = {}
    for item in flat_data:
        nodes[item["id"]] = {
            "id": item["id"],
            "label": item["name"],
            "disabled": True if item['status']=="0" else False,
            "children": []
        }

    tree = []
    for item in flat_data:
        parent_id = item["parent_id"]
        if parent_id and parent_id in nodes:
            nodes[parent_id]["children"].append(nodes[item["id"]])
        else:
            tree.append(nodes[item["id"]])


    def clean_children(node):
        if not node["children"]:
            node.pop("children")
        else:
            for child in node["children"]:
                clean_children(child)

    for t in tree:
        clean_children(t)

    return tree


def get_all_menu_dict(data):
    """
    获取所有菜单数据，重组结构
    """
    tree_dict = {}
    for item in data:
        if item["menu_type"] == "F":
            continue  # 直接跳过按钮类型
        if item["parent_id"] == 0:
            if item["is_frame"] == "1":
                top_menu = {
                    "id": item["id"],
                    "path": item["path"],
                    "component": "Layout",
                    "children": [{
                        "path": item["path"],
                        "meta": {
                            "title": item["name"],
                            "icon": item["icon"],
                            "noCache": True,
                            "link": None
                        }
                    }],
                    "parent_id": item["parent_id"],
                    "sort": item["sort"]
                }
            else:
                top_menu = {
                    "id": item["id"],
                    "name": item["route_name"],
                    "path": "/" + item["path"],
                    "redirect": "noRedirect",
                    "component": "Layout",
                    "alwaysShow": True,
                    "meta": {
                        "title": item["name"],
                        "icon": item["icon"],
                        "noCache": True,
                        "link": None
                    },
                    "parent_id": item["parent_id"],
                    "sort": item["sort"],
                    "children": []
                }
            tree_dict[item["id"]] = top_menu
        else:
            if item["is_frame"] == "1":
                children_menu = {
                    "id": item["id"],
                    "name": item["route_name"],
                    "path": item["path"],
                    "component": "Layout",
                    "meta": {
                        "title": item["name"],
                        "icon": item["icon"],
                        "noCache": True,
                        "link": None
                    },
                    "parent_id": item["parent_id"],
                    "sort": item["sort"]
                }
            elif item["visible"]:
                children_menu = {
                    "id": item["id"],
                    "name": item["route_name"],
                    "path": item["path"],
                    "component": item["component"],
                    "meta": {
                        "title": item["name"],
                        "icon": item["icon"],
                        "noCache": True,
                        "link": None
                    },
                    "parent_id": item["parent_id"],
                    "sort": item["sort"]
                }
            else:
                children_menu = {
                    "id": item["id"],
                    "name": item["route_name"],
                    "path": item["path"],
                    "component": item["component"],
                    "meta": {
                        "title": item["name"],
                        "icon": item["icon"],
                        "noCache": True,
                        "link": None
                    },
                    "hidden": True,
                    "parent_id": item["parent_id"],
                    "sort": item["sort"]
                }
            tree_dict[item["id"]] = children_menu
    return tree_dict

def get_init_pwd():
    return Config.objects.get(key='sys.user.initPassword').value