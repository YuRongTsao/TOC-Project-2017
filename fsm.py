from transitions.extensions import GraphMachine
import telegram
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

API_TOKEN = '501071757:AAHMkTIfwFEJvH0UaRNAmZyQeH813XFqE7s'
bot = telegram.Bot(token=API_TOKEN)

productFile = json.load(open("product.json"))
cakes = productFile["生日蛋糕"]
puddings = productFile["布丁餅乾"]
breads = productFile["燒菓子"]
storeFile = json.load(open("store.json"))

#state1
global searchId
searchId = 0

#state3
GDriveJSON = 'google_sheet.json'
GSpreadSheet = 'operaOrder'
count = 1

global order
order = {
    'name' : "",
    'tel' : "",
    'address' : "",
    'total':0,
    'products' : [],
}

def calPrice(name,amount):
        price =0

        for cake in cakes:
            if cake["name"] == name:
                price = cake["price"]
                break
        if price == 0:
            for pudding in puddings:
                if pudding["name"] == name:
                    price = pudding["price"]
                    break
        if price == 0:
            for bread in breads:
                if bread["name"] == name:
                    price = bread["price"]
                    break

        price = int(price)

        return price*amount


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
    
    def is_going_to_state0(self, update):
        text = update.message.text
        return text.lower() == '/start'
    
    def is_going_to_state1(self, update):
        text = update.message.text
        if "產品" in text.lower():
            return True
        elif "1" in text.lower():
            return True

    def is_going_to_state1_2(self, update):
        text = update.message.text
        if "生日蛋糕" in text.lower():
            return True
        elif "1" in text.lower():
            return True

    def is_going_to_state1_2_3(self, update):  #cakes
        text = update.message.text
        global searchId

        for cake in cakes :
            if cake["name"] in text.lower():
                searchId = cake["id"]
                return True
            elif str(cake["id"]+1) in text.lower():
                searchId = cake["id"]
                return True

        if text.lower()!= "n":
            update.message.reply_text("品名輸入錯誤，請重新輸入")


    def is_going_to_state1_3(self, update):
        text = update.message.text
        if "布丁" in text.lower():
            return True
        elif "餅乾" in text.lower():
            return True
        elif "2" in text.lower():
            return True

    def is_going_to_state1_3_3(self, update):  #puddings
        text = update.message.text
        global searchId

        for pudding in puddings :
            if pudding["name"] in text.lower():
                searchId = pudding["id"]
                return True
            elif str(pudding["id"]+1) in text.lower():
                searchId = pudding["id"]
                return True
        if text.lower()!= "n":
            update.message.reply_text("品名輸入錯誤，請重新輸入")


    def is_going_to_state1_4(self, update):
        text = update.message.text
        if "菓子" in text.lower():
            return True
        elif "3" in text.lower():
            return True

    def is_going_to_state1_4_3(self, update):  #breads
        text = update.message.text
        global searchId

        for bread in breads :
            if bread["name"] in text.lower():
                searchId = bread["id"]
                return True
            elif str(bread["id"]+1) in text.lower():
                searchId = bread["id"]
                return True

        if text.lower()!= "n":
            update.message.reply_text("品名輸入錯誤，請重新輸入")


    def back_to_state1(self, update):
        text = update.message.text
        if "n" in text.lower():
            return True


    #state2
    def is_going_to_state2(self, update):
        text = update.message.text
        if "門市" in text.lower():
            return True
        elif "2" in text.lower():
            return True

    def back_to_state0(self, update):
        text = update.message.text
        if "n" in text.lower():
            return True

    #state3
    def is_going_to_state3(self, update):
        text = update.message.text
        if "訂單" in text.lower():
            return True
        elif "3" in text.lower():
            return True

    def is_going_to_state3_2(self, update):
        text = update.message.text
        global order

        if "done" in text.lower():
            return True

        #切文字
        text = text.lower()
        strlist =text.split('/')
        price = calPrice(strlist[0],int(strlist[1]))

        order["products"].append({
            'name':strlist[0],
            'amount':strlist[1],
            'price':price
            })
        print(order["products"][0]["price"])
        update.message.reply_text("感謝您訂購了 "+strlist[1]+" 個 "+strlist[0]+"\n還需要哪些產品嗎?")
        return False

    def is_going_to_state3_2_3(self, update):
        text = update.message.text
        global order 

        if order["name"] =="":
            order["name"] = text
            update.message.reply_text("請輸入電話號碼")
            return False
        elif order["tel"] =="":
            order["tel"] = text
            update.message.reply_text("請輸入地址")
            return False
        elif order["address"] =="":
            order["address"] = text
            return True
    def back_to_state3(self, update):
        text = update.message.text
        global order
        if 'n' in text.lower():
            order["name"] = ""
            order["tel"] = ""
            order["address"] = ""
            order["total"] = ""
            order["products"] = [] 
            return True

    def state3_2_3_back_to_state0(self, update):
        text = update.message.text
        global order

        if 'y' in text.lower():
            #google sheet
            try:
                scope = ['https://spreadsheets.google.com/feeds']
                key = SAC.from_json_keyfile_name(GDriveJSON, scope)
                gc = gspread.authorize(key)
                worksheet = gc.open(GSpreadSheet).sheet1
                print("連線成功")

                name = order["name"]
                tel = order["tel"]
                address = order["address"]
                total = order["total"]
                productData = ""
                for item in order["products"]:
                    productData += item["name"]+" / "+item["amount"]+"\n"

                worksheet.insert_row([name,tel,address,productData,total],2)
                update.message.reply_text("訂購成功！")

                #clean data
                order["name"] = ""
                order["tel"] = ""
                order["address"] = ""
                order["total"] = ""
                order["products"] == [] 

            except Exception as ex:
                print('無法連線Google試算表', ex)
                sys.exit(1)
           
            return True

    def on_enter_state0(self, update):
        update.message.reply_text("歡迎光臨歐培拉西點專賣店!")
        update.message.reply_text("您可以選擇 :\n1. 查詢產品 \n2. 查詢門市\n3. 下訂單")
        
    def on_exit_state0(self, update):
        print('Leaving state0')


    #state1
    def on_enter_state1(self, update):
        update.message.reply_text("歐培拉擁有以下產品種類 :\n1. 生日蛋糕\n2. 布丁/餅乾 \n3. 燒菓子 \n\n(輸入產品種類或編號獲得更多資訊)\n(若想回到主選單請輸入'n')")
    def on_enter_state1_2(self, update):
     
            cakeData = ""
            cakeCtr = 1

            for cake in cakes:
                cakeData += str(cakeCtr)+". "+cake["name"]+"\n"
                cakeCtr+=1 

            bot.send_message(chat_id=update.message.chat_id,text="想吃哪種生日蛋糕呢 ? \n"+cakeData+"\n(輸入品名或編號獲得更多資訊)\n(輸入'n'退出查詢)")
        
 

    def on_enter_state1_2_3(self, update):

        cake = cakes[searchId]

        image_name = cake["name"]
        file_name = "images/"+image_name+".jpg"

        update.message.reply_text("品名： "+cake["name"])
        bot.send_photo(chat_id=update.message.chat_id,photo=open(file_name,'rb'))
        bot.send_message(chat_id=update.message.chat_id,text="尺吋： "+cake["size"]+"\n價格： $"+str(cake["price"])+"\n\n主要成份：\n"+cake["ingrediens"]+"\n\n備註：\n"+cake["remarks"])
        


        self.go_back(update)

    def on_enter_state1_3(self, update):
        
            puddingData = ""
            puddingCtr = 1

            for pudding in puddings:
                puddingData += str(puddingCtr)+". "+pudding["name"]+"\n"
                puddingCtr+=1 

            bot.send_message(chat_id=update.message.chat_id,text="想吃哪種布丁或餅乾呢 ? \n"+puddingData+"\n(輸入品名或編號獲得更多資訊)\n(輸入'n'退出查詢)")
        

    def on_enter_state1_3_3(self, update):
        
        global searchId
        pudding = puddings[searchId]

        print("searchId: "+str(searchId))


        image_name = pudding["name"]
        file_name = "images/"+image_name+".jpg"

        update.message.reply_text("品名： "+pudding["name"])
        bot.send_photo(chat_id=update.message.chat_id,photo=open(file_name,'rb'))
        bot.send_message(chat_id=update.message.chat_id,text="價格： $"+str(pudding["price"])+"\n\n主要成份：\n"+pudding["ingrediens"]+"\n\n備註：\n"+pudding["remarks"])
        

        self.go_back(update)
    
    def on_enter_state1_4(self, update):
            breadData = ""
            breadCtr = 1

            for bread in breads:
                breadData += str(breadCtr)+". "+bread["name"]+"\n"
                breadCtr+=1 

            bot.send_message(chat_id=update.message.chat_id,text="想吃哪種燒菓子呢 ? \n"+breadData+"\n(輸入品名或編號獲得更多資訊)\n(輸入'n'退出查詢)")

    def on_enter_state1_4_3(self, update):
        bread = breads[searchId]

        image_name = bread["name"]
        file_name = "images/"+image_name+".jpg"

        update.message.reply_text("品名： "+bread["name"])
        bot.send_photo(chat_id=update.message.chat_id,photo=open(file_name,'rb'))
        bot.send_message(chat_id=update.message.chat_id,text="價格： $"+str(bread["price"])+"\n\n主要成份：\n"+bread["ingrediens"]+"\n\n備註：\n"+bread["remarks"])

        self.go_back(update)


    def on_enter_state2(self, update):
        stores = storeFile["stores"]
        data = ""
        for store in stores:
            data += "店名："+ store["name"]+"\n地址："+ store["address"]+"\n電話："+ store["tel"]+"\n營業時間："+ store["open"]+"\n\n"

        bot.send_message(chat_id=update.message.chat_id,text="門市資訊：\n\n"+"客服電話："+storeFile["tel"]+"\n\n客服信箱：\n"+storeFile["email"]+"\n\n分店資訊：\n"+ data+"\n\n(若想回到主選單請輸入'n')")
        bot.send_message(chat_id=update.message.chat_id,text='<a href="http://www.opera-1995.com.tw/products_list.aspx?classid=-1">More about Opera</a>',parse_mode=telegram.ParseMode.HTML)
    def on_enter_state3(self, update):
    
        data = ""

        for item in productFile:
            item = str(item)
            data += "\n"+item+":\n"
            productArr = productFile[item]
            for product in productArr:
                data += product["name"]+"..." +"$"+str(product["price"])+"\n"

        bot.send_message(chat_id=update.message.chat_id,text="產品目錄：\n"+data)
        update.message.reply_text("請輸入欲訂購品項\n格式 : 品名/數量\n(例:香蕉巧克力蛋糕/2)\n(一則訊息輸入一種品項)")        
        update.message.reply_text("(完成所有商品訂購後請輸入'done'進入下一階段)\n(若想回到主選單請輸入'n')")
 
    def on_exit_state3(self, update):
        print('Leaving state3')

    
    def on_enter_state3_2(self, update):
        update.message.reply_text("請輸入訂購人姓名")   

    def on_enter_state3_2_3(self, update):
        productData = ""
        total = 0

        global order
    
        for item in order["products"]:
            productData += item["name"]+" * "+item["amount"] + "/ $" + str(item["price"]) +"\n"
            total += item["price"]
        order["total"] = total
        bot.send_message(chat_id=update.message.chat_id,text="請確認訂購資訊:\n姓名 : "+ order["name"]+"\n電話 : "+order["tel"]+"\n地址 : "+order["address"]+"\n訂購商品 : \n"+productData+"\n小計： "+str(order["total"]))
        update.message.reply_text("若資料無誤請輸入'y'\n重新填寫請輸入'n'")

    




