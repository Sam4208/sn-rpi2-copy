from email_alert import *
send = True

print('\n\n\nWhat time period would you like to view data entries for?\n--------------------------------------------------------------------------------------------\nFor data from the current time to a set number of days in the past - today\nFor data between 2 custom times - hist\n--------------------------------------------------------------------------------------------')
answer = input()

if answer == 'today':
 print('\n\n\nFor how many days in the past would you like to view data entries for?')
 days_in_past = input()
 try:
   end_time = datetime.datetime.now()
   start_time = end_time - datetime.timedelta(days=int(days_in_past))
 except ValueError or TypeError:
    print('Incorrect date format')
    send = False
      

elif answer == 'hist':
   print('\n\n\nWhat dates would you like to view data between?\n--------------------------------------------------------------------------------------------\nhh/dd/mm/yy-hh/dd/mm/yy\n--------------------------------------------------------------------------------------------')
   date_input = input()
   try:
            
       year = (int('20'+str(date_input[9:11])))
       month = int(date_input[6:8])
       day = int(date_input[3:5])
       hour = int(date_input[0:2])
       start_time=datetime.datetime(year,month,day,hour)

       year = (int('20'+str(date_input[21:23])))
       month = int(date_input[18:20])
       day = int(date_input[15:17])
       hour = int(date_input[12:14])
       end_time=datetime.datetime(year,month,day,hour)     

      
   except ValueError :     
       print('Incorrect date format') 
       send=False


print('\n\nWould you like to send this data to a new email address or all stored addresses\n--------------------------------------------------------------------------------------------\nnew\nstored\n--------------------------------------------------------------------------------------------')
email_decision = input()
if email_decision == 'stored':
  email = 'stored'
elif email_decision == 'new':
  print('\n\nType in the new email address')
  email = input() 

if send == True:
    print('\n\nTrying to send email...\n\n')
    email_alert(True,False,False,False,False,False,False,False,False,False,start_time,end_time,email)
