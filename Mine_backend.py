from logging import error
from mysql import connector as sql
import time
import hashlib

#mysql profile
host = "localhost"
user = "root"
password = "mysql123"

try:
    root = sql.connect(host = host, user = user, password = password)
    rootcommand = root.cursor()
except:
    print("Unable to connect to the Database")
    exit = True

def create_blockchain(blockchain_name):
    global command, branch
    try:
        rootcommand.execute("Create database `%s`;" % blockchain_name)
        branch = sql.connect(host = host, user = user, password = password, database = blockchain_name)
        command = branch.cursor()

        command.execute("Create table Basic(Timestamp double,Hash varchar(56));")
        command.execute("Insert into Basic values(%s,'%s');" % (str(time.time()), hashlib.sha224(bytes(blockchain_name + " secret hexit","utf-32")).hexdigest()))
        
        branch.commit()
        return "Sucessfully created Blockchain: " + blockchain_name

    except Exception as e:
        e =  str(e).replace("database","blockchain")
        e =  str(e).replace("Database","Blockchain")
        return e

def use_blockchain(blockchain_name):
    global command, branch
    try: 
        branch = sql.connect(host = host, user = user, password = password,database = blockchain_name)
        command = branch.cursor()
        command.execute("use `%s`" % blockchain_name)
        return "Using Blockchain: " + blockchain_name

    except Exception as e:
        e =  str(e).replace("database","blockchain")
        e =  str(e).replace("Database","Blockchain")
        return e

def create_block(block_name, parent_block,data):
    global command, branch
    try:
        command.execute("Show tables;")
        all_blocks = command.fetchall()
        if (parent_block,) in all_blocks: 
            command.execute("Create table `%s`(Timestamp double, Hash varchar(56), Parent_Block varchar(40), Data varchar(100));" % block_name)
            command.execute("Select * from `%s`;" % parent_block)
            parent_block_data = command.fetchone()
            command.execute("Insert into `%s` values(%s, '%s', '%s', '%s');" % (block_name, str(time.time()), hashlib.sha224(bytes(str(parent_block_data),"utf-32")).hexdigest(), parent_block, data))
            
            branch.commit()
            return "Sucessfully created Block: " + block_name
        else:
            return "Invalid Parent Block. Please create first block from 'basic' parent block if you haven't already."

    except Exception as e:
        e =  str(e).replace("table", "block")
        e =  str(e).replace("Table", "Block")
        return e

def verify_blockchain(blockchain_name):

    try:
        branch = sql.connect(host = host, user = user, password = password, database = blockchain_name)
        branch_command = branch.cursor()
        n = 0
        branch_command.execute("Show tables;")
        error = False
        all_blocks = branch_command.fetchall()
        total_blocks = len(all_blocks)
        while error == False and n < total_blocks :
            child_block = all_blocks[n][0]
            n+=1
            if child_block.lower() == "basic":
                branch_command.execute("Select Hash from basic;")
                basic_hash = branch_command.fetchone()[0]
                if basic_hash == hashlib.sha224(bytes(blockchain_name + " secret hexit","utf-32")).hexdigest():
                    continue
                else:
                    return "Hash in Root Block was manipulated."
            branch_command.execute("Select Parent_Block, Hash from %s;" % child_block)
            child_block_data = branch_command.fetchone()
            parent_block = child_block_data[0]
            parent_block_hash = child_block_data[1]
            branch_command.execute("Select * from %s;" % parent_block)
            parent_block_data = branch_command.fetchone()
            calculated_parent_block_hash = hashlib.sha224(bytes(str(parent_block_data), "utf-32")).hexdigest()
            if parent_block_hash != calculated_parent_block_hash:
                error = True
                return "Data in %s (Parent Block) or Hash in %s (Child Block) was manipulated." % (parent_block, child_block) 

        else:
            return "Verified " + str(n) + " blocks"
    
    except Exception as e:
        e =  str(e).replace("table", "block")
        e =  str(e).replace("Table", "Block")
        return e

