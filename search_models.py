import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
import tkinter.font as tkFont
import threading
from selenium.webdriver.chrome.options import Options



def InfiniteScrolling(driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(4)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height



def Electroplanet_Web(driver,list_of_categories,data,Sharaf_DG):
        output_df = pd.DataFrame(columns=['Model','Electroplanet'])
        for cate in list_of_categories:
            df = data[data['Category'] == cate]
            # print(df)
            list_of_models = df["Models"]
            # We got the models of one category
            check_once = 0
            for models in list_of_models:
                if check_once == 0:
                    print("Model: ",models)
                    df_link = Sharaf_DG[Sharaf_DG['Category'] == cate]
                    keyword = models
                    # print(df_link["Links"])
                    dyno_link = df_link["Links"].iloc[0]
                    # print(dyno_link)
           
                    model_ids :list = []
                    model_links: list = []
                    driver.get(dyno_link)
                    # # Get scroll height
                    InfiniteScrolling(driver)
                    
                    # driver.get(dyno_link)
                    # time.sleep(5)
                    all_divs  = driver.find_elements(By.CSS_SELECTOR, ".product.name.product-item-name.product-name")
                    
                    # print(len(all_divs))
                    # Compare product name with model name 
                    for div in all_divs:
                        product_link = div.find_element(By.CSS_SELECTOR,".product-item-link").get_attribute('href')
                        model_id = div.text.replace(" ", "")
                        model_id = model_id.replace("\n", "")

                        print(model_id)
                        check_once = 1
                        # Save this model id in the list and use it later 
                        # 
                        model_ids.append(model_id)
                        model_links.append(product_link)



                total_models = len(model_ids)
                counter = 0
                location_model = 0
                for each_model in model_ids: 
                    if each_model.find(models) != -1:
                        output_df = output_df.append({
                                "Model":models,
                                "Electroplanet": "o",
                                "Product Link": model_links[location_model]
                        },ignore_index=True)
                        print(models,"Found")
                        break
                    counter+=1
                    location_model+=1

                if counter == total_models:
                    output_df = output_df.append({
                            "Model":models,
                            "Electroplanet": "x",
                            "Product Link": ""
      
                    },ignore_index=True)
                    print(models,"Not Found")
                
                # Compare here now

        with pd.ExcelWriter("output.xlsx",mode="a",if_sheet_exists='replace') as writer:
            output_df.to_excel(writer,sheet_name="Electroplanet")


def FetchProduct(model):


    url = "https://www.almanea.sa/api/search"

    payload = json.dumps({
    "word": f"{model}"
    })
    headers = {
    'Cookie': 'wp_ga4_customerGroup=NOT%20LOGGED%20IN; __Host-next-auth.csrf-token=a0c6833a1127baf2ffd76713967f090081b75661570a0efb97352bdbb28780fd%7C3a9d6435a226bb2beaaff4b1c1658b684d5e1bba0aafe4746605bee585e8b8f1; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.almanea.sa; handshake=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdG9yZSI6ImFyIiwic2Vzc2lvbklEIjoibnhKRnZDV3hQai1mR19yZ294eFd5bU1GclFDeGloTTQiLCJpYXQiOjE2OTQwODQzNjcsImV4cCI6MTY5NjY3NjM2N30.MCIpTx4Y0k7v6JNwnjl-vQi6aKtBgWdif6xanLLSX7E',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    final_response = response.json()

    total_products = final_response['totalProduct']
    

    if total_products == 1:   
        product_link = "https://www.almanea.sa/product/"+final_response['products'][0]['_source']['rewrite_url']
        product_name = final_response['products'][0]['_source']['name'][0]
        # print(product_name)
        # Compare this name with the model 
        # If it matches then do output o 
        # Else output x
        if product_name.find(model) != -1:
            # If model is found store the output with o and break the loop
            return ({
                    "Model":model,
                    "Almanea": "o",
                    "Product Link": product_link
                    
            })
        else:
             return ({
                    "Model":model,
                    "Almanea": "x",
                    "Product Link": ""
                    
            })
    elif total_products > 1:
        product_link = "https://www.almanea.sa/product/"+final_response['products'][0]['_source']['rewrite_url']
        product_name = "https://www.almanea.sa/product/"+final_response['products'][0]['_source']['name']
        # Compare this name with the model 
        # If it matches then do output o 
        # Else output x
        if product_name.find(model) != -1:
            # If model is found store the output with o and break the loop
            return ({
                    "Model":model,
                    "Almanea": "o",
                    "Product Link": product_link
                    
            })
        else:
             return ({
                    "Model":model,
                    "Almanea": "x",
                    "Product Link": ""
                    
            })
            

    else:
        return ({
                    "Model":model,
                    "Almanea": "x",
                    "Product Link": ""
                    
        })
    


def Biougnach_Web(list_of_categories,data):
        output_df = pd.DataFrame(columns=['Model','Biougnach'])
        for cate in list_of_categories:
            df = data[data['Category'] == cate]
            # print(df)
            list_of_models = df["Models"]
            
            for models in list_of_models:
                 
            
                output_df = output_df.append(FetchProduct(models),ignore_index=True)
               

        with pd.ExcelWriter("output.xlsx",mode="a",if_sheet_exists='replace') as writer:
            output_df.to_excel(writer,sheet_name="Biougnach")


def FetchProduct(model):


    url =f"https://www.biougnach.ma/webapigw/api/v1/c/Catalog/FilterItemsAsync/?FullTextSearch={model}"

    payload = json.dumps({})
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    final_response = response.json()

    total_products = final_response['count']
    

    if total_products == 1:   
        
        product_name = final_response['data'][0]['productCode']
        # print(product_name)
        # Compare this name with the model 
        # If it matches then do output o 
        # Else output x
        if product_name.find(model) != -1:
            # If model is found store the output with o and break the loop
            return ({
                    "Model":model,
                    "Biougnach": "o"
                    
                    
            })
        else:
             return ({
                    "Model":model,
                    "Biougnach": "x",
                    
                    
            })
    elif total_products > 1:
   
        product_name = final_response['data'][0]['productCode']
        # Compare this name with the model 
        # If it matches then do output o 
        # Else output x
        if product_name.find(model) != -1:
            # If model is found store the output with o and break the loop
            return ({
                    "Model":model,
                    "Biougnach": "o"
                   
                    
            })
        else:
             return ({
                    "Model":model,
                    "Biougnach": "x"
                    
                    
            })
            

    else:
        return ({
                    "Model":model,
                    "Biougnach": "x"
                 
                    
        })
    
def Run_Biougnach():




    # 0------------------------------------------------------------------------------
    # df_sharaf_dg_categories_keywords = pd.read_excel("search_keywords.xlsx")
    # df_sharaf_dg_brands = pd.read_excel("input.xlsx")
    data = pd.read_excel("models.xlsx",sheet_name="Models")
    
    # Biougnach = pd.read_excel("models.xlsx",sheet_name="Biougnach")
    

    list_of_categories = data["Category"].unique()

  
    Biougnach_Web(list_of_categories,data)
   
    
def Run_Electroplanet():

    data = pd.read_excel("models.xlsx",sheet_name="Models")
    Electroplanet = pd.read_excel("models.xlsx",sheet_name="Electroplanet")

    driver = webdriver.Chrome("C:\Program Files\chromedriver.exe")
    list_of_categories = data["Category"].unique()

    Electroplanet_Web(driver,list_of_categories,data,Electroplanet)

def Electroplanet_WebTop20(driver,list_of_categories,data,Sharaf_DG):
        output_df = pd.DataFrame(columns=['Model','ElectroplanetTop20'])
        for cate in list_of_categories:
            df = data[data['Category'] == cate]
            # print(df)
            list_of_models = df["Models"]
            # We got the models of one category
            check_once = 0
            for models in list_of_models:
                if check_once == 0:
                    print("Model: ",models)
                    df_link = Sharaf_DG[Sharaf_DG['Category'] == cate]
                    keyword = models
                    # print(df_link["Links"])
                    dyno_link = df_link["Links"].iloc[0]
                    # print(dyno_link)
           
                    model_ids :list = []
                    driver.get(dyno_link)
                    # # Get scroll height
                    InfiniteScrolling(driver)
                    
                    # driver.get(dyno_link)
                    # time.sleep(5)
                    all_divs  = driver.find_elements(By.CSS_SELECTOR, ".product.name.product-item-name.product-name")
                    # print(len(all_divs))
                    # Compare product name with model name 
                    count = 0 
                    for div in all_divs:
                        

                        model_id = div.text.replace(" ", "")
                        model_id = model_id.replace("\n", "")

                        
                        print(model_id)
                        check_once = 1
                        # Save this model id in the list and use it later 
                        # 
                        model_ids.append(model_id)
                        count+=1

                        if count >= 20:
                            break



                total_models = len(model_ids)
                counter = 0
                for each_model in model_ids: 
                    if each_model.find(models) != -1:
                        output_df = output_df.append({
                                "Model":models,
                                "Electroplanet": "o",
                        },ignore_index=True)
                        print(models,"Found")
                        break
                    counter+=1

                if counter == total_models:
                    output_df = output_df.append({
                            "Model":models,
                            "Electroplanet": "x",
      
                    },ignore_index=True)
                    print(models,"Not Found")
                
                # Compare here now

        with pd.ExcelWriter("output.xlsx",mode="a",if_sheet_exists='replace') as writer:
            output_df.to_excel(writer,sheet_name="Electroplanet")

def Run_ElectroplanetTop20():

    data = pd.read_excel("models.xlsx",sheet_name="Models")
    Electroplanet = pd.read_excel("models.xlsx",sheet_name="ElectroplanetTop20")

    driver = webdriver.Chrome("C:\Program Files\chromedriver.exe")
    list_of_categories = data["Category"].unique()

    Electroplanet_WebTop20(driver,list_of_categories,data,Electroplanet)
 

# NVO - Paused
def Electroplanet_WebNVO(driver,list_of_categories,data,Sharaf_DG):
        output_df = pd.DataFrame(columns=['Model','Electroplanet'])
        for cate in list_of_categories:
            df = data[data['Category'] == cate]
            # print(df)
            list_of_models = df["Models"]
            # We got the models of one category
            check_once = 0
            for models in list_of_models:
                if check_once == 0:
                    print("Model: ",models)
                    df_link = Sharaf_DG[Sharaf_DG['Category'] == cate]
                    keyword = models
                    # print(df_link["Links"])
                    dyno_link = df_link["Links"].iloc[0]
                    # print(dyno_link)
           
                    model_ids :list = []
                    driver.get(dyno_link)
                    # # Get scroll height
                    InfiniteScrolling(driver)
                    
                    # driver.get(dyno_link)
                    # time.sleep(5)
                    all_divs  = driver.find_elements(By.CSS_SELECTOR, ".product.name.product-item-name.product-name")
                    # print(len(all_divs))
                    # Compare product name with model name 
                    for div in all_divs:
                        model_id = div.text.replace(" ", "")
                        model_id = model_id.replace("\n", "")
                        if model_id.find("OLED") != -1:
                            pass
                        else:

                            print(model_id)

                            model_ids.append(model_id)
                        check_once = 1



                total_models = len(model_ids)

                counter = 0
                foundModels = 0
                
                for each_model in model_ids: 
                    if each_model.find(models) != -1:
                        foundModels+=1
                        output_df = output_df.append({
                                "Model":models,
                                "Electroplanet": "o",
                        },ignore_index=True)
                        print(models,"Found")
                        break
                    counter+=1

                if counter == total_models:
                  
                  
                    output_df = output_df.append({
                            "Model":models,
                            "Electroplanet": "x",
      
                    },ignore_index=True)
                    print(models,"Not Found")
                
                # Compare here now

        with pd.ExcelWriter("output.xlsx",mode="a",if_sheet_exists='replace') as writer:
            output_df.to_excel(writer,sheet_name="Electroplanet")

def Run_ElectroplanetNVO():

    data = pd.read_excel("models.xlsx",sheet_name="Models")
    Electroplanet = pd.read_excel("models.xlsx",sheet_name="Electroplanet")

    driver = webdriver.Chrome("C:\Program Files\chromedriver.exe")
    list_of_categories = data["Category"].unique()

    Electroplanet_WebNVO(driver,list_of_categories,data,Electroplanet)
    

        

# Main App 
class App:

    def __init__(self, root):
        #setting title
        root.title("Morocco Model Check")
        ft = tkFont.Font(family='Arial Narrow',size=13)
        #setting window size
        width=640
        height=480
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root.configure(bg='black')

        ClickBtnLabel=tk.Label(root)
       
      
        
        ClickBtnLabel["font"] = ft
        
        ClickBtnLabel["justify"] = "center"
        ClickBtnLabel["text"] = "Morocco Model Check"
        ClickBtnLabel["bg"] = "black"
        ClickBtnLabel["fg"] = "white"
        ClickBtnLabel.place(x=120,y=190,width=150,height=70)
    

        
        Lulu=tk.Button(root)
        Lulu["anchor"] = "center"
        Lulu["bg"] = "#009841"
        Lulu["borderwidth"] = "0px"
        
        Lulu["font"] = ft
        Lulu["fg"] = "#ffffff"
        Lulu["justify"] = "center"
        Lulu["text"] = "START"
        Lulu["relief"] = "raised"
        Lulu.place(x=375,y=190,width=150,height=70)
        Lulu["command"] = self.start_func




  

    def ClickRun(self):

        running_actions = [
            Run_Biougnach,
            Run_Electroplanet         
    
        ]

        thread_list = [threading.Thread(target=func) for func in running_actions]

        # start all the threads
        for thread in thread_list:
            thread.start()

        # wait for all the threads to complete
        for thread in thread_list:
            thread.join()
    
    def start_func(self):
        thread = threading.Thread(target=self.ClickRun)
        thread.start()

    
        

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

