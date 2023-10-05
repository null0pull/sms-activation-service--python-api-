import requests
from json import load
from phonenumbers import parse
from colorama import Fore
import traceback
from time import sleep
from threading import Thread


r = Fore.RED
g = Fore.GREEN
b = Fore.BLUE
y = Fore.YELLOW
c = Fore.CYAN

urlApiSMSAct = "https://sms-activation-service.com/stubs/handler_api?"
def sms_activation_api():
        file = open('settings_json.json');data = load(file);file.close();return data['sms_activation_service_api']

def return_country_for_5sim():
        file = open('settings_json.json');data = load(file);file.close();return data['sms_activation_service_country']   

def print_balance_for_sms_activation():
        try:
                balance = requests.get(f"{urlApiSMSAct}api_key={sms_activation_api()}&action=getBalance&lang=en")
                print(f"|==============SMS Activation Service Account Details=============|")
                print(f"{g}       Your Balance is : {balance.text} ${Fore.RESET}")
                print(f"|==================================================|")
                if balance.text == "0.00":
                        print(f'{r}Your SMS Activation Service Balance is Zero.')
                        return "ZERO"
        except Exception as e:
                print(f"{e}")

def getCountryAndOperators():
      request_url = f"{urlApiSMSAct}api_key={sms_activation_api()}&action=getCountryAndOperators&lang=en"
      countryAndOperators = requests.get(request_url)
      print("ID         Name            ")
      for line in (countryAndOperators.json()):
            if line.get("name") == return_country_for_5sim().capitalize():
                print(f'{Fore.LIGHTBLUE_EX}{line.get("id")}{Fore.RESET}          {line.get("name")}          ')
                print("Please Select Operator: ")
                operators_list = []
                index_ = 0
                for operator in line.get("operators"):
                      operators_list.append(operator)
                      price_details_req_url = f"{urlApiSMSAct}api_key={sms_activation_api()}&action=getServicesAndCost&country={line.get('id')}&operator={operator}&lang=en"
                      for json in requests.get(price_details_req_url).json():
                             if json.get("name").lower() == "amazon":
                                    price = json.get("price")
                      print(f"  [{index_}]: {operator}            Price: ${price}")
                      index_ += 1
                selected_operator = int(input("Enter your choice: "))
                country_id = line.get("id")
                return operators_list[selected_operator], country_id

# Phone Process
def sms_activation_phone_reseved_data(operator, country_id: str) -> list:
        phone_data_list = [] #phone_number_with_code #phone_number_without_code #order_id
        try:
                order_phone_url_api = f"{urlApiSMSAct}api_key={sms_activation_api()}&action=getNumber&service=am&operator={operator}&country={country_id}&lang=en"
                print(f"Operator is {y}{operator}{Fore.RESET} & Country ID is {y}{country_id}{Fore.RESET}")
                order_phone_response = requests.get(order_phone_url_api)
                order_phone_data = order_phone_response.text
                if order_phone_data == "NO_BALANCE":
                      print(f"{r}You can not buy numbers your balance is ZERO= 0${Fore.RESET}")
                      return "NO_BALANCE"
                elif order_phone_data == "NO_NUMBERS":
                      print(f"{r}No numbers with the given parameters, try later, or change operator, country.{Fore.RESET}")
                      return "NO_NUMBERS"
                elif "ACCESS_NUMBER" in order_phone_data:
                      order_phone_data_list = order_phone_data.split(":")[1:]
                      phone_number_with_code = order_phone_data_list[1].strip()
                      formatted_number = parse("+"+str(phone_number_with_code), None).national_number
                      phone_data_list.append(phone_number_with_code)
                      phone_data_list.append(str(formatted_number))
                      phone_data_list.append(order_phone_data_list[0].strip())
                      return phone_data_list
                elif order_phone_data == "ERROR_API":
                      print(f"{y}Please Wait While Processing to buy Number ... {Fore.RESET}")
                else:
                      return order_phone_data
        except:
              return traceback.format_exc()

def set_status_for_sms_activation_phone_reseved(status, order_id):
      '''
      STATUS CODES
      3 - Request another sms
      6 - Complete activation
      8 - Cancel order '''
      try:
            api_url = f"{urlApiSMSAct}api_key={sms_activation_api()}&action=setStatus&id={order_id}&status={status}&lang=en"
            response = requests.get(api_url)
            #print(f"{r}{response.text}{Fore.RESET}")
            def run():
                  sleep(180)
                  requests.get(api_url)
            
            if response.text == "CANNOT_BEFORE_2_MIN":
                  Thread(target=run, args=()).start()
      except:
            pass

def get_status_for_sms_activation_phone_reseved(order_id):
      api_url = f"{urlApiSMSAct}api_key={sms_activation_api()}&action=getStatus&id={order_id}&lang=en"
      response = requests.get(api_url)
      if response.text == "STATUS_WAIT_CODE":
            print("Waiting for SMS to arrive")
            return "STATUS_WAIT_CODE"
      elif response.text == "STATUS_CANCEL":
            return "STATUS_CANCEL"
      elif "STATUS_OK" in response.text:
            sms_code = (response.text).split(":")[1]
            return str(sms_code)
      else:
            return response.text