def verify_block(block_name, parent_block):
    global command, branch
    error = False

    try:
        if block_name.lower() == "basic":
            exit
        command.execute("Select Parent_Block, Hash from %s;" % block_name)
        child_block_data = command.fetchone()
        parent_block = child_block_data[0]
        parent_block_hash = child_block_data[1]
        command.execute("Select * from %s;" % parent_block)
        parent_block_data = command.fetchone()
        calculated_parent_block_hash = hashlib.sha224(bytes(str(parent_block_data), "utf-32")).hexdigest()
        if parent_block_hash != calculated_parent_block_hash:
            error = True
            return "Data in %s (Parent Block) or Hash in %s (Child Block) was manipulated." % (parent_block, block_name) 

        return "Verified " + block_name + " block."
    
    except Exception as e:
        e =  str(e).replace("database","blockchain")
        e =  str(e).replace("Database","Blockchain")
        e =  str(e).replace("table","block")
        e =  str(e).replace("Table","Block")
        return e

def delete_blockchain(blockchain_name):
    try:
        rootcommand.execute("Drop database `%s`;" % blockchain_name)
        return "Sucessfully deleted Blockchain: " + blockchain_name
    
    except Exception as e:
        e =  str(e).replace("database","blockchain")
        e =  str(e).replace("Database","Blockchain")
        return e

def show_block_data(block_name):
    try:
        global command, branch
        command.execute("Select Data from `%s`;" % block_name)
        data = command.fetchone()[0]
        return "Data of " + block_name + ": " + data
    except Exception as e:
        e =  str(e).replace("table", "block")
        e =  str(e).replace("Table", "Block")
        return e

def set_backbone_block(parent_block_name):
    global branch, command, backbone_block
    command.execute("Show tables;")
    all_blocks = command.fetchall()
    if (parent_block_name,) in all_blocks: 
        backbone_block = parent_block_name
        return "Set " + backbone_block + " as parent block." 
    else:
        return "Block does not exist."
    
def create_backbone_block(block_name, data):
    global  backbone_block, command, branch
    try:
        command.execute("Create table `%s`(Timestamp double, Hash varchar(56), Parent_Block varchar(40), Data varchar(100));" % block_name)
        command.execute("Select * from `%s`;" % backbone_block)
        parent_block_data = command.fetchone()
        command.execute("Insert into `%s` values(%s, '%s', '%s', '%s');" % (block_name, str(time.time()), hashlib.sha224(bytes(str(parent_block_data),"utf-32")).hexdigest(), backbone_block, data))
        
        branch.commit()
        return "Sucessfully created " + block_name + "Childblock(from " + backbone_block + ")"
    except Exception as e:
        e =  str(e).replace("table", "block")
        e =  str(e).replace("Table", "Block")
        return e

def set_unibranching_block(parent_block_name):
    global branch, command, unibranching_block
    command.execute("Show tables;")
    all_blocks = command.fetchall()
    if (parent_block_name,) in all_blocks: 
        unibranching_block = parent_block_name
        return "Set " + unibranching_block + " as parent block."
    else:
        return "Block does not exist."

def create_unibranching_block(block_name, data):
    global unibranching_block, command, branch
    try:
        current_unibranching_block = unibranching_block
        command.execute("Create table `%s`(Timestamp double, Hash varchar(56), Parent_Block varchar(40), Data varchar(100));" % block_name)
        command.execute("Select * from `%s`;" % current_unibranching_block)
        parent_block_data = command.fetchone()
        command.execute("Insert into `%s` values(%s, '%s', '%s', '%s');" % (block_name, str(time.time()), hashlib.sha224(bytes(str(parent_block_data),"utf-32")).hexdigest(), current_unibranching_block, data))
        branch.commit()
        set_unibranching_block(block_name)
        return "Sucessfully created " + block_name + "Childblock(from " + current_unibranching_block + ")"
    except Exception as e:
        e =  str(e).replace("table", "block")
        e =  str(e).replace("Table", "Block")
        return e

exit = False

