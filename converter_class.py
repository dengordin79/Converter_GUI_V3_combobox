from tkinter import *
import datetime, os, sys, requests, json
from tkinter import filedialog
from tkinter.ttk import Combobox


class Converter(Tk):
    API_KEY='3e623231f9cd13d498430eb138163340'
    SERVICE_URL=f'http://api.exchangeratesapi.io/v1/latest?access_key={API_KEY}'
    PROJECT_ROOT_PATH=os.path.dirname(__file__)
    SAVED_RATES_FOLDER=os.path.join(PROJECT_ROOT_PATH,'rates_files')
    CSV_FILE=os.path.join(PROJECT_ROOT_PATH,'exchange_record_log.csv')
    RATES_FILES_FILTER=(('rates files','*.json'),('log file','*.csv'))
    LOG_FILES_FOLDER=os.path.join(PROJECT_ROOT_PATH,'log_files')
    LOG_FILE_PATH=os.path.join(LOG_FILES_FOLDER,'conversion_history.csv')
    LOG_FILE_HEADERS=('Date_time','Ammount to convert','Currency code (from)','Currency code (to)','Result')
    CURRENCY_SHORT_LIST=['USD','EUR','JPY','GBP','CNH','ILS','RUB','UAH','BYN','KZT']
    def __init__(self):
        super().__init__()
        self.grid_columnconfigure(0,weight=0)
        self.grid_columnconfigure(1,weight=1)
        self.controls_frame=Frame()
        self.result_frame=Frame()
        self.info_frame=Frame()
        self.controls_frame.grid(column=0,row=0,rowspan=2)
        self.result_frame.grid(column=1,row=0)
        self.info_frame.grid(column=1,row=1)
        self.rates={}
        #control frame
        Button(self.controls_frame,text='Get rates online',command=self.get_rates_online).pack()
        Button(self.controls_frame,text='Get rates from file',command=self.get_rates_offline).pack()
        Button(self.controls_frame,text='Convert',command=self.convert).pack()
        Button(self.controls_frame,text='Display convertion history',command=self.get_conversion_history).pack()
        #result frame
        Label(self.result_frame,text='Currency from:',anchor=W).grid(column=0,row=0,sticky=(W,E))
        Label(self.result_frame,text='Currency to:',anchor=W).grid(column=0,row=1,sticky=(W,E))
        Label(self.result_frame,text='Amount:',anchor=W).grid(column=0,row=2,sticky=(W,E))
        Label(self.result_frame,text='Converted:',anchor=W).grid(column=0,row=3,sticky=(W,E))
       #result labels
        self.select_from_var=StringVar()        
        self.select_from_var.set('Select')        
        self.curr_from_entry=Combobox(
            self.result_frame,
            textvariable=self.select_from_var,
            values=Converter.CURRENCY_SHORT_LIST)
        self.curr_from_entry.bind("<<ComboboxSelected>>",self.combo_select)
        self.curr_from_entry.grid(column=1,row=0)
        self.select_to_var=StringVar()        
        self.select_to_var.set('Select')
        self.curr_to_entry=Combobox(
            self.result_frame,
            textvariable=self.select_to_var,
            values=Converter.CURRENCY_SHORT_LIST)
        self.curr_to_entry.bind("<<ComboboxSelected>>",self.combo_select)
        self.curr_to_entry.grid(column=1,row=1)
        self.amount=Entry(self.result_frame)
        self.amount.grid(column=1,row=2)
        self.result_label=Label(self.result_frame)
        self.result_label.grid(column=1,row=3)
        #info frame
        self.get_rates_label=Label(self.info_frame,text='Please, get rates!',anchor=N,fg='red')
        self.get_rates_label.grid(row=0)
        self.mainloop()
    
    def get_rates_online(self):
        response=requests.get(self.SERVICE_URL)
        rates_dict=response.json()
        code=response.status_code
        print(f'HTTP response code: {code}')
        date=rates_dict.get('date')
        self.time_stamp=rates_dict.get('timestamp')
        file_name=f'rates_{date.replace("-","_")}__{self.time_stamp}.json'
        with open(os.path.join(self.SAVED_RATES_FOLDER,file_name),'w') as f:
            json.dump(rates_dict, f, indent=4)
            pass
        self.rates=rates_dict
        self.get_rates_label.config(text=f'Rates online {self.rates.get("date")}',fg='green')
        pass
    def get_rates_offline(self):
        rate_file=filedialog.askopenfile(
            initialdir=self.SAVED_RATES_FOLDER,
            filetypes=self.RATES_FILES_FILTER)
        self.rates=json.load(rate_file)
        self.get_rates_label.config(text=f'Rates offline {self.rates.get("date")}',fg='green')
        pass
    def combo_select(self,e):
        self.currency_from=self.curr_from_entry.get()
        self.currency_to=self.curr_to_entry.get()
        
        pass
    def convert(self):
        if len(self.rates)==0:
            print("No rates data found!!!")
            return
        
        ammount_to_convert=self.amount.get()
        ammount_to_convert=float(ammount_to_convert)
        rate_from=self.rates['rates'][self.currency_from]
        rate_to=self.rates['rates'][self.currency_to]
        res=(rate_to/rate_from)*ammount_to_convert
        print(f'{datetime.datetime.now()}\tConverting {ammount_to_convert} {self.currency_from} to {self.currency_to}, result: {res:.2f} {self.currency_to}')
        headers='datetime, ammount to convert, currency from, currency to, result\n'
        record_of_convert=f'{datetime.datetime.now()},{ammount_to_convert}, {self.currency_from},{self.currency_to}, {res:.2f}'
        print(self.CSV_FILE)
        with open(self.CSV_FILE,'w') as f:
            f.write(headers)
            f.write(record_of_convert)
            pass
        self.result_label.config(text=f'{res:.2f}{self.currency_to}')   
        conversion_data=datetime.datetime.now().strftime("%m/%d/%Y__%H:%M:%S"),str(ammount_to_convert),str(self.currency_from),str(self.currency_to),str(res)
        self._update_log_file(conversion_data)
        pass
    def _update_log_file(self,current_conversion):
        if os.path.exists(self.LOG_FILE_PATH):
            with open(self.LOG_FILE_PATH) as f: headers_from_file=f.readline()
            if headers_from_file !=",".join(self.LOG_FILE_HEADERS)+'\n':
                with open(self.LOG_FILE_PATH,'w') as f: f.write(",".join(self.LOG_FILE_HEADERS)+'\n')
                pass
            pass
        else:
            with open(self.LOG_FILE_PATH,'w') as f: f.write(",".join(self.LOG_FILE_HEADERS)+'\n')
            pass
        pass
        with open(self.LOG_FILE_PATH,'a') as f: f.write(",".join(current_conversion)+'\n')
        pass
    def get_conversion_history(self):
        TABLE_ROW_FORMAT='\u007c{:20} \u007c{:20} \u007c{:20} \u007c{:20} \u007c{:20} \u007c\n'
        result_string=''
        result_string+=106*'\u2015'+'\n'
        with open(self.LOG_FILE_PATH) as f:
            file_data=f.readlines()
            pass
        result_string+=TABLE_ROW_FORMAT.format(*(file_data[0].strip().split(',')))
        result_string+=106*'\u2015'+'\n'
        for i in range(1,len(file_data)):
            result_string+=TABLE_ROW_FORMAT.format(*(file_data[i].strip().split(',')))
        result_string+=106*'\u2015'
        print(result_string)
        history_win=Toplevel()
        history_win.title('Conversation history')
        history=Text(history_win,width=112)
        history.pack(expand=True,fill=BOTH)
        history.insert('1.0',result_string)
        
        
        
        
        pass
    pass

if __name__=='__main__':
    Converter()