mkdir -p certs/{ca,broker}
cd certs

# ca
openssl genrsa   -out ca/ca.key   2048
openssl req   -new   -x509   -days 1826   -key ca/ca.key   -out ca/ca.crt   -subj "/CN=MQTT CA"

# broker
openssl genrsa   -out broker/broker.key   2048
openssl req   -new   -out broker/broker.csr   -key broker/broker.key   -subj "/CN=broker"
openssl x509   -req   -in broker/broker.csr   -CA ca/ca.crt   -CAkey ca/ca.key   -CAcreateserial   -out broker/broker.crt   -days 360