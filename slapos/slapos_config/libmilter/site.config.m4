

APPENDDEF(`confLIBDIRS', `-L/usr/lib')
APPENDDEF(`confINCDIRS', `-I/usr/include')

APPENDDEF(`confLIBS', `-lresolv')

dnl ### Changes to disable the default NIS support
APPENDDEF(`confENVDEF', `-UNIS')
APPENDDEF(`confENVDEF', `-fPIC')
dnl APPENDDEF(`confENVDEF', `-DDNSMAP=0')
dnl APPENDDEF(`confENVDEF', `-DNAMED_BIND=0')

dnl #####################################################################
dnl ###                                                               ###
dnl ### The next group of statements illustrates how to add support   ###
dnl ### for a particular map class.                                   ###
dnl ###                                                               ###
dnl ### Note that the map define goes in confMAPDEF, and that any     ###
dnl ### special library must be defined.  Note, also that include     ###
dnl ### directories and library directories must also be defined if   ###
dnl ### they are places that your compiler does not automatically     ###
dnl ### search.                                                       ###
dnl ###                                                               ###
dnl #####################################################################

dnl ### Changes for CDB support.
dnl APPENDDEF(`confMAPDEF',`-DCDB')
dnl APPENDDEF(`confLIBS', `-lcdb')
dnl APPENDDEF(`confINCDIRS', `-I/usr/local/include')
dnl APPENDDEF(`confLIBDIRS', `-L/usr/local/lib')

dnl #####################################################################
dnl ###                                                               ###
dnl ### The next group illustrates how to add support for a compile   ###
dnl ### time option.  In addition to the compile time define, any     ###
dnl ### required libraries must be given.  In addition, include and   ###
dnl ### library directories must be given if they are not standardly  ###
dnl ### searched by your compiler.                                    ###
dnl ###                                                               ###
dnl ### Note the "-R" for the library directory.  On some systems,    ###
dnl ### that can be used to tell the run time loader where to find    ###
dnl ### dynamic libraries (shared objects).  Check your system        ###
dnl ### documentation (man ld) to see if this is appropriate for your ###
dnl ### system.                                                       ###
dnl ###                                                               ###
dnl #####################################################################

dnl ### Changes for STARTTLS support
dnl APPENDDEF(`confENVDEF',`-DSTARTTLS')
dnl APPENDDEF(`confLIBS', `-lssl -lcrypto')
dnl APPENDDEF(`confLIBDIRS', `-L/usr/local/ssl/lib -R/usr/local/ssl/lib')
dnl APPENDDEF(`confINCDIRS', `-I/usr/local/ssl/include')
