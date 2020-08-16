import os
from time import sleep

# current_case_file_name = ""

def generate(case_folder_path, specify_cases=[], headless=True, closewindows=True, wait=0, nap=0, run=True):
    test_folder_name = case_folder_path.split("/")[1]
    test_agent_file_name = "test_{}_agent.py".format(test_folder_name)
    # current_case_file_name = test_agent_file_name
    test_class_name = "Test{}Class".format(test_folder_name)

    if len(specify_cases)==0:
        case_file_paths = os.listdir(case_folder_path)
    else:
        case_file_paths = specify_cases

    print("识别到总共有{}个场景".format(len(case_file_paths)))
    print("开始生成测试脚本>>")

    with open(test_agent_file_name,"w",encoding="UTF-8") as file:
        file.writelines(["from test_base import TestBase\n","import pytest\n"])
        file.writelines(["\n","\n"])
        file.writelines(["class {}(TestBase):\n".format(test_class_name)])
        file.writelines(["\n"])

        for case_file in case_file_paths:
            case_name = case_file.split(".")[0]
            file.writelines(["    def {}(self):\n".format(case_name)])
            file.writelines(["        self.init('{}/{}',headless={},nap={},closewindows={},wait={})\n" \
                                .format(case_folder_path,case_file,headless,nap,closewindows,wait)])
            file.writelines(["        self.run()\n"])
            file.writelines(["\n"])

            print("场景{}测试脚本已经生成".format(case_name))




        file.writelines(["test_example = {}()\n".format(test_class_name)])
        file.writelines(["\n"])

        for case_file in case_file_paths:
            case_name = case_file.split(".")[0]
            file.writelines(["def test_{}():\n".format(case_name)])
            file.writelines(["    test_example.{}()\n".format(case_name)])
            file.writelines(["\n"])
            

    print("自动化测试脚本已经生成完毕。")
    print("****************************************************")

    if run:
        __run_auto_test__(test_agent_file_name)


def __run_auto_test__(test_agent_file_name):
    if len(test_agent_file_name)>0:
        sleep(5) #等候5秒开始跑测试用例
        print("开始跑测试用例>>")
        os.system("pytest -s -q --alluredir ./report "+test_agent_file_name)
        sleep(5)
        os.system("allure generate ./report -o ./report/html --clean")
        print("测试用例已跑完。")
    else:
        pass
