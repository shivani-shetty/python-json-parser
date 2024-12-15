class JsonException(Exception):
    pass


class JsonParser:
    def __init__(self):
        self.i=0
        self.depth=0
        self.s=""

    def skip_whitespace(self):
        while self.s[self.i] in [" ","\n","\t","\r"] and self.i<len(self.s):
            self.i+=1

    def process_colon(self):
        if self.s[self.i] != ":":
            raise JsonException('Invalid JSON: Expected ":"')
        self.i += 1

    def process_comma(self):
        if self.s[self.i] != ",":
            raise JsonException('Invalid JSON: Expected ","')
        self.i += 1

    def parse_string(self):
        try:
            if self.s[self.i] == '"':
                self.i+=1
                self.skip_whitespace()
                res=""
                while self.s[self.i] != '"':
                    if self.s[self.i] == '\\':
                        next_char=self.s[self.i+1]
                        if next_char in ['"','//','/','b','f','n','r','t']:
                            res+=next_char
                            self.i+=1
                        elif next_char=='u':
                            #this hexadecimal could respresent a special character/emoji/..
                            if (isHexaDecimal(self.s[self.i+2]) and isHexaDecimal(self.s[self.i+3])
                                and isHexaDecimal(self.s[self.i+4]) and isHexaDecimal(self.s[self.i+5])):
                                res+=chr(int(self.s[self.i+2:self.i+6], 16))
                                self.i+=5
                        else:
                            raise JsonException("Invalid JSON: Illegal backlash sequence")
                    else:
                        if self.s[self.i]=="\t":
                            raise JsonException("Invalid JSON: tab character in the string")
                        elif self.s[self.i]=="\n":
                            raise JsonException("Invalid JSON: line break character in the string")
                        else:
                            res+=self.s[self.i]
                        self.i+=1
                self.i+=1
                return res
                    
        except IndexError:
            raise JsonException("Invalid JSON: Missing end quote") 
        
    def parse_number(self):
        start=self.i
        #move past the negative sign
        if self.s[self.i]=="-":
            self.i+=1

        if self.s[self.i] == "0":
            self.i += 1

        elif self.s[self.i].isnumeric():
            self.i += 1
            while self.s[self.i].isnumeric():
                self.i += 1

        if self.s[self.i] == ".":
            self.i += 1
            while self.s[self.i].isnumeric():
                self.i += 1

        if self.s[self.i].lower() == "e":
            self.i += 1
            if self.s[self.i] in ["-", "+"]:
                self.i += 1
            while self.s[self.i].isnumeric():
                self.i += 1

        if self.i > start:
            try:
                number = float(self.s[start:self.i])
            except ValueError:
                raise JsonException(f'Invalid JSON: Invalid number (\'{self.s[start:self.i]}\')')
            if float(number) % 1 == 0:
                return int(number)
            else:
                return float(number)
            
    def parse_object(self):
        if self.s[self.i] == "{":
            self.i += 1
            self.depth += 1
            self.skip_whitespace()
            result = {}
            initial = True

            while self.s[self.i] != "}":
                if not initial:
                    self.skip_whitespace()
                    self.process_comma()
                    self.skip_whitespace()

                key = self.parse_string()
                self.skip_whitespace()
                self.process_colon()
                self.skip_whitespace()
                value = self.parse_value()
                result[key] = value
                self.skip_whitespace()
                initial = False

            self.i += 1
            self.depth -= 1
            return result

    
    def parse_value(self):
        res=self.parse_string()
        if not res:
            res=self.parse_number()
        if not res:
            res=self.parse_object()
        if not res:
            res=self.parse_list()
        if not res:
            res = self.parse_keyword("true", True)
        if res is None:
            res = self.parse_keyword("false", False)
        if res is None:
            res = self.parse_keyword("null", None)
        return res
    
    def parse_list(self):
        if self.s[self.i] == "[":
            self.i += 1
            self.depth += 1
            if self.depth > 19:
                raise JsonException("Exceeds maximum depth allowed for this parser.")
            self.skip_whitespace()

            result = []
            initial = True

            try:
                while self.s[self.i] != "]":
                    if not initial:
                        self.process_comma()
                        self.skip_whitespace()
                    value = self.parse_value()
                    self.skip_whitespace()
                    result.append(value)
                    initial = False
            except IndexError:
                raise JsonException("Invalid JSON: Missing closing bracket")

            self.i += 1
            self.depth -= 1
            return result
        
    def parse_keyword(self,keyword,value):
        if self.s[self.i:self.i+len(keyword)]==keyword:
            self.i+=len(keyword)
            return value


    def parse_json_string(self,s):
        self.s=s
        self.skip_whitespace()
        if self.s[self.i] not in ["{", "["]:
            raise JsonException("Json should either be an object or an array of objects")
        json_object=self.parse_value() 
        return json_object

    
def isHexaDecimal(c):
    try:
        #Tries to convert c into a base 10 number from base 16. Returns false if it doesn't belong in the A-F,0-9
        int(c,16)
        return True
    except ValueError:
        return False