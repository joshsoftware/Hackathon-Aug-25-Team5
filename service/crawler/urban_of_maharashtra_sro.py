from lib.jobs_log import updateJobStatus
from lib.jobs_log import updateCrawler,push_to_parser
from lib.jobs_log import checkFile,samejobCount
from lib.common import getId, savePage
from lib.proxy_handler import get_agent
from lib.s3_handler import S3Handler
from bs4 import BeautifulSoup
from lib.captcha_solver import CaptchaSolver
import datetime
import requests, re 
from time import sleep

sleep_time = 3
def getPage(job):
    try:
        job_id = job['job_id']
        inputs = job['inputs']
        agent = requests.session()
        url1 = job['inputs'][0]
        page1= agent.get(url1['url'], headers= url1['headers'], verify=False)
        sleep(sleep_time)

        soup=BeautifulSoup(page1.content , 'lxml')
        url2= job['inputs'][1]
        payload=url2['payload']
        for i in soup('input',{"type":"hidden"}):
            payload[i.get('id')]=i.get("value")
        
        # Page 2, response
        page2=agent.post(url2['url'], data=payload , headers=url2['headers'] ,verify=False)
        sleep(sleep_time)
        soup1=BeautifulSoup(page2.content , 'lxml')
        body = soup1.find('body')
        record1 = dict()
        for ii in body.text.split('\n'):
            ii = re.sub('\n|\t|\s+','', ii)
            values = ii.split('|')
            if len(values) > 1 and '__VIEWSTATE'in values:
                data = [ k for k in values if len(k) > 0 and 'hiddenField' not in k ]
                for k in range(58):
                    record1[data[k]] = data[k+1]

        url3= job['inputs'][2]
        payload1=url3['payload']
        payload1["__VIEWSTATE"]= record1["__VIEWSTATE"]
        payload1["__VIEWSTATEGENERATOR"]=record1["__VIEWSTATEGENERATOR"]
        payload1["__EVENTVALIDATION"]=record1["__EVENTVALIDATION"]

        # Page 3, response
        page3=agent.post(url3['url'], data=payload1 , headers=url3['headers'], verify=False)
        sleep(sleep_time)
        soup2=BeautifulSoup(page3.content , 'lxml')
        body1 = soup2.find('body')
        record2 = dict()
        for jj in body1.text.split('\n'):
            jj = re.sub('\n|\t|\s+','', jj)
            values1 = jj.split('|')
            if len(values1) > 1 and '__VIEWSTATE'in values1:
                data1 = [ j for j in values1 if len(j) > 0 and 'hiddenField' not in j ]
                for j in range(58):
                    record2[data1[j]] = data1[j+1]
        img='https://freesearchigrservice.maharashtra.gov.in/'+soup2.find('img',{'id':"imgCaptchaUrban"}).get('src')
        captcha=agent.get(img)
        captcha_text = CaptchaSolver().deathbycaptcha_text(captcha.content)
        print(captcha_text)
        url4=job['inputs'][3]
        payload2=url4['payload']
        payload2["txtImgUrban"]=captcha_text
        payload2["__VIEWSTATE"]= record2["__VIEWSTATE"]
        payload2["__VIEWSTATEGENERATOR"]=record2["__VIEWSTATEGENERATOR"]
        payload2["__EVENTVALIDATION"]=record2["__EVENTVALIDATION"]
        page4=agent.post(url4['url'], data=payload2 , headers=url4['headers'] ,verify=False)
        sleep(sleep_time)
        res = page4
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
#job={'job_id': 'ade0dbec5a594d54b1d41e4481a31bbf', 'is_crawled': False, 'is_parsed': False, 'storage_id': '', 'extension': '.html', 'source': 'https://freesearchigrservice.maharashtra.gov.in/', 'source_type': 'sro', 'sub_type': 'rest', 'jira': 'gp_15_urban_of_maharashtra', 'crawl_queue': 'crawl_queue', 'parse_queue': 'transform_queue', 'email_queue': '', 'domain': 'freesearchigrservice.maharashtra.gov.in', 'database': 'registration_system', 'collection': 'india', 'job_script': 'jobs.maharashtra.urban_of_maharashtra_sro_job.jobs', 'crawl_script': 'crawler.maharashtra.urban_of_maharashtra_sro.getPage', 'parser_script': 'parser.maharashtra.urban_of_maharashtra_sro.parser', 'priorities': 'default', 'storage_path': '', 'state': 'Maharashtra', 'params': [{'district_name': 'पुणे', 'year': '2023', 'village_name': "Budhavar Peth ", 'property_number': 12}], 'crawl_count': 0, 'insert_time': datetime.datetime(2023, 9, 20, 10, 23, 5, 105131), 'update_time': datetime.datetime(2023, 9, 20, 10, 23, 5, 105135), 'error': '', 'inputs': [{'method': 'GET', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'headers': {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'payload': {'ScriptManager1': 'UpMain|btnUrbansearch', '__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', 'ddlFromYear': '2023', 'ddlDistrict': '---Select District----', 'txtAreaName': '', 'ddlareaname': '-----Select Area----', 'txtAttributeValue': '', 'txtImg': ('',), 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__ASYNCPOST': 'true', 'btnUrbansearch': 'Urban Areas in Rest of Maharashtra / उर्वरित महाराष्ट्रातील शहरी भाग'}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'payload': {'ScriptManager1': 'UpMain|ddlDistrictUrban', 'ddlFromYearUrban': '2022', 'ddlDistrictUrban': '1', 'ddlareanameUrban': '-----Select Area----', 'txtAttributeValueUrban': '', 'txtImgUrban': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__EVENTTARGET': 'ddlDistrictUrban', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', '__ASYNCPOST': 'true'}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'type': 'data'}, {'method': 'POST', 'url': 'https://freesearchigrservice.maharashtra.gov.in/', 'payload': {'ScriptManager1': ('UpMain|btnSearchUrban',), 'ddlFromYearUrban': '2022', 'ddlDistrictUrban': '1', 'ddlareanameUrban': "Budhavar Peth ", 'txtAttributeValueUrban': 12, 'txtImgUrban': '', 'FS_PropertyNumber': '', 'FS_IGR_FLAG': '', '__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': '', '__VIEWSTATEGENERATOR': '', '__EVENTVALIDATION': '', '__ASYNCPOST': ('true',), 'btnSearchUrban': 'शोध / Search'}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Host': 'freesearchigrservice.maharashtra.gov.in', 'Origin': 'https://freesearchigrservice.maharashtra.gov.in', 'Referer': 'https://freesearchigrservice.maharashtra.gov.in/', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0', 'X-MicrosoftAjax': 'Delta=true', 'X-Requested-With': 'XMLHttpRequest'}, 'type': 'data'}]}
#getPage(job)

