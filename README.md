一个使用 python 实现共享锁、排他锁、意向共享锁、意向排他锁库。

### 使用方法：
```python
from lock import Source

# 初始化一个锁资源， 非公平锁方式的实现
source = Source()
# 初始化一个锁资源，公平锁方式的实现
source = Source(True)

# 获取资源的 X 锁， 获取不到则线程被阻塞，获取到了继续往下执行
lock = source.lockX() 
# X 锁解锁
lock.unlock()

# 获取资源的 IX 锁， 获取不到则线程被阻塞，获取到了继续往下执行
lock = source.lockIX() 
# IX 锁解锁
lock.unlock()

# 获取资源的 S 锁， 获取不到则线程被阻塞，获取到了继续往下执行
lock = source.lockS() 
# S 锁解锁
lock.unlock()

# 获取资源的 IS 锁， 获取不到则线程被阻塞，获取到了继续往下执行
lock = source.lockS() 
# IS 锁解锁
lock.unlock()
```
