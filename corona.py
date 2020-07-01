import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY = "tth8WtQ01c_S"
PROJECT_TOKEN = "tQOOVg87G0W0"
RUN_TOKEN = "taBV79hpbQ3d"

class Data:
	def __init__(self, api_key,project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key":self.api_key
		}
		self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',params=self.params)
		self.data = json.loads(response.text)
		return data
	def get_total_cases(self):
		return self.data['total'][0]['value']
	def get_total_deaths(self):
		return self.data['total'][1]['value']
	def get_total_recovered(self):
		return self.data['total'][2]['value']

	def get_country(self,country):
		data = self.data['country']
		for stuff in data:
			if stuff['name'].lower() == country.lower():
				return stuff
		return "0";

	def get_list_country(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())
		return countries;

	def update_data(self):
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("Data updated")
					break
				time.sleep(5)


		t = threading.Thread(target=poll)
		t.start()


def speak(text):
	engine =  pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		r.adjust_for_ambient_noise(source)
		audio = r.listen(source)
		val = ""

		try:
			val = r.recognize_google(audio)
		except Exception as e:
			print("Erorr:", str(e))

	return val.lower()


def main():
	data = Data(API_KEY,PROJECT_TOKEN)
	print("Started Program")
	END_PHRASE = 'stop'
	country_list = data.get_country

	TOTAL_PATTERNS = {
			re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
			re.compile("[\w\s]+ total cases"): data.get_total_cases,
            re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
            re.compile("[\w\s]+ total deaths"): data.get_total_deaths
	}

	COUNTRY_PATTERNS = {
		re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
	}
	UPDATE_COMMAND = "update"
	while True:
		print('Speak')
		text = get_audio()
		print(text)
		result = None
		for pattern,func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result=func();
				break;

		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words = set(text.split(" "))
				for country in country_list:
					if country in words:
						result = func(country)
						break;

		if result:
			print(result)

		if text.find(END_PHRASE) != -1:
			break
		if text == UPDATE_COMMAND:
			data.update_data();

main()