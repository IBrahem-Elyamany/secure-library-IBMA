import os


def allowed_ex(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in {'png','jpg','jpeg','gif'}
def allowed_size(file):
    file.seek(0,os.SEEK_END)
    file_size=file.tell()
    file.seek(0,os.SEEK_SET)
    return file_size <= 5*1024*1024