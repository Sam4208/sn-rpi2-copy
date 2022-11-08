import smtplib
import imghdr
from email.message import EmailMessage

def alert():

    recipient_address=[]

    f = open("email_alert_settings.txt", "r")
    list_email_info = f.read().splitlines()  

    for line in range (0,len((list_email_info))):

        if line == 1:
            gmail_user  = list_email_info[line]
        elif line == 3:
            gmail_password = list_email_info[line]
        elif line== 5:
            email_subject= list_email_info[line]
        elif line== 7:
            email_text = list_email_info[line]
        elif line> 8:
            recipient_address.append(list_email_info[line])
         
    f.close()
    
    
    newMessage = EmailMessage()                         
    newMessage['Subject'] = email_subject
    newMessage['From'] = gmail_user                 
    newMessage['To'] = recipient_address                
    newMessage.set_content(email_text) 

    
    
  
    try:
    
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        #smtp_server.set_debuglevel(1)
        smtp_server.ehlo()
    
        smtp_server.login(gmail_user, gmail_password)
        
        smtp_server.send_message(newMessage)
    
        smtp_server.close()
    
        print ("Email sent successfully!")
    
    except Exception as ex:
    
        print ("Something went wrong….",ex)
        
alert()



    

    




