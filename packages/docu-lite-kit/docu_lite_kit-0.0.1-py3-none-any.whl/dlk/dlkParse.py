
class dlkBlock:
    """
        The building block object representing python definitions e.g. class, def.
        Any docstring and body content is stored in the object's .docstring and .body fields
        Most of the processing of python structures is done here
    """
    def __init__(self, first_line_number, doclines, pattern_list):
        self.first_line_number = first_line_number
        self.pattern_list = pattern_list
        self.first_line_text = doclines[first_line_number]
        self.indent_spaces = len(self.first_line_text) - len(self.first_line_text.lstrip())
        self.indent_level = 0
        self.signature = ""
        self.docstring = ""
        self.body = ""
        # if no pattern on first line, exit early with self.pattern = False
        if(pattern_list != 'docstring'):
            self.pattern = self._has_pattern(self.first_line_text)
            if(self.pattern == False):
                return
        else:
            self.pattern = 'docstring'

        self._fill_signature(doclines, first_line_number)
        self._fill_content(doclines, first_line_number)

    def to_dict(self):
        return {
            "type": self.pattern,
            "line_number": self.first_line_number,
            "signature": self.signature.strip(),
            "indent_level": self.indent_level,
            "docstring": [l.strip('\n') for l in self.docstring] if self.docstring else [],
            "body": [l.strip('\n') for l in self.body] if self.body else []
        }

    def _has_pattern(self, line):
        l = line.strip()
        for pat in self.pattern_list:
            if (l.startswith(pat) and line.endswith(':\n')):
                return line.split()[0]
        return False

    def _fill_signature(self, doclines, first_line_number):
        if("(" in self.first_line_text):
            lno = first_line_number
            sigtext = ""
            while not (')' in sigtext):
                sigtext += doclines[lno].strip()
                lno += 1
            self.signature =  sigtext[:sigtext.find(')')+1].replace(self.pattern,'').lstrip()
        else:
            self.signature = "".join(self.first_line_text.split()[1:])

    def _fill_content(self, doclines, first_line_number):
        content_start = first_line_number + 1
        content_end = len(doclines)-1
        docstring_start = -1
        docstring_end = -1
        line_no = first_line_number + 1 if self.pattern !='docstring' else first_line_number
        while( line_no <= content_end):
            line  = doclines[line_no].replace("'''",'"""').strip()
            if(line.startswith('"""')):
                if(docstring_start<0):
                    docstring_start = line_no
                    line = line.replace('"""','',1)
                else:
                    docstring_end = line_no
            if('"""' in line and docstring_start>=0):
                docstring_end = line_no
            if(self._has_pattern(doclines[line_no])):
                content_end = line_no
            line_no +=1
        if(docstring_start>=0):
            self.docstring = doclines[docstring_start:docstring_end + 1]
            content_start = docstring_end + 1
        self.body = doclines[content_start:content_end]
      #  self.body = [f"{docstring_start} {docstring_end} {content_start} {content_end}"]
        
class dlkParse:
    """
        Processes the input document into a list of dlkBlocks stored in the .blocks field
    """
    def __init__(self, doclines, patterns):
        self.blocks = []

        # get all blocks in a flat list
        for line_no, line in enumerate(doclines):
            block = dlkBlock(line_no, doclines, patterns)
            if(block.pattern):
                self.blocks.append(block)                
            elif len(self.blocks) == 0 and '"""' in line.replace("'''",'"""'):
                self.blocks.append(dlkBlock(line_no, doclines, 'docstring'))
                
        # tell each object what its indent level is within the document
        indents =[0]
        for dlkB in self.blocks:
            if(dlkB.indent_spaces > indents[-1]):
                indents.append(dlkB.indent_spaces)
            dlkB.indent_level = indents.index(dlkB.indent_spaces)

class dlkIO:
    """
        Reads the input file, calls dlkParse, and holds methods to output to screen and/or JSON
    """
    def __init__(self, input_file, pattern_list = ['def', 'class', 'docstring']):
        with open(input_file) as f:
            lines = f.readlines()
            self.blocks = dlkParse(lines, pattern_list).blocks

    def dlkPrint(self, pattern_list = ['def', 'class', 'docstring']):
        print(f"This is an example printout of the object list created by dlkParse\n\n")
        for block in self.blocks:
            if(block.pattern not in pattern_list):
                continue
            print(f"{block.first_line_number+1:4}: {block.pattern} {block.signature}")
            if('docstring' in pattern_list and block.docstring !=""):
                for l in block.docstring:
                    print(f"    docs:{l.replace('\n','')}")
            if('body' in pattern_list and block.body !=""):
                for l in block.body:
                    print(f"    body:{l.replace('\n','')}")
    
    def dlkDumpJSON(self, JSON_file = 'dlk.json', pattern_list = ['def', 'class', 'docstring']):
        import json
        block_dicts = [b.to_dict() for b in self.blocks]
        with open(JSON_file, 'w') as f:
            json.dump(block_dicts, f, indent=2)


