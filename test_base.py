import pytest
import requests
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement 
from selenium.webdriver.chrome.options import Options
import json
import allure
from time import sleep
from time import time
from selenium.webdriver.common.keys import Keys

class TestBase:
   
    def init(self,case_file_path,headless=True,closewindows=True,wait=0,nap=0):
        self.case_file_path = case_file_path
        self.closewindows = closewindows
        self.nap = nap
        json_file = open(case_file_path,"r",encoding="UTF-8")
        self.case_json = json.load(json_file)
        self.agent_options = []
        all_case_type = [case["type"] for case in self.case_json]
        if "page" in all_case_type:
            self.agent_options.append("selenium")
        if "api" in all_case_type:
            self.agent_options.append("requests")
            

        if "selenium" in self.agent_options:
            self.chrome_options = Options()
            if headless:
                self.chrome_options.add_argument('headless') # 设置option
            
            self.chrome_options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(options=self.chrome_options)
        
        if "requests" in self.agent_options:
            self.req_s = requests.session()
        
        sleep(wait)



    def login(self,url,method="GET",data={}):
        if url=="":
            pass
        else:
            if "selenium" in self.agent_options:
                self.driver.get(url)
            
            if "requests" in self.agent_options:
                if method=="GET":
                    self.req_s.get(url)
                else:
                    self.req_s.post(url,data=json.dumps(data),headers={"Content-Type":"application/json"})


    def run(self):
        case_total = len(self.case_json)
        count = 0     
        
        for case in self.case_json:
            try:
                if case["type"]=="page": #是页面访问，用selenium
                    expect_pass = self.__page_req__(case)  
                    if expect_pass:
                        count = count+1
                    else:
                        print("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过")
                        allure.attach("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过",allure.attachment_type.TEXT)
                

                elif case["type"]=="api": #是接口测试，用requests
                    expect_pass = self.__api_req__(case)  
                    if expect_pass:
                        count = count+1
                    else:
                        print("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过")
                        allure.attach("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过",allure.attachment_type.TEXT)
                
                elif case["type"]=="click":
                    expect_pass = self.__click_req__(case)
                    if expect_pass:
                        count = count+1
                    else:
                        print("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过")
                        allure.attach("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过",allure.attachment_type.TEXT)
                
                elif case["type"]=="fill":
                    expect_pass = self.__fill_req__(case)
                    if expect_pass:
                        count = count+1
                    else:
                        print("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过")
                        allure.attach("不是期望结果","场景["+self.case_file_path+"]用例["+case["title"]+"]未通过",allure.attachment_type.TEXT)
                
                else:
                    pass
                
            except Exception as ex:
                print("异常信息："+str(ex),"场景["+self.case_file_path+"]用例["+case["title"]+"]未通过")
                allure.attach("异常信息："+str(ex),"场景["+self.case_file_path+"]用例["+case["title"]+"]未通过",allure.attachment_type.TEXT)
                if case["type"]=="page" or  case["type"]=="click" or case["type"]=="fill":
                    fail_screenshot_file = self.__screenshot_as_file__() 
                    allure.attach.file(fail_screenshot_file, '失败用例截图:{filename}'.format(filename=fail_screenshot_file),allure.attachment_type.PNG)
                continue

            sleep(self.nap)

        if hasattr(self,"driver"):
            try:
                if self.closewindows:
                    self.driver.close()
                    self.driver.quit()
                # pass
            except:
                pass
        else:
            pass

        #所有用例通过才算通过
        assert count==case_total

    def __page_req__(self,case):
        driver = self.driver
        driver.implicitly_wait(10)
        method = case["method"]
        if method=="GET":
            driver.get(case["url"])
        else:
            pass

        return self.__expect_counter_for_driver__(driver,case)


    def __api_req__(self,case):
        method = case["method"]
        if method=="GET":
            resp = self.req_s.get(case["url"])
        elif method=="POST":
            headers = {"Content-Type":"application/json"}
            resp = self.req_s.post(case["url"],data=json.dumps(case["data"]),headers=headers)
        elif method=="DELETE":
            resp = self.req_s.delete(case["url"])
        else:
            pass
        
        if resp is None:
            return False
        else:
            return self.__expect_counter_for_api__(case,resp)

    def __click_req__(self,case):
        driver = self.driver
        el = driver.find_element_by_xpath(case["url"])
        driver.execute_script("arguments[0].click();", el)
        if case["method"]=="SWITCH":
            driver.switch_to.window(driver.window_handles[-1])
        
        return self.__expect_counter_for_driver__(driver,case)
        

    def __fill_req__(self,case):
        driver = self.driver
        form_datas = case["data"]["form_datas"]
        if "iframe_xpath" in case["data"]:
            iframe_xpath = case["data"]["iframe_xpath"]
            ifel = driver.find_element_by_xpath(iframe_xpath)
            driver.switch_to.frame(ifel)

        for fd in form_datas:
            if "id" in fd:
                input_el = driver.find_element_by_id(fd["id"])
            elif "name" in fd:
                input_el = driver.find_element_by_name(fd["name"])
            else:
                input_el = driver.find_element_by_xpath(fd["xpath"])
            
            input_el.clear()
            input_el.send_keys(fd["value"])

        
        return self.__expect_counter_for_driver__(driver,case)
        

    def __expect_counter_for_driver__(self,driver,case):
        expect_infos = case["expect"]
        expect_count = 0
        for ex in expect_infos:
            if ex["get_type"]=="id":
                el = driver.find_element_by_id(ex["key"]) 
                expect_count = expect_count + self.__assert_type_deliver__(ex,el)

            elif ex["get_type"]=="name":
                el = driver.find_element_by_name(ex["key"])                
                expect_count = expect_count + self.__assert_type_deliver__(ex,el)

            elif ex["get_type"]=="xpath":
                el = driver.find_element_by_xpath(ex["key"])
                expect_count = expect_count + self.__assert_type_deliver__(ex,el)
            
            elif ex["get_type"]=="class":
                els = driver.find_elements_by_class_name(ex["key"])       
                expect_count = expect_count + self.__assert_type_deliver__(ex,els)    

            elif ex["get_type"]=="tag":
                els = driver.find_elements_by_tag_name(ex["key"])
                expect_count = expect_count + self.__assert_type_deliver__(ex,els)
            
            elif ex["get_type"]=="careless":
                expect_count = expect_count + 1
            
            else:
                pass

        return expect_count==len(expect_infos)

    def __expect_counter_for_api__(self,case,resp):
        expect_infos = case["expect"]
        expect_count = 0
        for ex in expect_infos:
            if ex["get_type"]=="json":
                result = resp.json()
                keys = ex["key"].split("/")
                for k in keys:
                    if k.isdigit():
                        result = result[int(k)]
                    else:
                        result = result[k]
                
                expect_count = expect_count + self.__assert_type_deliver__(ex,result)

            elif ex["get_type"]=="xml":
                pass

            elif ex["get_type"]=="value":
                result = resp.text
                expect_count = expect_count + self.__assert_type_deliver__(ex,result)

            elif ex["get_type"]=="careless":
                expect_count = expect_count + 1
            
            else:
                pass
    
        return expect_count==len(expect_infos)

    def __assert_type_deliver__(self,ex,el):
        expect_count = 0
        if ex["assert_type"]=="contain":
            if self.__contain__(ex["key_value"],el):
                expect_count = 1
            else:
                pass

        elif ex["assert_type"]=="equal":
            if self.__equal__(ex["key_value"],el):
                expect_count = 1
            else:
                pass
            
        elif ex["assert_type"]=="exist":
            if self.__exist__(el):
                expect_count = 1
            else:
                pass

        else:
            pass

        return expect_count

    def __contain__(self, key_value,el):
        if type(el) is list:
            for item in el:
                if key_value in item.text:
                    return True
                else:
                    continue
            
            return False
        elif type(el) is WebElement:
            if key_value in el.text:
                return True
            else:
                return False
        else:
            if key_value in str(el):
                return True
            else:
                return False

    def __equal__(self, key_value,el):
        if type(el) is list:
            for item in el:
                item.text==2
                if key_value == item.text:
                    return True
                else:
                    continue
            
            return False
        elif type(el) is WebElement:
            if key_value == el.text:
                return True
            else:
                return False
        else:
            if key_value == str(el):
                return True
            else:
                return False

    def __exist__(self,el):
        if type(el) is list:
            if len(el)>0:
                    return True
            else:
                return False
       
        else:
            if el is not None:
                return True
            else:
                return False

    def __screenshot_as_file__(self):
        '''在本地截图函数'''
        try:
            pic_pth = r"D:\2020\python\auto_test\report\screenshot"
            filename = pic_pth + "\\" + str(time.time()).split('.')[0] + '.png'
            self.driver.get_screenshot_as_file(filename)
            return filename
        except Exception as e:
            print(e)
            return None
        

      