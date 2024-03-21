"""
Inspired in the mininet CLI.
"""

import subprocess
from cmd import Cmd
from os import isatty
from select import poll, POLLIN
import select
import sys
import os
import atexit

class VNFCLI( Cmd ):
    "Simple command-line interface to talk to nodes."

    prompt = 'nfv-menu> '

    def __init__( self, controller, stdin=sys.stdin, script=None,
                  *args, **kwargs ):

        self.controller = controller
        # Local variable bindings for py command
        self.locals = { 'controller': controller }
        # Attempt to handle input
        self.inPoller = poll()
        self.inPoller.register( stdin )
        self.inputFile = script
        Cmd.__init__( self, *args, stdin=stdin, **kwargs )

        self.hello_msg()
        if self.inputFile:
            self.do_source( self.inputFile )
            return

        self.initReadline()
        self.run()

    readlineInited = False

    def hello_msg(self):
        """
        """
        print('======================================================================')
        print('Welcome to the NFV CLI')
        print('======================================================================')
        print('You can now make reservations for your hosts in the network.')
        print('To add a firewall policy run:')
        print('add_fw_entry <src> <dst>')
        print('')
        print('To delete a reservation run: ')
        print('del_fw_entry <src> <dst>')
        print('')


    @classmethod
    def initReadline( cls ):
        "Set up history if readline is available"
        # Only set up readline once to prevent multiplying the history file
        if cls.readlineInited:
            return
        cls.readlineInited = True
        try:
            from readline import ( read_history_file, write_history_file,
                                   set_history_length )
        except ImportError:
            pass
        else:
            history_path = os.path.expanduser( '~/.nfv_controller_history' )
            if os.path.isfile( history_path ):
                read_history_file( history_path )
                set_history_length( 1000 )
            atexit.register( lambda: write_history_file( history_path ) )

    def run( self ):
        "Run our cmdloop(), catching KeyboardInterrupt"
        while True:
            try:
                if self.isatty():
                    subprocess.call( 'stty echo sane intr ^C',shell=True)
                self.cmdloop()
                break
            except KeyboardInterrupt:
                # Output a message - unless it's also interrupted
                # pylint: disable=broad-except
                try:
                    print( '\nInterrupt\n' )
                except Exception:
                    pass
                # pylint: enable=broad-except

    def emptyline( self ):
        "Don't repeat last command when you hit return."
        pass

    def getLocals( self ):
        "Local variable bindings for py command"
        self.locals.update( self.mn )
        return self.locals

    helpStr = (
        'To add a reservation run:\n'
        'add_reservation <src> <dst> <duration> <bw> <priority>\n'
        '\n'
        'To delete a reservation run: \n'
        'del_reservation <src> <dst>\n'
        ''
    )

    def do_help( self, line ):
        "Describe available CLI commands."
        Cmd.do_help( self, line )
        if line == '':
            print( self.helpStr )
  
    def do_exit( self, _line ):
        "Exit"
        assert self  # satisfy pylint and allow override
        return 'exited by user command'

    def do_quit( self, line ):
        "Exit"
        return self.do_exit( line )

    def do_EOF( self, line ):
        "Exit"
        print( '\n' )
        return self.do_exit( line )

    def isatty( self ):
        "Is our standard input a tty?"
        return isatty( self.stdin.fileno() )

    """
    NFV COMMANDS
    """


    def do_print_mpls_path(self, line = ""):
        """Prints current mpls paths"""

        print("Current MPLS Paths:")
        print("---------------------")
        for i, ((src, dst), datas) in enumerate(self.controller.current_path.items()):
            for data in datas:
                if (len(data) > 1):
                    print("{} {}->{} : {}".format(i, src, dst, 
                        "->".join(data)))
    
    def do_print_fw_policy(self, line=""):
        """Prints current firewall policies"""

        print("Current FireWall Policies:")
        print("---------------------")
        for src, dst in self.controller.firewall_policy.keys():
            print("{} -> {}".format(src, dst))
        
    def do_add_fw_entry(self, line=""):
        """
        Adds a firewall policy.
        add_fw_entry <src> <dst>
        """
        # gets arguments
        args = line.split()

        if len(args) < 2:
            print("Not enough args!")
            return
        
        elif len(args) == 2:
            src, dst =  args[:2]
        
        else:
            print("Too many args!")
            return

        # add entry
        res = self.controller.add_firewall_policy(src, dst)
    
    def do_del_fw_entry(self, line=""):
        """
        Delete a firewall policy.
        del_fw_entry <src> <dst>
        """
        # gets arguments
        args = line.split()

        if len(args) < 2:
            print("Not enough args!")
            return
        
        elif len(args) == 2:
            src, dst =  args[:2]
        
        else:
            print("Too many args!")
            return

        # add entry
        res = self.controller.del_firewall_policy(src, dst)