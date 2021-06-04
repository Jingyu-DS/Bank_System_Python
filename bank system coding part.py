import datetime
from abc import *
from dateutil.relativedelta import relativedelta


#create the function outside the class to help check the condition whether the customer is about to overdraw
def check_overdraw(customer_ins, act_type, amount):
    if act_type == 'checking':
        return amount+CheckingAccount.WITHDRAW_FEE > customer_ins.checking_account.balance
    elif act_type == 'saving':
        return amount+SavingAccount.WITHDRAW_FEE > customer_ins.saving_account.balance
    else:
        return amount+ReserveAccount.WITHDRAW_FEE > customer_ins.reserve_account.balance

#create the function outside the class the help check whether the customer will do the overdraw or not 
def do_overdraw(customer_ins, act_type, amount):
    line = 'you will be overdrawing from you account, overdraft fee is 40 dollars, enter yes to continue'
    return True if input(line).lower().startswith('y') else False
        

#This is the abtract class to indicate the basic operations of a bank system
#by using the abstract method, the operations cannot be competed without the subclasses
class Operation(ABC):
    def __init__(self,name):
        self.holder=name

    @abstractmethod
    def deposit(self,amount):
        raise NotImplementedError('Subclass must implement abstract mothod')
    
    @abstractmethod
    def withdraw(self,amount):
        raise NotImplementedError('Subclass must implement abstract mothod')

    @abstractmethod
    def transfer(self,amount):
        raise NotImplementedError('Subclass must implement abstract mothod')

#This class is to show the basic funtionality of an account     
class Account:

    OVER_DRAW_FEE = 40
    
    def __init__(self,balance=0):
        self.balance=balance

    def withdraw(self,amount):
        self.balance -= amount
        return amount

    def deposit(self, amount):
        self.balance += amount
        return self.balance
    
#Several subclasses below are the specific account types with different withdraw fees as class instances 
class CheckingAccount(Account):

    WITHDRAW_FEE = 1
 
    def __init__(self,balance):
        super().__init__(balance)

    def withdraw(self,amount):
        self.balance -= (amount + CheckingAccount.WITHDRAW_FEE)
        return amount


class SavingAccount(Account):

    WITHDRAW_FEE = 5

    def __init__(self,balance):
        super().__init__(balance)

    def withdraw(self,amount):
        self.balance -= (amount + SavingAccount.WITHDRAW_FEE)
        return amount
    

class ReserveAccount(Account):

    WITHDRAW_FEE = 10
    INTEREST = 0.0001

    def __init__(self,balance):
        super().__init__(balance)

    def withdraw(self,amount):
        self.balance -= (amount + ReserveAccount.WITHDRAW_FEE)
        return amount
    
    def pay_interest(self):
        self.balance += self.balance * ReserveAccount.INTEREST

