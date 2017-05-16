import boto3
import uuid
dynamodb = boto3.resource("dynamodb",region_name="us-west-2",
aws_access_key_id= "",
aws_secret_access_key = "")
import json
import datetime

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):

    operation=event['httpMethod']
    if operation=='POST':
          table=dynamodb.Table('order')
    	  response = table.put_item(
          	Item={
         	   'menu_id':event['menu_id'],
            	   'order_id':event['order_id'],
            	   'customer_name':event['customer_name'],
            	   'customer_email':event['customer_email'],
            	   'order_status': 'processing',
            	   "order": {  }
          	 })
    	  table=dynamodb.Table('Pizza')     
    	  response=table.get_item(
        	Key={
            	  'menu_id':event['menu_id']
        	})
          if(response['Item']['sequence'][0]=='selection'):    
               outcome=""
               outcome+="Hi "+event['customer_name']
               outcome+=", please choose one of these selection:"
               value_coun=1
               for k in response['Item']['selection']:
                   outcome+=(" "+str(value_coun)+". "+str(k)+",")
                   value_coun+=1
               outcome=outcome[:-1]
          else: 
               outcome=""
               outcome+="Hi "+event['customer_name']
               outcome+="Which size do you want?"
               value_coun=1
               for k in response['Item']['size']:
                  outcome+=(" "+str(value_coun)+". "+str(k)+",")
                  value_coun+=1
               outcome=outcome[:-1]    
          return {"Message": outcome}
    elif (operation=='PUT'):
          table=dynamodb.Table('order')
          response = table.get_item(
       		 Key={
              		'order_id':event['order_id'],
          		})
          ordermap=  response['Item']['order']
    	  table=dynamodb.Table('Pizza')
          detailsmenu=table.get_item(
       		Key={
                   'menu_id':response['Item']['menu_id'] 
         	})
          if (detailsmenu['Item']['sequence'][0]=='selection'):
               if 'selection' not in ordermap:
            	outcome=""
                input_number=int(event['input'])
                outcome+="Which size do you want?"
                value_coun=1
                for k in detailsmenu['Item']['size']:
                  outcome+=(" "+str(value_coun)+". "+str(k)+",")
                  value_coun+=1
                outcome=outcome[:-1] 
                if((input_number-1)<(len(detailsmenu['Item']['selection']))):
                    order_selection={"selection":detailsmenu['Item']['selection'][input_number-1]}
                else:
                    return "Please select from available options."
                table=dynamodb.Table('order')
                res=table.update_item(
                   Key={
                        'order_id':event['order_id']
                       },
                       UpdateExpression= "SET #n= :val1",
                       ExpressionAttributeNames = {"#n":"order"},
                       ExpressionAttributeValues={':val1': order_selection})
                return {"Message":outcome}
               elif 'size' not in ordermap:
            	input_number=int(event['input']) 
                if((input_number-1)<(len(detailsmenu['Item']['size']))):
            	   order_size=detailsmenu['Item']['size'][input_number-1]
                else:
                   return "Please select from available options."
            	dict_map={}
            	dict_map['selection']=response['Item']['order']['selection']
            	dict_map['size']=order_size
            	order_price=detailsmenu['Item']['price'][input_number-1]
            	dict_map['costs']=order_price
            	dict_map['order_time']=str(datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S'))
            	table=dynamodb.Table('order')
                res=table.update_item(
                Key={
                    'order_id':event['order_id']
                    },
                UpdateExpression= "SET order_status= :val1,#n= :val2",
                ExpressionAttributeNames = {"#n":"order"},
                ExpressionAttributeValues={":val1": "processing",':val2':dict_map})
                outcome=""
                outcome+="Your order costs $"+order_price+". We will email you when the order is ready. Thank you!"
                return {"Message":outcome} 
               else:
            	return "Please select from the available options."
          elif (detailsmenu['Item']['sequence'][0]=='size'):
               if 'size' not in ordermap:
            	   outcome="" 
                   outcome+='please choose one of these selection:'
                   value_coun=1
            	   for k in detailsmenu['Item']['selection']:
                      outcome+=(" "+str(value_coun)+". "+str(k)+",")
                      value_coun+=1
                   outcome=outcome[:-1]
            	   input_number=int(event['input']) 
                   if((input_number-1)<(len(detailsmenu['Item']['size']))):
                         order_size=detailsmenu['Item']['size'][input_number-1]
                   else:
                         return "Please select from the available options."
                   dict_map={}
                   #dict_map['selection']=response['Item']['order']['selection']
                   dict_map['size']=order_size
                   order_price=detailsmenu['Item']['price'][input_number-1]
                   dict_map['costs']=order_price
                   dict_map['order_time']=datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S')
                   table=dynamodb.Table('order')
                   res=table.update_item(
                	Key={
                    		'order_id':event['order_id']
                    	},
                	UpdateExpression= "SET order_status= :val1,#n= :val2",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={":val1": "processing",':val2':dict_map})
                   return {"Message":outcome}  
               elif 'selection' not in ordermap:
                   input_number=int(event['input'])
                   if((input_number-1)<(len(detailsmenu['Item']['selection']))):
            	       order_selection={"selection":detailsmenu['Item']['selection'][input_number-1]}
                   else:
                       return "Please select from the available options."
            	   order_selection['size']=response['Item']['order']['size']
            	   order_selection['costs']=response['Item']['order']['costs']
            	   order_selection['order_time']=response['Item']['order']['order_time']
            	   table=dynamodb.Table('order')
                   res=table.update_item(
                	Key={
                          'order_id':event['order_id']
                        },
                        UpdateExpression= "SET #n= :val1",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={':val1': order_selection})
                   outcome=""
            	   outcome+="Your order costs $"+order_selection['costs']+'. We will email you when the order is ready. Thank you!'
                   return {"Message":outcome} 
               else: 
            	   return "Please select from the available options."   
    elif (operation=='GET'):
         table=dynamodb.Table('order')
         try:
             response=table.get_item(
      	  		Key={
                        'order_id':event['order_id']
             })
             return response['Item'] 
         except KeyError:return "400"
         
    else:
        return respond(ValueError('Unsupported method'))
   
