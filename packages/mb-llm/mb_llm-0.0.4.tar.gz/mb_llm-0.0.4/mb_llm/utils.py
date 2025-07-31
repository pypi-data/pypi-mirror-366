import torch

__all__ = ['get_gpu_properties','get_memory_allotted']

def get_gpu_properties():
    """
    Returns the properties of the GPU.
    """
    for i in range(torch.cuda.device_count()):
        print(torch.cuda.get_device_name(i))
        print(torch.cuda.get_device_capability(i))
        print(torch.cuda.get_device_properties(i))
    
def get_memory_allotted():
    """
    Returns the memory allotted to the GPU.
    To be used as wrapper for monitoring memory usage.
    """
    return torch.cuda.memory_allocated()

