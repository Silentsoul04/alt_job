import sys

if sys.version_info[0] < 3: 
    print("Sorry, you must use Python 3")
    sys.exit(1)

from .core import AltJob

def main():
    AltJob()
    
if __name__ == '__main__':
    main()