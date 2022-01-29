import streamlit as st
import youtube_dl
import requests
import pprint
from configure import auth_key
from time import sleep

if 'status' not in st.session_state:
    st.session_state['status'] = 'submitted'
    st.session_state['save_location'] = '' 
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192', 
    }],
    'ffmpeg-location': './',
    'outtmpl': "./%(id)s.%(ext)s",
}
CHUNK_SIZE = 5242880

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers = {
    "authorization": auth_key,
    "content-type":"application/json"
}

@st.cache
def download_audio(link):
    _id = link.strip()
    def get_vid(_id):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(_id)
        #download audio part of video to local
    meta = get_vid(_id)
    st.session_state['save_location'] = meta['id']+".mp3"
    print('saved video(mp3) to', st.session_state['save_location'])
        
def read_file(filename):
    with open(filename,'rb') as _file:
        while True:
            data = _file.read(CHUNK_SIZE)
            if not data:
                break
            yield data
 
#access file and upload
def start_transcription():
    upload_response = requests.post(
        upload_endpoint,
        headers=headers, data=read_file(st.session_state['save location'])           
    )

    audio_url = upload_response.json()['upload_url']
    print("Uploaded to", audio_url)
    
    transcript_request = {
        'audio_url': audio_url,
        'lab_categories': 'False',
    }
    #send request
    transcript_response = request.post(transcript_endpoint, json=transcript_request, headers=headers)
    
    transcript_id = transcript_response.json()['id']
    polling_endpoint = transcript_endpoint + "/" + transcript_id
    return polling_endpoint
            
st.title("Easily transcribe Youtube videos")
#this is a random video length 23s 480p
link = st.text_input("Enter your youtube video link", "https://www.youtube.com/watch?v=WX7-3E6cirQ")

download_audio(link)

#start
polling_endpoint = start_transcription()
#update the session state

while st.session_state['status']!='completed':
    polling_response = requests.get(polling_endpoint, headers=headers)
    st.session_state['status'] = polling_response.json()['status']
    print(polling_response.json()['status'])
    transcription = polling_response.json()['text']

st.markdown(transcription)