while exit == False:
    cmd_input = input("Mine >> ")
    cmd_input = cmd_input.lower()
    if "create" in cmd_input:

        if "blockchain" in cmd_input:
            #create blockchain "<name>";
            if "\"" in cmd_input:
                first_occurrence = cmd_input.find("\"") + 1
                last_occurrence = cmd_input.find("\"", first_occurrence)
                blockchain_name = cmd_input[first_occurrence : last_occurrence]
                print(create_blockchain(blockchain_name))
            elif "\'" in cmd_input:
                first_occurrence = cmd_input.find("\'") + 1
                last_occurrence = cmd_input.find("\'", first_occurrence)
                blockchain_name = cmd_input[first_occurrence : last_occurrence]
                print(create_blockchain(blockchain_name))   
            else:
                print("Error: Invalid syntax. Type help for help.")
        
        elif "block" and "from" and "(" and ")" in cmd_input:
            #create block "<blockname>" from "<parentblock>" ("<data>");
            if "\"" in cmd_input:
                first_occurrence = cmd_input.find("\"") + 1
                last_occurrence = cmd_input.find("\"", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            elif "\'" in cmd_input:
                first_occurrence = cmd_input.find("\'") + 1
                last_occurrence = cmd_input.find("\'", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            else:
                print("Error: Invalid syntax. Type help for help.")
                continue

            if "\"" in cmd_input:
                first_occurrence = cmd_input.find("\"", last_occurrence + 1) + 1
                last_occurrence = cmd_input.find("\"", first_occurrence)
                parent_block = cmd_input[first_occurrence : last_occurrence]

            elif "\'" in cmd_input:
                first_occurrence = cmd_input.find("\'", last_occurrence + 1) + 1
                last_occurrence = cmd_input.find("\'", first_occurrence)
                parent_block = cmd_input[first_occurrence : last_occurrence]

            else:
                print("Error: Invalid syntax. Type help for help.")
                continue
            first_occurrence = cmd_input.find("(") + 1
            last_occurrence = cmd_input.find(")")
            data = cmd_input[first_occurrence : last_occurrence]
            print(create_block(block_name, parent_block, data))

        elif "backblock" and "(" and ")" in cmd_input:
            #create backblock "<blockname>" (<data>);
            if "\"" in cmd_input:
                first_occurrence = cmd_input.find("\"") + 1
                last_occurrence = cmd_input.find("\"", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            elif "\'" in cmd_input:
                first_occurrence = cmd_input.find("\'") + 1
                last_occurrence = cmd_input.find("\'", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            else:
                print("Error: Invalid syntax. Type help for help.")
                continue
            first_occurrence = cmd_input.find("(") + 1
            last_occurrence = cmd_input.find(")")
            data = cmd_input[first_occurrence : last_occurrence]
            print(create_backbone_block(block_name, data))

        elif "uniblock" and "(" and ")" in cmd_input:
            #create uniblock "<blockname>" (<data>);
            if "\"" in cmd_input:
                first_occurrence = cmd_input.find("\"") + 1
                last_occurrence = cmd_input.find("\"", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            elif "\'" in cmd_input:
                first_occurrence = cmd_input.find("\'") + 1
                last_occurrence = cmd_input.find("\'", first_occurrence)
                block_name = cmd_input[first_occurrence : last_occurrence]

            else:
                print("Error: Invalid syntax. Type help for help.")
                continue
            first_occurrence = cmd_input.find("(") + 1
            last_occurrence = cmd_input.find(")")
            data = cmd_input[first_occurrence : last_occurrence]
            print(create_unibranching_block(block_name, data))

        else:
            print("Error: Invalid syntax. Type help for help.")
            continue

    elif "use" in cmd_input:
        #use "<blockchain>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
            print(use_blockchain(blockchain_name))
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
            print(use_blockchain(blockchain_name))   
        else:
            print("Error: Invalid syntax. Type help for help.")
    
    elif "verify" and "from" in cmd_input:
        #verify "<block>" from "<parentblock>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            block_name = cmd_input[first_occurrence : last_occurrence]

        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            block_name = cmd_input[first_occurrence : last_occurrence]

        else:
            print("Error: Invalid syntax. Type help for help.")
            continue

        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"", last_occurrence + 1) + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]

        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'", last_occurrence + 1) + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]

        else:
            print("Error: Invalid syntax. Type help for help.")
            continue
        
        print(verify_block(block_name, parent_block))

    elif "verify" in cmd_input:
        #verify "<blockchain>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
        else:
            print("Error: Invalid syntax. Type help for help.")
            continue
        print(verify_blockchain(blockchain_name))
    
    elif "delete" in cmd_input:
        #delete "<blockchain>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
            print(delete_blockchain(blockchain_name))
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            blockchain_name = cmd_input[first_occurrence : last_occurrence]
            print(delete_blockchain(blockchain_name))   
        else:
            print("Error: Invalid syntax. Type help for help.")
    
    elif "show" in cmd_input:
        #show "<block>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            block_name = cmd_input[first_occurrence : last_occurrence]
            print(show_block_data(block_name))
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            block_name = cmd_input[first_occurrence : last_occurrence]
            print(show_block_data(block_name))   
        else:
            print("Error: Invalid syntax. Type help for help.")    

    elif "set" and "backblock" in cmd_input:
        #set backblock as "<parentblock>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]
            print(set_backbone_block(parent_block))
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]
            print(set_backbone_block(parent_block))   
        else:
            print("Error: Invalid syntax. Type help for help.")

    elif "set" and "uniblock" in cmd_input:
        #set uniblock as "<parentblock>";
        if "\"" in cmd_input:
            first_occurrence = cmd_input.find("\"") + 1
            last_occurrence = cmd_input.find("\"", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]
            print(set_unibranching_block(parent_block))
        elif "\'" in cmd_input:
            first_occurrence = cmd_input.find("\'") + 1
            last_occurrence = cmd_input.find("\'", first_occurrence)
            parent_block = cmd_input[first_occurrence : last_occurrence]
            print(set_unibranching_block(parent_block))   
        else:
            print("Error: Invalid syntax. Type help for help.")

    elif "help" in cmd_input:
        #help
        print("""
--------------------------------------------------------------------------------
create blockchain "<name>";
Create new Blockchains using this command.
--------------------------------------------------------------------------------
create block "<blockname>" from "<parentblock>" ("<data>");
Create new Blocks from Parentblock using this command.
NOTE: If this is the first Block in the Blockchain, use "basic" as parentblock.
--------------------------------------------------------------------------------
create backblock "<blockname>" (<data>);
Create new Blocks from the backbone using this command.
(Refer set backbone command)
--------------------------------------------------------------------------------
create uniblock "<blockname>" (<data>);
Create new Blocks from the previous parent using this command.
(Refer set unibranch command)
--------------------------------------------------------------------------------
use "<blockchain>";
Use existing blockchains using this command.
--------------------------------------------------------------------------------
verify "<blockchain>";
Verify existing blockchains using this command.
--------------------------------------------------------------------------------
verify "<block>" from "<parentblock>";
Verify specific blocks from parent block using this command.
--------------------------------------------------------------------------------
delete "<blockchain>";
Delete existing blockchains using this command.
--------------------------------------------------------------------------------
show "<block>";
Use this command to view the data in the block.
--------------------------------------------------------------------------------
set backblock as "<parentblock>";
Set a parentblock to use as universal parent.
(Used along with create backbone command)
--------------------------------------------------------------------------------
set uniblock as "<parentblock>";
Set a parentblock to branch out from.
(Used along with create unibranch command)
--------------------------------------------------------------------------------
""")

    elif "exit" in cmd_input:
        #exit
        exit = True

    else:
        print("Error: Invalid syntax. Type help for help.")

try:
    branch.close()
    root.close()
except:
    print("Couldn't close all SQL connections")


#commands
#delete_blockchain("s")
#create_blockchain("s")
#use_blockchain("s")
#create_block("t","Basic","datatta")
#create_block("t2","t","datatsta")
#print(verify_blockchain("s"))
#print(show_block_data("t2"))

'''
set_backbone_block("t2")
create_backbone_block("t2a", "smthngsmthng")
create_backbone_block("t2b", "snthgfd")
'''

'''
set_unibranching_block("t2")
create_unibranching_block("t3", "ssh")
create_unibranching_block("t4", "ssl")
'''
