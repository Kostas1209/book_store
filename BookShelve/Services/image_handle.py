import os
import base64
from PIL import Image


MAX_SIZE = 10


def get_size(file):
    st = os.stat(file) 
    if st.st_size >= 1024 * 1024 * MAX_SIZE:
        raise Exception("file is bigger than {} MB!".format(MAX_SIZE))
    
    return st.st_size 

def write_image_to_file(file_path, note_path):
    image = Image.open(file_path)
    image = image.resize((180,240), Image.ANTIALIAS)
    text = base64.b64encode(image.tobytes())
    with open(note_path,"wb") as file:
        pickle.dump(text, file)
    return text

def get_image_from_text(create_image_path, text):
    bytes = base64.b64decode(text)
    image = Image.frombytes(size = (180,240),data = bytes,mode = 'RGB')
    image = image.rotate(270)
    image.save(create_image_path, format = "JPEG")