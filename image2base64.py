import base64

image_file_path = '/home/pine/workspace/paddle/2222.png'  
output_file_path = '/home/pine/workspace/paddle/image2.txt'  

with open(image_file_path, 'rb') as image_file:
    image_data = image_file.read()

base64_encoded_data = base64.b64encode(image_data)
base64_message = base64_encoded_data.decode('utf-8')

with open(output_file_path, 'w') as file:
    file.write(base64_message)

print("Base64 encoded data has been written to", output_file_path)

