import register_agent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if __name__ == "__main__":
    register_agent.generate("cases/mail163",run=True,headless=False,nap=5)


