# stoarge.py는 실제 json 입출력 담당

import json
import logging
import threading
from pathlib import Path
from .models import TodoItem
from .utils import sort_key


STORAGE_PATH = Path(__file__).parent / "todo.json"
DEBUG_FORMAT = "[%(levelname)s] %(asctime)s : file(%(filename)s) function(%(funcName)s) lineno(%(lineno)s) \n \t %(message)s"
lock = threading.Lock()


def make_debug_logger(name = None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(DEBUG_FORMAT)
    file_handler = logging.FileHandler(filename = "storage_history.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
    
debug_logger = make_debug_logger("func_call_history")


# JSON 파일에서 TodoItem 리스트 불러오기
def load_items() -> list[TodoItem]:
    if not STORAGE_PATH.exists() or STORAGE_PATH.stat().st_size == 0:
        return []
    with open(STORAGE_PATH, "r") as f:
        data = json.load(f)
    items = [TodoItem.from_dict(d) for d in data]
    debug_logger.debug(f"Parsed {len(items)} items from storage")
    return(sorted(items, key=sort_key))


# TodoItem 리스트 전체를 JSON 파일로 저장
def save_items(items: list[TodoItem]):
    with open(STORAGE_PATH, "w") as f:
        json.dump([item.to_dict() for item in items], f, indent = 2)
    debug_logger.debug(f"Stored {len(items)} items in storage")

# 새 항목 추가 (기존 리스트에 append 후 저장)
def add_item(item: TodoItem):
    items = load_items()
    items.append(item)
    save_items(items)
    

# 인덱스에 해당하는 항목 삭제
def delete_item(index: int):
    '''
    Not used for now, but implemented for potential future use
    '''
    items = load_items()
    if 0 <= index < len(items):
        del items[index]
        save_items(items)
    else:
        raise IndexError("Invalid index")
    
# 전체 항목 삭제
def clear_items():
    '''
    Not used for now, but implemented for potential future use
    '''
    save_items([])

# 인덱스의 항목 수정
def update_item(index: int, date=None, time=None):
    '''
    Not used for now, but implemented for potential future use
    '''
    items = load_items()
    if 0 <= index < len(items):
        if date is not None:
            items[index].date = date
        if time is not None:
            items[index].time = time
        save_items(items)
    else:
        raise IndexError("Invalid index")

def mdel_threaded(indexes: list[int]):
    '''
    Not used for now, but implemented for potential future use
    '''
    items = load_items()
    deleted_titles = [None]
    
    def mark_deleted(i):
        if 0 <= i < len(items):
            with lock:
                deleted_titles[i] = items[i].title
                items[i] = None
    
    threads = []
    for idx in indexes:
        t = threading.Thread(target=mark_deleted, args=(idx,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
        
    items = [item for item in items if item is not None]
    save_items(items)
    
    for title in deleted_titles:
        if title:
            print(f"Deleted: {title}")