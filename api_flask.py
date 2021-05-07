#coding:utf-8

import flask
import sys
import os
import re

app = flask.Flask(__name__, template_folder="templates", static_folder="/home/gwenael/wgsi_server/static/")

def get_last_number_of_messages():
	'''
		Retrieve the last file value in the folder and increment the value.
		__get_last_number_of_messages(k)__.
	'''

	current_directory_flask_list = []

	for last_message_in_the_directory in os.listdir('messages'):
		last_message = re.findall('([0-9]{0,}\_message\.txt)', last_message_in_the_directory)
		for j in last_message:
			current_directory_flask_list.append(j)

	recover_last_message = int(current_directory_flask_list[0].split("_")[0]) + 1
	return str(recover_last_message) + "_message.txt"

@app.route('/contact_api_json', methods=["GET", "POST"])
def contact_api_json():
	'''
		You can send confidential data to our server, we will look into it all.
		return : json page!
	'''
	if(flask.request.method == "POST"):
		flask_request_json   = flask.request.json
		for item_pull_request in flask_request_json.items():
			if("lastname" and "firstname" and "message" in item_pull_request):
				'''
					In the POSTDATA, it should have information like this :
					{"lastname":"your_last_name", "firstname":"your_first_name", "message":"your_message_to_send"}
				'''
				try:
					flask_request_json["message"] = eval(flask_request_json["message"])

				except NameError as exception_error_flask_request:
					flask_request_json["message"] = flask_request_json["message"]

				except SyntaxError as exception_error_flask_request:
					flask_request_json["message"] = flask_request_json["message"]

				with open("messages/" + get_last_number_of_messages(), "w") as write_new_file:
					write_new_file.write("\nLastname: %s\nFirstname: %s\nMessage: %s\n\n" %(flask_request_json["lastname"], flask_request_json["firstname"], flask_request_json["message"]))
					return flask_request_json

	return "missing json data!"

@app.route('/')
def index_page():
	'''
		@This is the server index page.
		return : render_templates page! (index.html)
	'''
	return flask.render_template('index.html')

@app.route('/contact')
def contact_page():
	'''
		@This is the server contact page.
		return : render_templates page! (contact.html)
	'''
	return flask.render_template('contact.html')

if __name__ == "__main__":
	app.run(host="0.0.0.0")
