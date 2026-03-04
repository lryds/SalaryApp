import flet as ft
import requests

API_BASE_URL = "http://60.204.247.2:5000"


def main(page: ft.Page):
    page.title = "员工薪酬查询"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 700

    current_user_code = ""

    emp_code_input = ft.TextField(label="职工代码", width=300)
    password_input = ft.TextField(label="密码", password=True, can_reveal_password=True, width=300)
    login_error_text = ft.Text(color="red")

    salary_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    old_pwd_input = ft.TextField(label="原密码", password=True, width=300)
    new_pwd_input = ft.TextField(label="新密码", password=True, width=300)
    pwd_msg_text = ft.Text()

    def show_login_page():
        page.controls.clear()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER  # 登录页居中
        page.add(
            ft.Text("薪酬查询系统", size=30, weight="bold"),
            emp_code_input,
            password_input,
            login_error_text,
            ft.ElevatedButton("登录", on_click=btn_login_click, width=300)
        )
        page.update()

    def show_main_page():
        page.controls.clear()
        page.vertical_alignment = ft.MainAxisAlignment.START  # 主页顶部对齐
        salary_list_view.controls.clear()
        salary_list_view.controls.append(ft.Text("数据加载中...", color="grey"))
        page.add(
            ft.Row([
                ft.Text(f"欢迎, 职工 {current_user_code}", size=20, weight="bold"),
                ft.IconButton(ft.icons.SETTINGS, on_click=lambda _: show_pwd_page()),
                ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: show_login_page())
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            salary_list_view  # ← 先挂载到页面
        )
        page.update()        # ← 先渲染页面框架
        load_salary_data()   # ← 再加载数据（此时视图已挂载）

    def show_pwd_page():
        page.controls.clear()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        pwd_msg_text.value = ""
        page.add(
            ft.Text("修改密码", size=25, weight="bold"),
            old_pwd_input,
            new_pwd_input,
            pwd_msg_text,
            ft.ElevatedButton("确认修改", on_click=btn_change_pwd_click, width=300),
            ft.TextButton("返回", on_click=lambda _: show_main_page())
        )
        page.update()

    def btn_login_click(e):
        nonlocal current_user_code
        try:
            res = requests.post(f"{API_BASE_URL}/login", json={
                "emp_code": emp_code_input.value,
                "password": password_input.value
            }, timeout=5)
            if res.status_code == 200:
                current_user_code = emp_code_input.value
                password_input.value = ""
                show_main_page()
            else:
                login_error_text.value = res.json().get("message", "登录失败")
                page.update()
        except Exception as ex:
            login_error_text.value = "无法连接服务器: " + str(ex)
            page.update()

    def load_salary_data():
        salary_list_view.controls.clear()
        try:
            res = requests.get(
                f"{API_BASE_URL}/salary?emp_code={current_user_code}",
                timeout=5  # ← 建议加超时
            )
            if res.status_code == 200:
                data = res.json().get("data", [])
                if not data:
                    salary_list_view.controls.append(ft.Text("暂无薪酬数据"))
                else:
                    for item in data:
                        card = ft.Card(
                            content=ft.Container(
                                padding=10,
                                content=ft.Column([
                                    ft.Text(f"月份: {item['month']}", weight="bold"),
                                    ft.Text(f"基本工资: {item['base']}"),
                                    ft.Text(f"奖金: {item['bonus']} | 扣款: {item['deduction']}"),
                                    ft.Text(f"实发: {item['net']}", color="green", weight="bold"),
                                ])
                            )
                        )
                        salary_list_view.controls.append(card)
            else:
                salary_list_view.controls.append(ft.Text(f"请求失败: {res.status_code}"))
        except Exception as ex:
            salary_list_view.controls.append(ft.Text(f"数据加载失败: {str(ex)}"))
        page.update()  # ← 数据写入后必须 update！

    def btn_change_pwd_click(e):
        try:
            res = requests.post(f"{API_BASE_URL}/change_password", json={
                "emp_code": current_user_code,
                "old_password": old_pwd_input.value,
                "new_password": new_pwd_input.value
            }, timeout=5)
            if res.status_code == 200:
                pwd_msg_text.value = "密码修改成功！请牢记新密码。"
                pwd_msg_text.color = "green"
            else:
                pwd_msg_text.value = res.json().get("message", "修改失败")
                pwd_msg_text.color = "red"
            page.update()
        except Exception as ex:
            pwd_msg_text.value = f"请求出错: {str(ex)}"
            pwd_msg_text.color = "red"
            page.update()

    show_login_page()


ft.app(target=main)
