import sys
import os

# Add the project root to sys.path so 'oops' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oops.main import main

if __name__ == "__main__":
    main()
