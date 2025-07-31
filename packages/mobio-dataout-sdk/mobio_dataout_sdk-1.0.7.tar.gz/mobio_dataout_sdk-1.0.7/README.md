##  Thư viện DATA OUT SDK dành cho các module cần out các event.


### Cài đặt:
```bash
 $ pip3 install mobio-dataout-sdk
 ```


### Sử dụng:

   ```python
    from mobio.sdks.dataout import DataOut

    DataOut().send(
        body, merchant_id, data_type, key_message
    )
    
    // body: dữ liệu json event raw của từng module, dữ liệu này chưa được chuẩn hóa theo đúng tài liệu định dạng mô t
ả event. module dataout sẽ chuẩn hóa về dữ liệu chuẩn của tài liệu 
    // merchant_id: id merchant phát sinh event
    // data_type: mã event được đặc tả trong tài liệu 
    // key_message: là key message theo đối tượng như deal_id, profile_id, ... (có thể không truyền)
#### Log - 1.0.0 
    - release sdk
#### Log - 1.0.1 
    - giam timeout request
#### Log - 1.0.2 
    - try catch send data
#### Log - 1.0.3
    - bỏ tham số key khi push tin kafka 
#### Log - 1.0.4
    - cho các module thêm tham số key khi push tin kafka
#### Log - 1.0.6
    - chuyển lấy cấu hình connector từ dataout sang market place
#### Log - 1.0.7
    - với dynamic event thì kiểm tra có connector đăng ký từng event không, nếu có thì chỉ nhận event có đăng ký 
