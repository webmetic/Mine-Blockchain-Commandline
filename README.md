# Mine-Blockchain-Commandline
I made a command line application for storing data in a blockchain. I've tried my best to fix all the possible bugs you might come across. You can use the "Mine_backend.py" file as a module directly as well. It uses MySql to store the blocks in the blockchain.

===================================================================================================================================================================================
HELP:

create blockchain "<name>";
Create new Blockchains using this command.

create block "<blockname>" from "<parentblock>" ("<data>");
Create new Blocks from Parentblock using this command.
NOTE: If this is the first Block in the Blockchain, use "basic" as parentblock.

create backblock "<blockname>" (<data>);
Create new Blocks from the backbone using this command.
(Refer set backbone command)

create uniblock "<blockname>" (<data>);
Create new Blocks from the previous parent using this command.
(Refer set unibranch command)

use "<blockchain>";
Use existing blockchains using this command.

verify "<blockchain>";
Verify existing blockchains using this command.

delete "<blockchain>";
Delete existing blockchains using this command.

show "<block>";
Use this command to view the data in the block.

set backbone as "<parentblock>";
Set a parentblock to use as universal parent.
(Used along with create backbone command)

set unibranch as "<parentblock>";
Set a parentblock to branch out from.
(Used along with create unibranch command)