#this class is about what the customer can do in the bank system 
class Customer:
    '''
    >>> Jingyu=Customer('jingyu','09/26/2000','jkw5688',876)
    >>> Jingyu.openAccount(50)
    'you cannot open an account without a minimum deposit of 100'
    >>> Jingyu.openAccount(500)
    'successfully opened a checking account, thank you'
    >>> Michael=Customer('yuhan','04/01/2005','666666',789)
    >>> Michael.openAccount(1000)
    'you are not old enough'
    >>> Jingyu.openAccount(200,'saving')
    'successfully opened a saving account, thank you'
    >>> Jingyu.apply_loan(200)
    'the loan has been approved to jingyu, new saving balance: 400'
    >>> Jingyu.apply_credit_card
    'you have your credit card now'
    >>> Jingyu.withdraw('saving',50)
    'withdrew 50, saving account balance: 345'
    >>> Jingyu.withdraw('checking',600)
    you will be overdrawing from you account, overdraft fee is 40 dollars, enter yes to continueyes
    'withdrew 600, checking account balance: -141'
    '''
    #use the special method to show the users what the class can do
    #use the property method to increase the functionality 
    @property
    def __doc__(self):
        return '''Customer class is used to create customer instances for our bank.
                Customer.openAccount(amount, account_Type) opens an account for out customer.
                Customer.apply_credit_card() gives the customer a credit card if his/her credit ranking is high enough
                Customer.withdraw helps the customer to withdraw money
                Customer.apply_loan(loan) helps the customer get a loan if his/her balance and credit ranking is high enough
                
                '''

    def __init__(self,name,birthdate,authority_id,credit_rating):
        month, day, year = birthdate.split('/')
        today = datetime.date.today()
        if int(month) < today.month:
            self.age = today.year - int(year) -1
        elif int(month) == today.month:
            if int(day) < day:
                self.age = today.year - int(year) - 1
            else:
                self.age = today.year - int(year)
        else:            
            self.age = datetime.date.today().year - int(year)
        self.holder=name
        self.birthdate=birthdate
        #restrict the access to the id and credit rating to aviod being modified unintentioanlly 
        self.__identity=authority_id
        self.__rating=credit_rating
        self.credit_card=False
        self.start_date = datetime.date.today()
        self.info = {'name':self.holder, 'birthdate':self.birthdate, 'id':self.__identity, 'credit':self.__rating, 'age':self.age}
        
    #use a method to get the credit rating 
    @property
    def get_credit(self):
        return self.__rating

    #use a method to get the id 
    @property
    def get_id(self):
        return self.__identity
    
    #help the customer open the type of account they would like to open
    def openAccount(self,amount,account_type='checking'):            
        if amount<100:
            return 'you cannot open an account without a minimum deposit of 100'
        if self.age<18:
            return 'you are not old enough'
        else:
            if account_type == 'checking':
                self.checking_account = CheckingAccount(amount)
            elif account_type == 'saving':
                self.saving_account = SavingAccount(amount)
            elif account_type == 'reserve':
                self.reserve_account = ReserveAccount(amount)
            else:
                return 'you entered an invalid account type'
        return f'successfully opened a {account_type} account, thank you'

    #help the customer withdraw money
    #use the check_overdraw and do_overdraw function outside the class to simplify the class 
    def withdraw(self, act_type, amount):
        act_type = act_type.lower()
        if not act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid account type, choice from checking, saving or reserve'
        if act_type=='checking':
            # check if user have checking_account
            if hasattr(self, 'checking_account'):
                # check if user is over drawing
                if check_overdraw(self, act_type, amount):
                    # ask if user want to overdraw
                    if do_overdraw(self, act_type, amount):
                        self.checking_account.withdraw(amount+CheckingAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, checking account balance: {self.checking_account.balance}'
                    # user does not want to overdraw
                    else:
                        return f'balance: {self.checking_account.balance}'
                # user is not over drawing
                else:
                    self.checking_account.withdraw(amount)
                    return f'withdrew {amount}, checking account balance: {self.checking_account.balance}'
            # user does not have checking account
            else:
                return f'{self.holder} does not have a {act_type} account'
        # same structure as withdrawing from checking account
        # first check that user have saving account
        # then check if over drawing
        # ask if user want to over draw
        elif act_type=='saving':
            if hasattr(self,'saving_account'):
                if check_overdraw(self, act_type, amount):
                    if do_overdraw(self, act_type, amount):
                        self.saving_account.withdraw(amount+SavingAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, saving account balance: {self.saving_account.balance}'
                    else:
                        return f'balance: {self.saving_account.balance}'
                else:
                    self.saving_account.withdraw(amount)
                    return f'withdrew {amount}, saving account balance: {self.saving_account.balance}'
            else:
                return f'{self.holder} does not have a {act_type} account'
        # same structure as withdrawing from checking account
        else:
            if hasattr(self,'reserve_account'):
                if check_overdraw(self, act_type, amount):
                    if do_overdraw(self, act_type, amount):
                        self.reserve_account.withdraw(amount+ReserveAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, reserve account balance: {self.reserve_account.balance}'
                    else:
                        return f'balance: {self.reserve_account.balance}'
                else:
                    self.reserve_account.withdraw(amount)
                    return f'withdrew {amount}, checking account balance: {self.reserve_account.balance}'
            else:
                return f'{self.holder} does not have a {act_type} account'
            
    #help the customer apply loan
    #the customer needs more than 500 credit rating and a saving account to get the loan which should be less than 1000.       
    def apply_loan(self,loan):
        if hasattr(self, 'saving_account'):
            # user need to have higher at least 500, and loan amount is less than 1000
            if self.__rating>=500 and loan<=1000:
                self.saving_account.balance+=loan
                return f'the loan has been approved to {self.holder}, new saving balance: {self.saving_account.balance}'
            else:
                return 'your loan has not been approved bacuase your credit rating is less than 500'
        else:
            return 'you have to open an saving account first'

    #help the customer apply for a credit card
    #the customer needs to have more than 200 credit rating and more than $200 balance to get the card
    @property
    def apply_credit_card(self):
        if hasattr(self, 'saving_account'):
            if self.__rating>=200 and self.saving_account.balance>200:
                self.credit_card=True
                return 'you have your credit card now'
            else:
                return 'you cannot have your credit card'
        else:
            return 'you have to open an saving account first'

    @property
    def pay_interest(self):
        if not hasattr(self, 'reserve_account'):
            return f'{self.holder} does not have a reserve account'
        # interests are paid on a monthly basis, and need to be manually collected
        if self.start_date + relativedelta(months=1) <= datetime.date.today():
            interest = self.reserve_account.balance * ReserveAccount.INTEREST_RATE
            self.reserve_account.balance += interest
            self.start_date = datetime.date.today()
            return f'collected ${interest} interest, new reserve account balance: {self.reserve_account.balance}'
        else:
            return f'next day to collect interest is {self.start_date + relativedelta(months=1)}, please be patient'


#This class is about the Manager     
class Manager(Operation):
    '''
    >>> Ivy=Manager('ivy','5678')
    >>> Henry=Customer('henry','05/27/2000','bbh1234',567)
    >>> Ivy.approve_loan(Henry,200)
    'saving account needs to be opened to apply for loan'
    >>> Henry.openAccount(600)
    'successfully open the account, thank you'
    >>> Ivy.approve_loan(Henry,200)
    'saving account needs to be opened to apply for loan'
    >>> Henry.openAccount(600,'saving')
    'successfully opened a saving account, thank you'
    >>> Ivy.approve_loan(Henry,200)
    'the loan has been approved to henry, new saving balance: 800'
    >>> Ivy.withdraw(Henry,'saving',100)
    'withdrew 100, saving account balance: 695'
    >>> Jingyu.openAccount(500)
    'successfully opened a checking account, thank you'
    >>> Ivy.transfer(Henry,'saving',Jingyu,'checking',200)
    "successfully transfered 200 from henry's saving account to jingyu's checking account"
    >>> Ivy.check_cust_info(Henry,'name')
    'henry'
    >>> Ivy.delete_account(Jingyu)
    "successfully deleted jingyu's account"
    '''
    #use the special method to indicate what the class can do 
    @property
    def __doc__(self):
        return '''Manager class is used to create manager instances for our bank.
                Manager.deposit(self,customer_ins, act_type, amount) helps the manager to make the deposit for the customer.
                Manager.withdraw(self,customer_ins, act_type, amount) helps the manager to withdraw the money for the customer
                Manager.transfer(self,from_customer_ins, from_act_type, to_customer_ins, to_act_type, amount) helps the manager to make tranfer
                Manager.check_cust_info(self, customer_ins, info_type) helps the manager to check the customer's information
                Manager.delete_account(self, customer_ins) helps the manager to delete the customer's account
                Manager.approve_loan(self,customer_ins,loan) helps the manager to approve the loan
                '''

    def __init__(self,name,manager_id):
        self.holder=name
        self.worker_id=manager_id
        
   #the manager can help the customer to make the deposit 
    def deposit(self,customer_ins, act_type, amount):
        act_type = act_type.lower()
        if not isinstance(customer_ins, Customer):
            return 'you entered incorrect customer, try again'
        if not act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid account type, choice from checking, saving or reserve'
        if act_type == 'checking':
            if not hasattr(customer_ins, 'checking_account'):
                return 'checking account needs to be opened before depositing'
            return customer_ins.checking_account.deposit(amount)
        elif act_type == 'saving':
            if not hasattr(customer_ins, 'saving_account'):
                return 'saving account needs to be opened before depositing'
            return customer_ins.saving_account.deposit(amount)
        else:
            if not hasattr(customer_ins, 'reserve_account'):
                return 'reserve account needs to be opened before depositing'
            return customer_ins.reserve_account.deposit(amount)
 
    #the manager can help the customer withdraw the money 
    def withdraw(self,customer_ins, act_type, amount):
        act_type = act_type.lower()
        if not isinstance(customer_ins, Customer):
            return 'you entered incorrect customer, try again'
        if not act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid account type, choice from checking, saving or reserve'
        # same structure as withdraw method from Customer class
        # first check that user have checking account
        # then check if over drawing
        # then ask if user want to overdraw
        if act_type=='checking':
            if hasattr(self,'checking_account'):
                if check_overdraw(customer_ins, act_type, amount):
                    if do_overdraw(customer_ins, act_type, amount):
                        customer_ins.checking_account.withdraw(amount+CheckingAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, checking account balance: {customer_ins.checking_account.balance}'
                    else:
                        return f'balance: {customer_ins.checking_account.balance}'
                else:
                    customer_ins.checking_account.withdraw(amount)
                    return f'withdrew {amount}, checking account balance: {customer_ins.checking_account.balance}'
            else:
                return f'{customer_ins.holder} does not have a {act_type} account'
        # same structre as above 
        elif act_type=='saving':
            if hasattr(self,'saving_account'):
                if check_overdraw(customer_ins, act_type, amount):
                    if do_overdraw(customer_ins, act_type, amount):
                        customer_ins.saving_account.withdraw(amount+SavingAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, saving account balance: {customer_ins.saving_account.balance}'
                    else:
                        return f'balance: {customer_ins.saving_account.balance}'
                else:
                    customer_ins.saving_account.withdraw(amount)
                    return f'withdrew {amount}, saving account balance: {customer_ins.saving_account.balance}'
            else:
                return f'{customer_ins.holder} does not have a {act_type} account'
        # same structure as above
        else:
            if hasattr(self,'reserve_account'):
                if check_overdraw(customer_ins, act_type, amount):
                    if do_overdraw(customer_ins, act_type, amount):
                        customer_ins.reserve_account.withdraw(amount+ReserveAccount.OVER_DRAW_FEE)
                        return f'withdrew {amount}, reserve account balance: {customer_ins.reserve_account.balance}'
                    else:
                        return f'balance: {customer_ins.reserve_account.balance}'
                else:
                    customer_ins.reserve_account.withdraw(amount)
                    return f'withdrew {amount}, checking account balance: {customer_ins.reserve_account.balance}'
            else:
                return f'{customer_ins.holder} does not have a {act_type} account'
            
    #the manager can halp transfer money between two accounts
    def transfer(self,from_customer_ins, from_act_type, to_customer_ins, to_act_type, amount):
        if not isinstance(from_customer_ins,Customer):
            return 'you entered incorrect sending customer, try again'
        if not isinstance(to_customer_ins,Customer):
            return 'you entered incorrect receiving customer, try again'
        if not from_act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid sending customer account type'
        if not to_act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid receiving customer account type'
        #use the withdraw and deposit method that have been created in the class to simplify the process 
        self.withdraw(from_customer_ins, from_act_type, amount)
        self.deposit(from_customer_ins, from_act_type, amount)        
        return f"successfully transfered {amount} from {from_customer_ins.holder}'s {from_act_type} account to {to_customer_ins.holder}'s {to_act_type} account"

    #the manager can check the customer's information: name, birthdate, id, credit rating 
    def check_cust_info(self, customer_ins, info_type):
        if not isinstance(customer_ins, Customer):
            return 'This customer is not in the system, check again'
        keys = ', '.join(customer_ins.info.keys())
        return customer_ins.info.get(info_type, f'{info_type} is invalid, choice from {keys}')                

    #if the account exists, the manager can delete the account 
    def delete_account(self, customer_ins):
        if not isinstance(customer_ins, Customer):
            return 'There is no such customer in our bank'
        name = customer_ins.holder
        del customer_ins
        return f'successfully deleted {name}\'s account'
 
    #the manager can approve the loan 
    def approve_loan(self,customer_ins,loan):
        if not isinstance(customer_ins,Customer):
            return 'you entered incorrect customer, try again'
        if not hasattr(customer_ins, 'saving_account'):
            return 'saving account needs to be opened to apply for loan'
        if customer_ins.get_credit>=500:
            self.deposit(customer_ins, 'saving', loan)
            return f'the loan has been approved to {customer_ins.holder}, new saving balance: {customer_ins.saving_account.balance}'
        else:
            return 'your loan has not been approved bacuase your credit rating is less than 500'

#this class is about the teller 
class Teller(Manager):
    '''
    >>> Xuerong=Customer('diana','05/16/1999','fin253',546)
    >>> Xuerong.openAccount(200000,'checking')
    'successfully opened a checking account, thank you'
    >>> Jiangyi=Customer('zhu','06/15/1999','love999',789)
    >>> Jiangyi.openAccount(500,'saving')
    'successfully opened a saving account, thank you'
    >>> Xilei=Teller('xilei','miss789')
    >>> Xilei.transfer(Xuerong,'checking',Jiangyi,'saving',10050)
    'ask a manager or an assitant to do that'
    >>> Xilei.transfer(Xuerong,'checking',Jiangyi,'saving',1005)
    'the transfer has been done successfully'
    >>> Xilei.access_info(Jiangyi,'name')
    'zhu'
    >>> Xilei.access_info(Jiangyi,'id')
    'id is restricted, or does not exist. pick from name, birthdate'

    '''

    #this is the information about the customer the teller can have access to: only the name and birthdate 
    allowed_info = ['name', 'birthdate']

    #this special method can show the users what the class can do 
    @property
    def __doc__(self):
        return '''the methods inherited from the Manager class do the similar things for the teller.
                Teller.transfer(self,from_customer_ins, from_act_type, to_customer_ins, to_act_type, amount) helps the teller to transfer limited money.
                Teller.access_info(self, customer_ins, info_type) helps the teller to have access to customer's information 
                other methods just shows what the manager can do but the teller cannot do 
                '''

    def __init__(self,name,teller_id):
        self.worker=name
        self.worker_id=teller_id

    #the teller can help do the tranfer which is limited amount 
    def transfer(self,from_customer_ins, from_act_type, to_customer_ins, to_act_type, amount):
        if not isinstance(from_customer_ins,Customer):
            return 'you entered incorrect sending customer, try again'
        if not isinstance(to_customer_ins,Customer):
            return 'you entered incorrect receiving customer, try again'
        if not from_act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid sending customer account type'
        if not to_act_type in ['checking', 'saving', 'reserve']:
            return 'you entered invalid receiving customer account type'
        if amount<=10000:
            self.withdraw(from_customer_ins, from_act_type, amount)
            self.deposit(from_customer_ins, from_act_type, amount)
            return 'the transfer has been done successfully'
        else:
            return 'ask a manager or an assitant to do that'

    #the teller can have access to limited customer information 
    def access_info(self, customer_ins, info_type):
        if not isinstance(customer_ins, Customer):
            return 'you entered incorrect customer, try again'
        if info_type not in Teller.allowed_info:
            return f'{info_type} is restricted, or does not exist. pick from {", ".join(Teller.allowed_info)}'
        if info_type == 'name':
            return customer_ins.holder
        else:
            return customer_ins.birthday
        
    #the teller cannot check all the customer information like the manager 
    def check_cust_info(self, customer_ins, info_type):
        return 'you cannot do that'

    #the teller cannot delete an account 
    def delete_account(self, customer_ins):
        return 'you cannot do that'

    #the teller cannot approve a loan
    def approve_loan(self,customer_ins,loan):
        return 'you cannot do that'
    
#this class is about the assistant 
class Assistant(Manager):
    '''
    >>> Gina=Assistant('gina','52099')
    >>> Xuerong=Customer('diana','05/16/1999','fin253',546)
    >>> Xuerong.openAccount(200000,'checking')
    'successfully opened a checking account, thank you'
    >>> Gina.check_cust_info(Xuerong,'name')
    'you cannot do that'
    >>> Gina.delete_account(Xuerong)
    'you cannot do that'
    >>> Gina.withdraw(Xuerong,'checking',500)
    'withdrew 500, checking account balance: 199499'
    '''

    #this special method can indicate what the class can do 
    @property
    def __doc__(self):
        return '''the Assistant class inherited from the Manager class. The class can do everything the Manager can do except
                  Assistant.check_cust_info(self, customer_ins, info_type and Assitant.delete_account(self, customer_ins)
               '''
        
    def __init__(self,name,assistant_id):
        self.worker=name
        self.worker_id=assistant_id

    #the assistant can do the things the manager can do except checking the customer information and delete an account 
    def check_cust_info(self, customer_ins, info_type):
        return 'you cannot do that'

    def delete_account(self, customer_ins):
        return 'you cannot do that'
    

    

        
        
        
