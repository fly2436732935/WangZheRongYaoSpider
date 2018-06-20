import requests,json,pymysql,threading
from queue import Queue
#创建数据库连接
coon=pymysql.Connection(host='127.0.0.1',database="wangzherongyao",user="root",password="123456",charset="utf8")
#创建游标
cursor=coon.cursor()
#请求头很多只有这一条有用
headers = {
    #此处需要自己修改，因存在个人信息，所以下行连接内容不全！
'Referer':'http://h5.kohsocialapp.qq.com/app/yxzj/herov2/herodetail/?  后面自己抓包填在这',

}
#创建请求队列
idque=Queue()
#经过爬取得知只有105——200  501---504有英雄
for i in [x for x in range(103,200)]+[501,502,503,504]:
    idque.put(i)
def run(idque,headers,coon,cursor):
    while not idque.empty():
        #显示线程名，此行可以删掉
        print(threading.current_thread().name)
        #获取英雄id
        i=idque.get()
        data={
                #以下XXX换成自己抓包得到的数据
            'uin':'XXXXXXXX',
            'userId':'XXXXXXXXX',
            'token':'XXXXXXXXX',
            'heroId':i,
            'skillIdStr':str(i)+'00|'+str(i)+'10|'+str(i)+'20|'+str(i)+'30',
            'channelId':'16000'+str(i),

        }
        #创建请求超时标
        TIMEOUT_STATE=True
        while TIMEOUT_STATE:
            TIMEOUT_STATE=False
            try:
                response = requests.post('http://h5.kohsocialapp.qq.com/app/wzry/ajax/getPointInfoById', headers=headers,data=data,timeout=5)
            except TimeoutError:
                #如果超时继续请求
                TIMEOUT_STATE=True
        jsdata=json.loads(response.text)
        TIMEOUT_STATE=True
        try:

            jsdata["data"]["szDesc"]
            while TIMEOUT_STATE:
                TIMEOUT_STATE = False
                try:
                    #获取对应ID的英雄姓名，所以需要发起对其他显示姓名的连接请求
                    responseName = requests.post('http://h5.kohsocialapp.qq.com/app/wzry/ajax/getSkillInfoById', headers=headers,
                                     data=data,timeout=5)
                except TimeoutError:
                    TIMEOUT_STATE = True
            NameData = json.loads(responseName.text)
            print(NameData["data"][1]["szHeroTitle"])
            print(jsdata["data"]['iHeroId'])
            print(jsdata["data"]["szDesc"])
            print(jsdata["data"]["szUseTech"])
            print(jsdata["data"]["szFightTech"])
            print(jsdata["data"]["szGroupIdea"])
            print(jsdata["data"]["szIntroduction"])
            try:
                #线程锁
                lock.acquire()
                sql="insert into gonglue(name,HeroId,技能,使用技巧,对抗技巧,团战思路,加点方式) VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(NameData["data"][1]["szHeroTitle"],jsdata["data"]['iHeroId'],jsdata["data"]["szDesc"],jsdata["data"]["szUseTech"],jsdata["data"]["szFightTech"],jsdata["data"]["szGroupIdea"],jsdata["data"]["szIntroduction"])
                cursor.execute(sql)
                coon.commit()
                lock.release()
            except Exception as e:
                print(e)
                coon.rollback()
                lock.release()
        except:
            pass
th_list=[]
lock=threading.Lock()
for j in range(3):
    threadName="线程"+str(j)
    th=threading.Thread(target=run,args=(idque,headers,coon,cursor),name=threadName)
    th.start()
    th_list.append(th)
for thnum in th_list:
    thnum.join()
cursor.close()
coon.close()