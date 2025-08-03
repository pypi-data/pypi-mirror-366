Simple TodoList Manager

How to install : 
    pip install todo-eunho

How to Use : 

1. add :
    adds an event to the todo list

    Command : 
        todo add "Title" --date "date" --time "time"

    flag : 
        --date : "DD_MON_YYYY" 
               : "16_JUN_2001"
        --time : "HH_MM"
               : "23_00"

    todo add "Meeting with Dowan Kim" --date "30_JUL_2025" --time "10_30"

2. show : 
    shows the todo list
    
    Command : 
    todo show
    
3. clear : 
    clears the todo list

    Command
    todo clear

4. delete :
    deletes an event of specified index from the todo list 

    Command : 
    todo delete <index>

5. fix : 
    fixes an event of specified index from the todo list

    Command : 
    todo fix <index> --date "date" --time "time"

    flag :
    --date : updates original event's date
    --time : updates original event's time


6. mdel :
    deletes multiple events from the todo list

    Command :
    todo mdel <index> <index> <index>


