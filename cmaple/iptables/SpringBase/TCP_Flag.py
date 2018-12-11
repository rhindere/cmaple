#! /usr/bin/env python
# -*- coding: utf-8 -*-

class TCP_Flag:
    """TCP_Flag class.
    This class describe a tcp_flag element.

    Parameters
    ----------
    tcp_flag : int or string. The tcp_flag name or number
    """
    def __init__(self, tcp_flag):
        """Initialize a tcp_flag class.

        Parameters
        ----------
        see above.
        """
        
        self.tcp_flag = tcp_flag
        
    def get_value(self):
        """Return the tcp_flag value"""
        return self.tcp_flag

    def to_string(self):
        """Return the tcp_flag value in string"""
        return self.tcp_flag
