from lib.jobs_log import updateJobStatus
from lib.jobs_log import updateCrawler,push_to_parser
from lib.jobs_log import checkFile,samejobCount
from lib.common import getId, savePage
from lib.proxy_handler import get_agent
from lib.s3_handler import S3Handler
from bs4 import BeautifulSoup
import datetime
import requests, re 
from time import sleep
from lib.captcha_solver import CaptchaSolver

sleep_time = 3
def getPage(job):
    try:
        job_id = job['job_id']
        inputs = job['inputs']
        agent = requests.session()

        url = job['inputs'][0]
        page= agent.get(url['url'],verify= False)
        sleep(sleep_time)
        soup= BeautifulSoup(page.content, features='lxml')

        url2= job['inputs'][1]
        for a in soup.find_all('input', {'type': "hidden"}):
            url2['payload'][a.get('id')] = a.get('value')
        page2= agent.post(url2['url'], data= url2['payload'], headers= url2['headers'])
        sleep(sleep_time)
        soup2= BeautifulSoup(page2.content, features= 'lxml')

        url3= job['inputs'][2]
        collect =dict()
        body = soup2.find('body')
        for ii in body.text.split('\n'):
            ii = re.sub('\n|\t|\s+', '', ii)
            values = ii.split('|')
            if len(values) > 1 and '__VIEWSTATE' and '__EVENTVALIDATION' in values:
                data = [i for i in values[3:] if len(i) > 0 and 'hiddenField' not in i]
                for i in range(45):
                    collect[data[i]] = data[i + 1]

        payload= url3['payload']
        payload['__VIEWSTATE'] = collect['__VIEWSTATE']
        payload['__VIEWSTATEGENERATOR'] = collect['__VIEWSTATEGENERATOR']
        payload['__EVENTVALIDATION'] = collect['__EVENTVALIDATION']
        page3= agent.post(url3['url'], data= payload, headers= url3['headers'])
        sleep(sleep_time)
        soup3= BeautifulSoup(page3.content, features='lxml')

        url4= job['inputs'][3]
        collect1 = dict()
        body1 = soup3.find('body')
        for jj in body1.text.split('\n'):
            jj = re.sub('\n|\t|\s+','', jj)
            values1 = jj.split('|')
            if len(values1) > 1 and '__VIEWSTATE' and '__EVENTVALIDATION' in values1:
                data1 = [ j for j in values1[3:] if len(j) > 0 and 'hiddenField' not in j ]
                for j in range(36):
                    collect1[data[j]] = data1[j+1]

        payload2= url4['payload']
        payload2['__VIEWSTATE'] = collect1['__VIEWSTATE']
        payload2['__VIEWSTATEGENERATOR']= collect1['__VIEWSTATEGENERATOR']
        payload2['__EVENTVALIDATION']= collect1['__EVENTVALIDATION']
        page4= agent.post(url4['url'], data= payload2, headers= url4['headers'])
        sleep(sleep_time)
        soup4= BeautifulSoup(page4.content, features='lxml')

        url5= job['inputs'][4]
        collect2 = dict()
        body2 = soup4.find('body')
        for kk in body2.text.split('\n'):
            kk = re.sub('\n|\t|\s+','', kk)
            values2 = kk.split('|')
            if  len(values2) > 1 and '__VIEWSTATE' and '__EVENTVALIDATION' in values2:
                data2= [ k for k in values2[3:] if len(k) > 0 and 'hiddenField' not in k ]
                for k in range(45):
                    collect2[data2[k]] = data2[k+1]

        payload3= url5['payload']
        payload3['__VIEWSTATE'] = collect2['__VIEWSTATE']
        payload3['__VIEWSTATEGENERATOR'] = collect2['__VIEWSTATEGENERATOR']
        payload3['__EVENTVALIDATION'] = collect2['__EVENTVALIDATION']
        page5= agent.post(url5['url'], data= payload3, headers= url5['headers'])
        sleep(sleep_time)
        soup5= BeautifulSoup(page5.content, features='lxml')

        url6= job['inputs'][5]
        img= 'https://freesearchigrservice.maharashtra.gov.in/'+soup5.find('img',{'id':"imgCaptcha_new"}).get('src')
        captcha= agent.get(img)
        captcha_text = CaptchaSolver().deathbycaptcha_text(captcha.content)

        collect3 = dict()
        body3 = soup5.find('body')
        for ll in body3.text.split('\n'):
            ll = re.sub('\n|\t|\s+','', ll)
            values3 = ll.split('|')
            if len(values3) > 1 and '__VIEWSTATE' and '__EVENTVALIDATION' in values3:
                data3= [ l for l in values3[3:] if len(l) > 0 and 'hiddenField' not in l ]
                for l in range(36):
                    collect3[data3[l]] = data3[l+1]

        payload4= url6['payload']
        payload4['__VIEWSTATE'] = collect3['__VIEWSTATE']
        payload4['__VIEWSTATEGENERATOR'] = collect3['__VIEWSTATEGENERATOR']
        payload4['__EVENTVALIDATION'] = collect3['__EVENTVALIDATION']
        payload4['txtImg1'] = captcha_text

        page6= agent.post(url6['url'], data= payload4, headers= url6['headers'])
        res = page6
        sleep(sleep_time)
        print('==> ', res.status_code)

        #--- END OF LOGIC ---WITH 200 OK Response
        # 200 OK response 
        if res.status_code == 200:
            data_h = push_to_parser(res,job)
            print(data_h)
    except Exception as e:
        job['error'] = e
        updateJobStatus(job)
        pass

