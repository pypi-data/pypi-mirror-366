# Docu-lite-kit
Standalone cli/importable components inspired by [docu-lite](https://pypi.org/project/docu-lite/)

The first component here is the ultra-light Python parser:
- Rewritten to be more robust around docstrings
- Packaged to be useable from the command line or imported as a module into other code
- Soon to replace the parser used within docu-lite

Current plans / ideas:
- Add the 'pattern'/'include' options in the demo file as cli arguments
- Add standalone / importable docu-lite-like html rendering components
- Add standalone / importable API delta checkers
  
## Screenshot
<img width="1296" height="589" alt="Capture" src="https://github.com/user-attachments/assets/d446b89a-4313-4599-9e97-a015ffe505e6" />


## 🛠 Installation

Install using pip: open a command window and type

```
pip install docu-lite-kit
```
## 💡 Usage
### Command line:
```
dlk.cli [-h] [--out] [--noprint] input.py
```
-  -h = show help
-  --out specifies the output file (JSON format)
-  --noprint = don't print the basic printout to the console 

### Imported as a module:
```
import dlk
```

Provides the following three interfaces (see demo_minimal.py):
```
    input_file = r"./demo_minimal.py"
    # parse the doc looking for objects matching a,b,c,d:
    # parser = dlk.dlkIO(input_file, [ pattern_list =  [a,b,c,d] ])
    # For the pattern list, docstring and body are implied & don't need to be mentioned.
    # The pattern list itself is optional and defaults to ['class', 'def']
    parser = dlk.dlkIO(input_file)

    # print out the result including the elements a,b,c,d:
    # parser.dlkPrint([a,b,c,d])
    # This time 'docstring' and 'body' do need to be explicitly mentioned if wanted in the printout
    # However pattern list is optional and defaults to ['class', 'def', 'docstring']
    # parser.dlkPrint( pattern_list = ['def', 'class', 'docstring', 'body'])
    parser.dlkPrint(['def', 'class', 'docstring', 'body'])

    # Similar to dlkPrint, this dumps the output to a JSON file:
    # parser.dlkDumpJSON(self, JSON_file = 'dlk.json', pattern_list = ['def', 'class', 'docstring'])
    parser.dlkDumpJSON()

```

[PyPI link](https://pypi.org/project/docu-lite-kit/)
