docker build -t ngquanghuyit/order_sv:v1.0.1 -f ./ecom_order_sv/Dockerfile ./ecom_order_sv;

docker login - ngquanghuyit -p password ;

docker push ngquanghuyit/order_sv:v1.0.1;

kuberctl apply -f ./ecom_order_sv/deployment.yaml;