#job = {'job_id': '20817eda2dd247749f38bd21febf67a1', 'is_crawled': False, 'is_parsed': False, 'storage_id': '', 'extension': '.html', 'source': 'https://freesearchigrservice.maharashtra.gov.in/', 'source_type': 'sro', 'sub_type': 'rest', 'jira': 'gp_15_rest_of_maharashtra', 'crawl_queue': 'crawl_queue', 'parse_queue': 'transform_queue', 'email_queue': '', 'domain': 'freesearchigrservice.maharashtra.gov.in', 'database': 'registration_system', 'collection': 'india', 'job_script': 'jobs.maharashtra.rest_of_maharashtra_sro_job.jobs', 'crawl_script': 'crawler.maharashtra.rest_of_maharashtra_sro.getPage', 'parser_script': 'parser.maharashtra.rest_of_maharashtra_sro.parser', 'priorities': 'default', 'storage_path': '', 'state': 'Maharashtra', 'params': [{'selected_year': '2023', 'district_name': 'वाशिम', 'tahsil_name': 'वाशीम', 'village_name': 'ढिल्ली', 'property_number': 1}], 'crawl_count': 0, 'insert_time': datetime.datetime(2023, 9, 20, 13, 44, 39, 411917), 'update_time': datetime.datetime(2023, 9, 20, 13, 44, 39, 411921), 'error': '', 'inputs': [{'method': 'GET', 'url': 'https://freesearchigrservice.maharashtra.gov.in/'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'payload': {'ScriptManager1': 'UpMain|btnOtherdistrictSearch', '__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', 'HiddenField2': '', 'ddlFromYear': '2023', 'ddlDistrict': '---Select District----', 'txtAreaName': '', 'ddlareaname': '-----Select Area----', 'txtAttributeValue': '', 'txtImg': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__ASYNCPOST': 'true', 'btnOtherdistrictSearch': 'Rest of Maharashtra / उर्वरित महाराष्ट्र'}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'payload': {'ScriptManager1': 'UpMain|ddlDistrict1', 'HiddenField2': '', 'ddlFromYear1': '2023', 'ddlDistrict1': '33', 'ddltahsil': '---Select Tahsil----', 'ddlvillage': '-----Select Village----', 'txtAttributeValue1': '', 'txtImg1': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__EVENTTARGET': 'ddlDistrict1', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', '__ASYNCPOST': 'true'}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'payload': {'ScriptManager1': 'UpMain|ddltahsil', 'HiddenField2': '', 'ddltahsil': '5 ', 'ddlvillage': '-----Select Village----', 'txtAttributeValue1': '', 'txtImg1': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', 'ddlFromYear1': '2023', 'ddlDistrict1': '33', '__ASYNCPOST': 'true', '__LASTFOCUS': '', '__EVENTARGUMENT': '', '__EVENTTARGET': 'ddltahsil', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': ''}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'payload': {'ScriptManager1': 'UpMain|ddlvillage', 'HiddenField2': '', 'ddlFromYear1': '2023', 'ddlDistrict1': '33', 'ddltahsil': '5 ', 'ddlvillage': 'ढिल्ली', 'txtAttributeValue1': '', 'txtImg1': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__EVENTTARGET': 'ddlvillage', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', '__ASYNCPOST': 'true'}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'payload': {'ScriptManager1': 'UpMain|btnSearch_RestMaha', 'HiddenField2': '', 'ddlFromYear1': '2023', 'ddlDistrict1': '33', 'ddltahsil': '5 ', 'ddlvillage': 'ढिल्ली', 'txtAttributeValue1': 1, 'FS_PropertyNumber': '', 'txtImg1': '', 'FS_IGR_FLAG': '', '__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', '__ASYNCPOST': 'true', 'btnSearch_RestMaha': 'शोध / Search'}, 'type': 'data'}]}
#getPage(job)
