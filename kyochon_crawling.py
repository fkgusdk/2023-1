
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

def get_sido_list(wd): # 모든 '시/도'를 리스트로 반환
    try: 
        # 시/도 선택하는 부분 선택해 html 정보 갱신 (시/도 담은 코드 추가됨)
        Select(wd.find_element(By.ID, 'sido1'))
        wd.implicitly_wait(5)
        
        # html 코드 불러오기
        html = wd.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 추가되어 나타난 option 태그에서 시/도 정보 추출
        sido_lst = [sido.text for sido in soup.select("select > option")]
        return sido_lst[1:-1]
    except:
        # 오류 났을 시
        print('Fail to get sido list')
        return
    
def get_gungu_list(wd): # 해당 시/도의 모든 '군/구'를 리스토 반환
    try: 
        # html 코드 불러오기
        html = wd.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 추가되어 나타난 option 태그에서 해당 시도의 모든 군/구 추출
        return [gungu.text for gungu in soup.select('#sido2 option')]
    except:
        # 오류났을 시
        print('Fail to get gungu list')
        return
    
def Kyochon_store(result): # 교촌 치킨 매장 정보를 리스트로 반환
    
    # WebDriver 객체 생성
    wd = webdriver.Chrome('C:/Users/user/My_Python/WebDriver/chromedriver.exe')
    
    # 웹페이지 연결
    wd.get('https://www.kyochon.com/shop/domestic.asp')
    wd.implicitly_wait(5) # 완벽하게 로드될 때까지 기다리기 (5초 넘으면 그냥 넘아가기)
    
    # 모든 '시/도'를 리스트로 반환
    sido_list = get_sido_list(wd)
    
    # 모든 촌 치킨 매장 정보 수집
    for sido_i in range(0,len(sido_list)): # 모든 시/도에 대해서
        
        crnt_sido = sido_list[sido_i] # 현재 조사하고 있는 시/도의 이름
        
        # 조사할 시도 선택하기
        select = Select(wd.find_element(By.ID, 'sido1')) # 시/도 선택 부분 선택
        wd.implicitly_wait(5) # 모두 로드될 때까지 기다리기 (5초 이상 걸리면 넘어감)
        select.select_by_value(str(sido_i+1)) # 조사할 시/도 하나 선택 (+1 : html에서 value=1 부터 시작)
        wd.implicitly_wait(5)
        
        # 해당 시도의 모든 군/구 알아내기
        select = Select(wd.find_element(By.ID, 'sido2')) # 군/구 선택 부분 선택 (html에 군/구 담은 코드 추가됨)
        wd.implicitly_wait(5)
        gungu_list = get_gungu_list(wd) # 해당 시/도의 모든 군/구 리스트로 저장
        
        # 해당 시/도의 매장 정보 추출
        for gungu_i in range(0,len(gungu_list)): # 해당 시/도의 모든 군/구에 대하여
            
            crnt_gungu = gungu_list[gungu_i] # 현재 조사할 군/구의 이름
            
            # 조사할 군/구 선택하기
            select = Select(wd.find_element(By.ID, 'sido2')) # 군/구 선택 부분 선택
            wd.implicitly_wait(5)
            select.select_by_value(str(gungu_i+1)) # 조사할 군/구 선택
            wd.implicitly_wait(5)
            
            # 선택한 시/도 & 군/구의 매장 검색
            wd.execute_script('search()')
            wd.implicitly_wait(5)
            
            # 갱신된 html 코드 불러오기
            html = wd.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 정보 추출
            store = [name.text for name in soup.select('.store_item > strong')] # 매장 이름
            store_address = [list(address)[0].string.strip() for address in soup.select('.store_item > em')] # 매장 주소
            for i in range(0,len(store)): # 반환할 리스트에 [매장 이름, 시/도, 군/구, 매장 주소] 추가하기
                result.append([store[i], crnt_sido, crnt_gungu, store_address[i]])

    return result


result = [] # 매장 정보 담을 리스트
result = Kyochon_store(result) # 담아오기

# 데이터 프레임으로 전환 후 csv 로 저장
tbl = pd.DataFrame(result, columns = ('store','sido','gungu','store_address'))
tbl.to_csv('./kyochon.csv', encoding = 'cp949', mode = 'w', index = True)




