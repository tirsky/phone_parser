# phone_parser
This module helps to parse phone numbers in russian format on websites

Try it: it's simply


url and path to page with contacts

pr = PhoneParser('https://hands.ru/') 
print(pr.get_phone_from('company/about'))
