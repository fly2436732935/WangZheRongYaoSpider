import requests,json,pymysql

coon=pymysql.Connection(host='127.0.0.1',database="wangzherongyao",user="root",password="123456",charset="utf8")
cursor=coon.cursor()
headers = {
    #此处需要自己修改，因存在个人信息，所以下行连接内容不全！
'Referer':'http://h5.kohsocialapp.qq.com/app/yxzj/herov2/herodetail/?  后面自己抓包填在这',

}
#经过爬取得知只有105——200  501---504有英雄
for i in [x for x in range(103,200)]+[501,502,503,504]:
    data={
        #以下XXX换成自己抓包得到的数据
    'uin':'XXXXXXXX',
    'userId':'XXXXXXXXX',
    'token':'XXXXXXXXX',
    'heroId':i,
    'skillIdStr':str(i)+'00|'+str(i)+'10|'+str(i)+'20|'+str(i)+'30',
    'channelId':'16000'+str(i),
    }

    response = requests.post('http://h5.kohsocialapp.qq.com/app/wzry/ajax/getPointInfoById', headers=headers,data=data)
    jsdata=json.loads(response.text)

    try:
        #此行为了让部分没有英雄的id响应抓到之后让程序报错，来跳过此次爬取
        jsdata["data"]["szDesc"]
        responseName = requests.post('http://h5.kohsocialapp.qq.com/app/wzry/ajax/getSkillInfoById', headers=headers,
                                 data=data)
        NameData = json.loads(responseName.text)
        print(NameData["data"][1]["szHeroTitle"])
        print(jsdata["data"]['iHeroId'])
        print(jsdata["data"]["szDesc"])
        print(jsdata["data"]["szUseTech"])
        print(jsdata["data"]["szFightTech"])
        print(jsdata["data"]["szGroupIdea"])
        print(jsdata["data"]["szIntroduction"])
        try:

            #下面根据自己数据库进行修改
            sql="insert into gonglue_copy(name,HeroId,技能,使用技巧,对抗技巧,团战思路,加点方式) VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(NameData["data"][1]["szHeroTitle"],jsdata["data"]['iHeroId'],jsdata["data"]["szDesc"],jsdata["data"]["szUseTech"],jsdata["data"]["szFightTech"],jsdata["data"]["szGroupIdea"],jsdata["data"]["szIntroduction"])
            cursor.execute(sql)
            coon.commit()
        except Exception as e:
            print(e)
            coon.rollback()
    except:
        pass

cursor.close()
coon.close()