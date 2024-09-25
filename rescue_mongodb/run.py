'''
Sử dụng cái phao cứu sinh này trong trường hợp MongoDB bị treo, do có quá nhiều command nặng trong queue đang chờ được thực hiện.
Tình huống thảm họa này tôi đã trải nghiệm ít nhất 2 lần, do tự tay bóp dái.
Cụ thể, nguyên nhân trực tiếp gây ra sự cố là khi tôi dùng robo3t đánh index cho 1 collection rất nặng (vài trăm triệu bản ghi), nhưng đã quên không tích chọn vào chạy ở background => kết quả command đánh index đó làm treo tất cả các command/query khác, trong khi các service vẫn tiếp tục đẩy thêm command/ query vào queue.
Hậu quả thì tất nhiên là toàn bộ hệ thống phụ thuộc vào MongoDB bị treo :(
Trong tình huống thảm họa đó, restart MongoDB không giải quyết được vấn đề, chỉ còn lựa chọn đó là tắt tất cả service (để không đẩy thêm command/query vào queue) và drop các command treo đi. Tuy nhiên số lượng command tồn khi đó đã rất nhiều (vài trăm), tôi đã phải xóa bằng tay từng command cho đến khi MongoDB có thể phục vụ bình thường trở lại. Rõ ràng thời gian xử lý là rất lâu, và trong lúc đó cũng vô cùng bối rối nên không kịp bình tĩnh ngồi viết script để xóa command tồn.
Đó là lí do hôm nay tôi bình tĩnh ngồi đây, viết cái life-saver này, tất có lúc dùng đến. 
'''

from pymongo import MongoClient

# client authen mongo
mongo_client = MongoClient('mongodb://localhost')

# get all operations
db = mongo_client.admin
result = db.command('currentOp')
ops = result.get('inprog', [])

op_ids = [op.get('opid') for op in ops]
print(f'Operation IDs to kill: {op_ids}')

# kill all operations
for opid in op_ids:
    db.command('killOp', op=opid)
    print(f'Killed operation ID: {opid}')
