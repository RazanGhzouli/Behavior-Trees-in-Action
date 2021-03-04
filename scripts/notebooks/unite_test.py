#!/usr/bin/env python
# coding: utf-8

# In[1]:


from testbook import testbook
from mock import MagicMock

import io

from unittest.mock import patch
# In[2]:


@testbook(r"C:\Users\Razan\Behavior-Trees-in-Action\scripts\notebooks\BT-mining-script.ipynb", execute=True)

def test_greet(testbook):
    ACCESS_TOKEN = testbook.ref("ACCESS_TOKEN")
    
    
    # The actual test
    ACCESS_TOKEN('c78bb1f0644409a80ac4f5fd75e3779231e86e3a')
    testbook.assert_called_with('c78bb1f0644409a80ac4f5fd75e3779231e86e3a')
    ACCESS_TOKEN('c78bb1f0644409a80ac4f5fd75e3779231e86e3a')
    testbook.assert_called_with('c78bb1f0644409a80ac4f5fd75e3779231e86e3m')

    # Showing what is in mock
    import sys
    sys.stdout.write(str( testbook.call_args ) + '\n')
    sys.stdout.write(str( testbook.call_args_list ) + '\n')
    

    
if __name__ == '__main__':
    test_greet(testbook)
    print("Everything passed")
    
    
    
    
# def test_foo(tb):
#     ACCESS_TOKEN = tb.ref("ACCESS_TOKEN")

#     assert ACCESS_TOKEN('c78bb1f0644409a80ac4f5fd75e3779231e86e3a') ==  


# In[ ]:




