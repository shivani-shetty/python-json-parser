import argparse
from app.json_parser import JsonParser

parser=argparse.ArgumentParser()
parser.add_argument("-file", action="store",dest="fileName",help="Location of the json file to be parsed")

if __name__=="__main__":
    input_args=parser.parse_args()
    file_name=input_args.fileName

    with open(file_name,'r') as file:
        content=file.read()
    
    json_parser=JsonParser()
    print(json_parser.parse_json_string(content))