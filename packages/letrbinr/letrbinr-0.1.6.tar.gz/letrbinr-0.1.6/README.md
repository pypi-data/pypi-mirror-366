Hi! LetrBinr is programming language. 

rules of the language:
    there are 2 data types in this language - ltr (string or symbol) and bin (number).
    you can`t write capital letters excluding words True and False.

    initializing variable - {variable name} eq {data type} {binary number} ;
    for example: a eq bin 0101 ;

    creating a function - its {function name} lb {arguments} rb ;
    for example: its frog lb kwa rb ;

    calling a function: do {function name} lb {arguments} rb ;
    for example: do frog lb kwa rb ;
    before calling a function, you should initialize the arguments as variables.
    for example: kwa eq ltr 01 ;
                do frog lb kwa rb ;

    to start for loop, write: for {letter or word} bin {decimal number} ;
    for example: for i bin 0101 ;

    to start infinity while loop, write: for inf ;

    to create if statement, write: true lb {condition} rb ;
    for example: true lb a !cmpeq b & b cmpeq c rb ;

    there are six logic operators: & (and), || (or), bg (>), ls (<), cmpeq (==), !cmpeq (!=).
    and two boolean variables - True and False.
    you can`t use logic operators on not variables. 
    for example, you can`t write: a !cmpeq bin 01010 ; 
    or: bin 01001 cmpeq bin 0101 ;
    you can only compare the variables: a cmpeq b ;, b bg c ;, kwa !cmpeq meow ;

    to create an input, write: talk lb (something for input) rb ;
    for example: talk lb bin 01010 bin 01010 ltr 011 bin 011 ltr 01110 rb ;

    to create print, write: say (something to print) ;
    for example: say ltr 00000111 ltr 00000100 ltr 00001011 ltr 00001011 ltr 00001110 spc ltr 00010110 ltr 00001110 ltr 00010001 ltr 00001011 ltr 00000011 ; 
    this line is saying "hello world"

    to add space, write "spc", to add enter ("\n"), write "ntr", to add tab, write "tab".

    in the end of every line write ";".

    after if statement, for loop or while loop in the start of new line write "tab". 
    this command will add 4 spaces (required indentation) to the line.        

writing code:
    to start writing the code, call the function "code".

    line numbering starts from 1.

    if you made a mistake and you want to fix the line, write "fix {line number} {new code}".
    for example: fix 1 a eq bin 0101 ;
    
    if you want to run the code, write "run code".

    if you want to end the coding, write "end coding".

how to start:
    from letrbinr import LetrBinr
    
    lb = LetrBinr()
    lb.code()

Thank you so much for your interest in letrbinr!