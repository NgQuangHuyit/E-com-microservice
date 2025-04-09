# Sử dụng Python 3.9 làm base image
FROM python:3.10.12

# Đặt thư mục làm việc
WORKDIR /ecom_customer_sv

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Expose port 8000
EXPOSE 8000

ENTRYPOINT ["bash", "-c", "python3 ./manage.py runserver 0.0.0.0:8000"]

