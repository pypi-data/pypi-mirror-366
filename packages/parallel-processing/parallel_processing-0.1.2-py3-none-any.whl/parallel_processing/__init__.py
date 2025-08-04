from typing import List, Literal, Union, Callable, TypeVar, Generic, Tuple
from enum import Enum
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from time import time
from tqdm import tqdm

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")


T = TypeVar('T')
V = TypeVar('V')

def timing(f):
  @wraps(f)
  def wrap(*args, **kw):
    ts = time()
    result = f(*args, **kw)
    te = time()
    logging.info('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
    return result
  return wrap

class ProcessingType(Enum):
  THREAD = 'THREAD'
  PROCESS = 'PROCESS'
  SEQUENCE = 'SEQUENCE'

class ParallelProcessing:
  def __init__(self, workers: int, processing_type: ProcessingType):
    self.workers: int = workers
    self.processing_type: ProcessingType = processing_type
    self.logger = logging.getLogger(self.__class__.__name__)

  @timing
  def run(self, processor: Callable[[int, T], V], items: List[T]) -> List[V]:
    if self.processing_type == ProcessingType.THREAD:
      with ThreadPoolExecutor(max_workers=self.workers) as pool:
        return list(tqdm(pool.map(processor, [(idx, item) for idx, item in enumerate(items)]), total=len(items)))
    
    if self.processing_type == ProcessingType.PROCESS:
      with Pool(processes=self.workers) as pool:
        return list(tqdm(pool.imap(processor, [(idx, item) for idx, item in enumerate(items)]), total=len(items)))
    
    results = []
    for idx, item in tqdm(enumerate(items)):
      results.append(processor(params=(idx, item)))
    return results
  
  @staticmethod
  def thread(workers: int, processor: Callable[[int, T], V], items: List[T]) -> List[V]:
    pp = ParallelProcessing(workers=workers, processing_type=ProcessingType.THREAD)
    return pp.run(processor=processor, items=items)
  
  @staticmethod
  def process(workers: int, processor: Callable[[int, T], V], items: List[T]) -> List[V]:
    pp = ParallelProcessing(workers=workers, processing_type=ProcessingType.PROCESS)
    return pp.run(processor=processor, items=items)
  
  @staticmethod
  def sequence(processor: Callable[[int, T], V], items: List[T]) -> List[V]:
    pp = ParallelProcessing(workers=0, processing_type=ProcessingType.SEQUENCE)
    return pp.run(processor=processor, items=items)