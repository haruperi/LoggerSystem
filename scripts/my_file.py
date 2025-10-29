from mylogger.utils import FrameInspector

def my_function():
    # Get the caller's frame
    frame = FrameInspector.get_caller_frame(0)
    
    # Extract detailed information
    info = FrameInspector.extract_frame_info(frame)
    
    print(f"Called from: {info['file_name']}")
    print(f"Function: {info['function']}")
    print(f"Line: {info['lineno']}")
    print(f"Module: {info['module']}")
    print(f"Code: {info['context_line']}")